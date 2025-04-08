import os
import geopandas as gpd
# 首先设置matplotlib使用非交互式后端
import matplotlib
matplotlib.use('Agg')  # 在导入pyplot之前设置
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from datetime import datetime
import uuid
import matplotlib.font_manager as fm
from matplotlib import rcParams
import platform
from matplotlib.projections import get_projection_class
from pyproj import CRS
import pyproj

# 定义shp文件路径
SHP_FOLDER = 'shp'
MAPS_OUTPUT_FOLDER = 'app/static/maps'
FONTS_FOLDER = 'app/static/fonts'

# 确保输出目录存在
os.makedirs(MAPS_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FONTS_FOLDER, exist_ok=True)

# 全局变量，用于缓存数据
_province_data = None
_city_data = None
_county_data = None

def get_region_data(region_type='province', parent_name=None):
    """
    获取区域数据（省、市、县）
    
    参数:
        region_type (str): 区域类型，可选 'province', 'city', 'county'
        parent_name (str, optional): 父级区域名称，用于筛选
        
    返回:
        list: 区域列表
    """
    global _province_data, _city_data, _county_data
    
    # 根据不同区域类型读取对应数据
    if region_type == 'province':
        # 获取省级数据
        if _province_data is None:
            try:
                province_path = os.path.join(SHP_FOLDER, '省.shp')
                if not os.path.exists(province_path):
                    return {"error": "省级地图文件不存在"}
                
                # 读取省级地图
                df = gpd.read_file(province_path, encoding='utf-8')
                if '省' in df.columns:
                    # 提取省份名称
                    provinces = sorted(df['省'].unique().tolist())
                    # 添加全国选项
                    _province_data = [{'name': '全国', 'value': '全国'}] + [{'name': p, 'value': p} for p in provinces if p]
                else:
                    return {"error": "省级地图文件结构不正确"}
            except Exception as e:
                return {"error": f"读取省级数据出错: {str(e)}"}
        
        return _province_data
    
    elif region_type == 'city':
        # 获取市级数据
        if parent_name:
            try:
                city_path = os.path.join(SHP_FOLDER, '市.shp')
                if not os.path.exists(city_path):
                    return {"error": "市级地图文件不存在"}
                
                # 读取市级地图
                df = gpd.read_file(city_path, encoding='utf-8')
                if '市' in df.columns and '省' in df.columns:
                    # 按省份筛选
                    filtered_df = df[df['省'] == parent_name]
                    if filtered_df.empty:
                        return []
                    
                    # 提取城市名称
                    cities = sorted(filtered_df['市'].unique().tolist())
                    return [{'name': c, 'value': c} for c in cities if c]
                else:
                    return {"error": "市级地图文件结构不正确"}
            except Exception as e:
                return {"error": f"读取市级数据出错: {str(e)}"}
        else:
            # 如果没有提供省份，则返回所有市
            if _city_data is None:
                try:
                    city_path = os.path.join(SHP_FOLDER, '市.shp')
                    if not os.path.exists(city_path):
                        return {"error": "市级地图文件不存在"}
                    
                    # 读取市级地图
                    df = gpd.read_file(city_path, encoding='utf-8')
                    if '市' in df.columns:
                        # 提取城市名称
                        cities = sorted(df['市'].unique().tolist())
                        _city_data = [{'name': c, 'value': c} for c in cities if c]
                    else:
                        return {"error": "市级地图文件结构不正确"}
                except Exception as e:
                    return {"error": f"读取市级数据出错: {str(e)}"}
            
            return _city_data
    
    elif region_type == 'county':
        # 获取县级数据
        if parent_name:
            try:
                county_path = os.path.join(SHP_FOLDER, '县.shp')
                if not os.path.exists(county_path):
                    return {"error": "县级地图文件不存在"}
                
                # 读取县级地图
                df = gpd.read_file(county_path, encoding='utf-8')
                if 'NAME' in df.columns and '市' in df.columns:
                    # 按城市筛选
                    filtered_df = df[df['市'] == parent_name]
                    if filtered_df.empty:
                        return []
                    
                    # 提取县区名称
                    counties = sorted(filtered_df['NAME'].unique().tolist())
                    return [{'name': c, 'value': c} for c in counties if c]
                else:
                    return {"error": "县级地图文件结构不正确"}
            except Exception as e:
                return {"error": f"读取县级数据出错: {str(e)}"}
        else:
            return {"error": "需要提供城市名称才能获取县级数据"}
    
    else:
        return {"error": f"不支持的区域类型: {region_type}"}

# 设置中文字体
def set_chinese_font():
    """设置matplotlib中文字体为微软雅黑"""
    # 查找微软雅黑字体路径
    font_path = None
    font_found = False
    
    # 针对Windows系统
    if platform.system() == 'Windows':
        msyh_font_names = ['msyh.ttc', 'msyh.ttf', 'msyhbd.ttf', 'msyhl.ttc', 'Microsoft YaHei']
        
        # 遍历系统字体目录查找微软雅黑
        system_font_dirs = [
            'C:/Windows/Fonts',  # Windows字体目录
            os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts')
        ]
        
        # 查找字体
        for font_dir in system_font_dirs:
            if not os.path.exists(font_dir):
                continue
            for font_name in msyh_font_names:
                full_path = os.path.join(font_dir, font_name)
                if os.path.exists(full_path):
                    font_path = full_path
                    font_found = True
                    break
            if font_found:
                break
    
    # 如果找到微软雅黑字体，设置为默认字体
    if font_found and font_path:
        print(f"使用系统微软雅黑字体: {font_path}")
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        # 设置全局字体
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = [font_prop.get_name(), 'SimHei', 'Arial Unicode MS', 'sans-serif']
        rcParams['axes.unicode_minus'] = False  # 正确显示负号
    else:
        # 如果找不到微软雅黑，尝试使用其他中文字体
        print("未找到系统微软雅黑字体，使用备用字体设置")
        plt.rcParams['font.sans-serif'] = ['SimHei', 'FangSong', 'SimSun', 'KaiTi', 'Arial Unicode MS', 'sans-serif'] 
        plt.rcParams['axes.unicode_minus'] = False

def hex_to_rgb(hex_color):
    """
    将十六进制颜色代码转换为RGB元组
    
    参数:
        hex_color (str): 十六进制颜色代码，如 "#RRGGBB"
        
    返回:
        tuple: RGB元组，值范围为0-1
    """
    # 去除可能的'#'前缀
    hex_color = hex_color.lstrip('#')
    # 将十六进制转换为RGB值(0-255)
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # 返回0-1范围的RGB值
    return tuple(c/255 for c in rgb)

def generate_map(map_type='省', region_name=None, highlight_region=None, 
                 base_color="#EAEAEA", highlight_color="#FF5733", 
                 border_color="white", border_width=0.5,
                 show_labels=True, showTitle=True, customTitle='', titleFontSize=15,
                 showCoordinates=False, coordinatesFontSize=20, save_local=False):
    """
    生成地图图片，可以高亮显示特定区域
    
    参数:
        map_type (str): 地图类型，可选 '省', '市', '县'
        region_name (str, optional): 筛选指定的区域名称
        highlight_region (str, optional): 高亮显示的区域名称
        base_color (str): 底图颜色(十六进制)
        highlight_color (str): 高亮区域颜色(十六进制)
        border_color (str): 边界线颜色
        border_width (float): 边界线宽度
        show_labels (bool): 是否显示标签
        showTitle (bool): 是否显示标题
        customTitle (str): 自定义标题，为空则使用默认标题
        titleFontSize (int): 标题字体大小
        showCoordinates (bool): 是否显示经纬度坐标
        coordinatesFontSize (int): 经纬度字体大小
        save_local (bool): 是否保存到本地文件系统
        
    返回:
        str: 如果save_local=True，返回生成的图片路径；否则返回Base64编码的图片数据
    """
    # 设置中文字体
    set_chinese_font()
    
    # 检查map_type有效性
    if map_type not in ['省', '市', '县']:
        raise ValueError("地图类型必须是 '省', '市' 或 '县'")
    
    # 处理全国地图的特殊情况
    is_national_map = (region_name == '全国' or not region_name or region_name == '')
    
    # 构建shp文件路径
    shp_path = os.path.join(SHP_FOLDER, f"{map_type}.shp")
    
    # 检查文件存在
    if not os.path.exists(shp_path):
        raise FileNotFoundError(f"找不到{shp_path}文件")
    
    try:
        # 读取shp文件
        gdf = gpd.read_file(shp_path, encoding='utf-8')
    except Exception as e:
        print(f"读取shp文件时出错: {str(e)}")
        # 尝试使用不同的编码
        try:
            gdf = gpd.read_file(shp_path, encoding='gbk')
        except Exception as e2:
            print(f"尝试使用GBK编码读取文件时出错: {str(e2)}")
            try:
                gdf = gpd.read_file(shp_path, encoding='latin1')
            except Exception as e3:
                raise ValueError(f"无法读取shp文件: {str(e3)}")
    
    # 显示数据框的列名，帮助调试
    print(f"数据框列名: {gdf.columns.tolist()}")
    
    # 定义可能的名称字段列表（确保在任何执行路径上都可访问）
    possible_name_fields = ['市', '省', '县', 'NAME', 'Name', 'name', 'CNAME', 'CName', 'cname', 
                           'CNTRY_NAME', 'PROV', 'CITY', 'COUNTY']
    
    # 如果指定了区域名称，筛选数据
    filtered = False
    original_region_name = region_name  # 保存原始输入
    
    # 对全国地图的特殊处理
    if is_national_map:
        if map_type == '省':
            print("生成全国省级地图")
        elif map_type == '市':
            print("生成全国市级地图")
        else:
            print("生成全国县级地图")
            
        filtered = False  # 显示全部区域
    elif region_name and region_name.strip():
        region_name = region_name.strip()
        
        # 对于市级地图，处理特殊情况
        region_search_variants = []
        if map_type == '市':
            # 自动添加"市"后缀（如果没有）
            if not region_name.endswith('市'):
                region_search_variants.append(region_name + '市')
            # 添加原始搜索词
            region_search_variants.append(region_name)
            # 如果搜索词以"市"结尾，添加不带"市"的版本
            if region_name.endswith('市'):
                region_search_variants.append(region_name[:-1])
            
            print(f"市级地图搜索变体: {region_search_variants}")
        else:
            region_search_variants = [region_name]
        
        # 尝试找到匹配的名称字段
        for field in possible_name_fields:
            if field in gdf.columns:
                print(f"使用{field}字段进行筛选")
                
                # 尝试每个搜索变体
                for search_term in region_search_variants:
                    try:
                        # 区分大小写的精确匹配
                        exact_match = gdf[gdf[field] == search_term]
                        if not exact_match.empty:
                            gdf = exact_match
                            filtered = True
                            print(f"找到精确匹配'{search_term}'的记录: {len(gdf)}条")
                            break
                        
                        # 不区分大小写的包含匹配
                        contains_match = gdf[gdf[field].str.contains(search_term, case=False, na=False)]
                        if not contains_match.empty:
                            gdf = contains_match
                            filtered = True
                            print(f"找到包含'{search_term}'的记录: {len(gdf)}条")
                            break
                    except Exception as e:
                        print(f"使用字段{field}和搜索词'{search_term}'筛选时出错: {str(e)}")
                
                if filtered:
                    break
        
        if not filtered:
            print(f"警告: 未找到包含'{region_name}'的区域，将显示完整地图")
            
            # 对于市级地图，如果找不到匹配项，可以尝试在省级地图中查找
            if map_type == '市':
                try:
                    # 尝试读取省级地图，查找省份
                    province_path = os.path.join(SHP_FOLDER, '省.shp')
                    if os.path.exists(province_path):
                        province_gdf = gpd.read_file(province_path, encoding='utf-8')
                        # 查找省份
                        if '省' in province_gdf.columns:
                            for search_term in region_search_variants:
                                province_match = province_gdf[province_gdf['省'].str.contains(search_term, case=False, na=False)]
                                if not province_match.empty:
                                    print(f"在省级地图中找到匹配'{search_term}'的省份: {province_match['省'].iloc[0]}")
                                    # 找到对应的市
                                    if '省' in gdf.columns:
                                        province_name = province_match['省'].iloc[0]
                                        city_in_province = gdf[gdf['省'] == province_name]
                                        if not city_in_province.empty:
                                            gdf = city_in_province
                                            filtered = True
                                            print(f"显示省份'{province_name}'下的所有城市: {len(gdf)}条")
                                            break
                except Exception as e:
                    print(f"尝试在省级地图中查找时出错: {str(e)}")
    
    # 创建图形
    plt.rcParams['figure.dpi'] = 100
    plt.rcParams['savefig.dpi'] = 300
    
    # 使用Figure和Axes对象，避免使用pyplot的状态机接口
    # 调整图形尺寸比例以更好地适配中国地图 (调整为更宽的比例)
    fig = matplotlib.figure.Figure(figsize=(14, 10))
    
    # 使用标准的子图，而不使用投影（避免与GeoPandas兼容性问题）
    ax = fig.add_subplot(111)
    
    # 投影转换 - 将地理坐标转换为适合中国地图的投影系统
    try:
        # 检查并转换当前坐标系统
        if gdf.crs and ('longlat' in str(gdf.crs).lower() or 'wgs84' in str(gdf.crs).lower()):
            print(f"检测到地理坐标系统: {gdf.crs}，转换为适合中国地图的投影系统")
            original_crs = gdf.crs  # 保存原始坐标系以便后续使用
            
            # 使用ESRI:102012 Asia_Lambert_Conformal_Conic投影
            # 这是专为亚洲地区设计的等角圆锥投影，特别适合中国地图
            asia_lcc_crs = CRS.from_epsg(102012)
            # 如果上面的代码报错（某些系统可能无法直接使用EPSG:102012），使用完整的PROJ字符串
            if not asia_lcc_crs:
                asia_lcc_crs = CRS.from_proj4(
                    "+proj=lcc +lat_1=30 +lat_2=62 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 "
                    "+ellps=WGS84 +datum=WGS84 +units=m +no_defs"
                )
            gdf = gdf.to_crs(asia_lcc_crs)
            print(f"坐标系统已转换为ESRI:102012 Asia_Lambert_Conformal_Conic")
        else:
            print(f"保持原始坐标系统: {gdf.crs}")
            original_crs = gdf.crs
    except Exception as e:
        print(f"尝试转换坐标系统时出错: {str(e)}")
        # 如果直接使用ESRI:102012失败，尝试使用PROJ字符串定义
        try:
            asia_lcc_crs = CRS.from_proj4(
                "+proj=lcc +lat_1=30 +lat_2=62 +lat_0=0 +lon_0=105 +x_0=0 +y_0=0 "
                "+ellps=WGS84 +datum=WGS84 +units=m +no_defs"
            )
            gdf = gdf.to_crs(asia_lcc_crs)
            print(f"坐标系统已转换为Asia Lambert Conformal Conic(使用PROJ字符串)")
        except Exception as e2:
            print(f"使用PROJ字符串转换坐标系时出错: {str(e2)}")
            original_crs = gdf.crs
    
    # 处理高亮区域
    highlight_gdf = None
    base_gdf = gdf.copy()
    
    if highlight_region and highlight_region.strip():
        highlight_region = highlight_region.strip()
        highlight_found = False
        
        # 创建高亮区域的搜索变体
        highlight_search_variants = []
        if map_type == '市':
            if not highlight_region.endswith('市'):
                highlight_search_variants.append(highlight_region + '市')
            highlight_search_variants.append(highlight_region)
            if highlight_region.endswith('市'):
                highlight_search_variants.append(highlight_region[:-1])
        else:
            highlight_search_variants = [highlight_region]
        
        print(f"高亮区域搜索变体: {highlight_search_variants}")
        
        # 在当前地图中查找高亮区域
        for field in possible_name_fields:
            if field in gdf.columns:
                print(f"使用{field}字段查找高亮区域")
                
                for search_term in highlight_search_variants:
                    try:
                        # 精确匹配
                        exact_match = gdf[gdf[field] == search_term]
                        if not exact_match.empty:
                            highlight_gdf = exact_match
                            highlight_found = True
                            print(f"找到精确匹配'{search_term}'的高亮区域: {len(highlight_gdf)}条")
                            break
                        
                        # 包含匹配
                        contains_match = gdf[gdf[field].str.contains(search_term, case=False, na=False)]
                        if not contains_match.empty:
                            highlight_gdf = contains_match
                            highlight_found = True
                            print(f"找到包含'{search_term}'的高亮区域: {len(highlight_gdf)}条")
                            break
                    except Exception as e:
                        print(f"查找高亮区域时出错: {str(e)}")
                
                if highlight_found:
                    break
        
        # 如果在当前地图中找不到高亮区域，尝试在下一级地图中查找
        if not highlight_found and map_type == '市':
            # 尝试在县级地图中查找区县
            try:
                county_path = os.path.join(SHP_FOLDER, '县.shp')
                if os.path.exists(county_path):
                    print(f"在县级地图中查找高亮区域: {highlight_region}")
                    county_gdf = gpd.read_file(county_path, encoding='utf-8')
                    
                    # 确保县级地图有必要的字段
                    if 'NAME' in county_gdf.columns and '市' in county_gdf.columns:
                        # 首先筛选出当前市下的所有县
                        city_counties = county_gdf[county_gdf['市'] == region_name]
                        
                        if not city_counties.empty:
                            # 在当前市的县中查找匹配的县区
                            for search_term in highlight_search_variants:
                                # 精确匹配县名
                                county_match = city_counties[city_counties['NAME'] == search_term]
                                if not county_match.empty:
                                    highlight_gdf = county_match
                                    highlight_found = True
                                    print(f"在县级地图中找到匹配'{search_term}'的区县: {len(highlight_gdf)}条")
                                    break
                                
                                # 包含匹配
                                county_contains = city_counties[city_counties['NAME'].str.contains(search_term, case=False, na=False)]
                                if not county_contains.empty:
                                    highlight_gdf = county_contains
                                    highlight_found = True
                                    print(f"在县级地图中找到包含'{search_term}'的区县: {len(highlight_gdf)}条")
                                    break
            except Exception as e:
                print(f"在县级地图中查找高亮区域时出错: {str(e)}")
        
        # 同样，如果是县级地图，也尝试在对应市的县级数据中查找
        elif not highlight_found and map_type == '省':
            # 尝试在市级地图中查找
            try:
                city_path = os.path.join(SHP_FOLDER, '市.shp')
                if os.path.exists(city_path):
                    print(f"在市级地图中查找高亮区域: {highlight_region}")
                    city_gdf = gpd.read_file(city_path, encoding='utf-8')
                    
                    # 确保市级地图有必要的字段
                    if '市' in city_gdf.columns and '省' in city_gdf.columns:
                        # 首先筛选出当前省下的所有市
                        if is_national_map:
                            # 如果是全国地图，不筛选省份
                            province_cities = city_gdf
                        else:
                            province_cities = city_gdf[city_gdf['省'] == region_name]
                        
                        if not province_cities.empty:
                            # 在当前省的市中查找匹配的市
                            for search_term in highlight_search_variants:
                                # 精确匹配市名
                                city_match = province_cities[province_cities['市'] == search_term]
                                if not city_match.empty:
                                    highlight_gdf = city_match
                                    highlight_found = True
                                    print(f"在市级地图中找到匹配'{search_term}'的城市: {len(highlight_gdf)}条")
                                    break
                                
                                # 包含匹配
                                city_contains = province_cities[province_cities['市'].str.contains(search_term, case=False, na=False)]
                                if not city_contains.empty:
                                    highlight_gdf = city_contains
                                    highlight_found = True
                                    print(f"在市级地图中找到包含'{search_term}'的城市: {len(highlight_gdf)}条")
                                    break
            except Exception as e:
                print(f"在市级地图中查找高亮区域时出错: {str(e)}")
        
        if not highlight_found:
            print(f"警告: 未找到高亮区域'{highlight_region}'")
    
    # 绘制地图 - 修复坐标系问题
    if highlight_gdf is not None:
        # 区分是否是完全相同的区域
        if highlight_gdf.equals(gdf):
            print("高亮区域与选择区域相同，使用单一样式渲染")
            # 如果高亮区域和选择区域完全相同，只绘制一次
            gdf.plot(ax=ax, color=highlight_color, edgecolor=border_color, linewidth=border_width)
        else:
            # 处理跨级别高亮显示的情况（如市级地图高亮显示县级区域）
            if 'geometry' not in highlight_gdf.columns:
                print("高亮数据没有几何信息，无法绘制")
            else:
                # 确保高亮区域与主地图使用相同的坐标系统
                try:
                    # 检查高亮区域的坐标系统
                    if highlight_gdf.crs != gdf.crs:
                        print(f"高亮区域和底图坐标系不同，将高亮区域从 {highlight_gdf.crs} 转换为 {gdf.crs}")
                        highlight_gdf = highlight_gdf.to_crs(gdf.crs)
                except Exception as e:
                    print(f"转换高亮区域坐标系时出错: {str(e)}")
                
                # 绘制底图
                gdf.plot(ax=ax, color=base_color, edgecolor=border_color, linewidth=border_width)
                
                # 绘制高亮区域
                try:
                    highlight_gdf.plot(ax=ax, color=highlight_color, edgecolor=border_color, linewidth=border_width)
                    print("成功绘制高亮区域")
                except Exception as e:
                    print(f"绘制高亮区域时出错: {str(e)}")
                    # 如果高亮区域绘制失败，至少保证底图正常显示
    else:
        # 没有高亮区域，直接绘制完整地图
        gdf.plot(ax=ax, color=base_color, edgecolor=border_color, linewidth=border_width)
    
    # 设置坐标轴宽高比，修复地图比例问题
    # 对于墨卡托投影地图使用'equal'确保比例正确
    ax.set_aspect('equal', adjustable='box')
    
    # 调整边界和布局，确保地图完整显示且不变形
    fig.tight_layout(pad=2.0)
    
    # 设置适当的视图范围以避免变形（针对中国地图）
    if is_national_map:
        try:
            # 获取数据边界并稍微扩大视图范围
            bounds = gdf.total_bounds
            x_min, y_min, x_max, y_max = bounds
            # 计算中心点
            x_center = (x_min + x_max) / 2
            y_center = (y_min + y_max) / 2
            # 计算合适的宽高
            width = (x_max - x_min) * 1.1  # 扩大10%
            height = (y_max - y_min) * 1.1
            # 确保中国地图的宽高比例合适
            aspect_ratio = width / height
            if aspect_ratio < 1.4:  # 确保中国地图足够宽
                width = height * 1.5  # 使用1.5的宽高比
            
            # 设置视图范围
            x_range = (x_center - width/2, x_center + width/2)
            y_range = (y_center - height/2, y_center + height/2)
            ax.set_xlim(x_range)
            ax.set_ylim(y_range)
            print(f"设置地图视图范围: 宽={width:.2f}, 高={height:.2f}, 比例={aspect_ratio:.2f}")
            print(f"X范围: {x_range}, Y范围: {y_range}")
        except Exception as e:
            print(f"设置视图范围时出错: {str(e)}")
    
    # 添加省/市/县名称标签
    if show_labels:
        name_fields = ['NAME', 'Name', 'name', 'CNAME', 'CName', 'cname', '市', '省', '县']
        name_field_to_use = None
        for field in name_fields:
            if field in gdf.columns:
                name_field_to_use = field
                break
        
        if name_field_to_use:
            print(f"使用{name_field_to_use}字段添加标签")
            # 如果数据量大，只对部分区域添加标签
            max_labels = 100
            if len(gdf) > max_labels and not filtered:
                print(f"数据量较大({len(gdf)}条)，仅显示部分标签")
                try:
                    # 计算区域面积
                    gdf['area'] = gdf.geometry.area
                    # 按面积降序排序，取最大的区域
                    labeled_gdf = gdf.sort_values('area', ascending=False).head(max_labels)
                except Exception as e:
                    print(f"计算区域面积时出错: {str(e)}")
                    # 如果计算面积失败，简单地取前N个记录
                    labeled_gdf = gdf.head(max_labels)
            else:
                labeled_gdf = gdf
            
            for idx, row in labeled_gdf.iterrows():
                try:
                    # 获取多边形的中心点
                    centroid = row.geometry.centroid
                    # 检查中心点是否在视图范围内
                    x, y = centroid.x, centroid.y
                    x_range = ax.get_xlim()
                    y_range = ax.get_ylim()
                    
                    # 只有当中心点在绘图区域内时才添加标签
                    if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
                        label = str(row[name_field_to_use])
                        # 计算合适的字体大小 (根据区域数量调整)
                        font_size = 8 if len(labeled_gdf) > 30 else 10
                        
                        # 如果是高亮区域，使用白色文本以提高可见度
                        label_color = 'white' if highlight_gdf is not None and idx in highlight_gdf.index else 'black'
                        
                        ax.text(x, y, label, 
                                fontsize=font_size, ha='center', va='center', color=label_color)
                except Exception as e:
                    print(f"添加标签时出错: {str(e)}")
                
    # 移除坐标轴
    ax.set_axis_off()
    
    # 显示经纬度网格
    if showCoordinates:
        # 重新启用坐标轴以显示经纬度
        ax.set_axis_on()
        
        # 如果当前是投影坐标系（Asia Lambert Conformal Conic），转换回地理坐标系以显示经纬度
        if gdf.crs and ('102012' in str(gdf.crs) or '+proj=lcc' in str(gdf.crs).lower()):
            try:
                # 获取当前视图范围（等角圆锥投影坐标系）
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # 创建网格点
                x_step = (x_max - x_min) / 5
                y_step = (y_max - y_min) / 5
                
                # 创建从Asia Lambert Conformal Conic投影到WGS84的坐标转换器
                transformer = pyproj.Transformer.from_crs(gdf.crs, "EPSG:4326", always_xy=True)
                
                # 创建经度刻度
                lon_ticks = []
                lon_labels = []
                for x in np.arange(x_min, x_max + x_step, x_step):
                    # 对于每个x坐标，使用中间y值进行转换
                    y_mid = (y_min + y_max) / 2
                    lon, _ = transformer.transform(x, y_mid)
                    lon_ticks.append(x)
                    lon_labels.append(f"{lon:.2f}°E")
                
                # 创建纬度刻度
                lat_ticks = []
                lat_labels = []
                for y in np.arange(y_min, y_max + y_step, y_step):
                    # 对于每个y坐标，使用中间x值进行转换
                    x_mid = (x_min + x_max) / 2
                    _, lat = transformer.transform(x_mid, y)
                    lat_ticks.append(y)
                    lat_labels.append(f"{lat:.2f}°N")
                
                # 设置刻度和标签
                ax.set_xticks(lon_ticks)
                ax.set_xticklabels(lon_labels, fontsize=coordinatesFontSize)
                ax.set_yticks(lat_ticks)
                ax.set_yticklabels(lat_labels, fontsize=coordinatesFontSize)
                
                # 添加网格线
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # 删除经纬度标签文本
                ax.set_xlabel('')
                ax.set_ylabel('')
            except Exception as e:
                print(f"显示经纬度网格时出错: {str(e)}")
                # 如果发生错误，回退到简单刻度
                ax.set_xticks([])
                ax.set_yticks([])
        elif gdf.crs and ('lcc' in str(gdf.crs).lower()):
            try:
                # 获取当前视图范围（等角圆锥投影坐标系）
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # 创建网格点
                x_step = (x_max - x_min) / 5
                y_step = (y_max - y_min) / 5
                
                # 创建从Lambert等角圆锥投影到WGS84的坐标转换器
                transformer = pyproj.Transformer.from_crs(gdf.crs, "EPSG:4326", always_xy=True)
                
                # 创建经度刻度
                lon_ticks = []
                lon_labels = []
                for x in np.arange(x_min, x_max + x_step, x_step):
                    # 对于每个x坐标，使用中间y值进行转换
                    y_mid = (y_min + y_max) / 2
                    lon, _ = transformer.transform(x, y_mid)
                    lon_ticks.append(x)
                    lon_labels.append(f"{lon:.2f}°E")
                
                # 创建纬度刻度
                lat_ticks = []
                lat_labels = []
                for y in np.arange(y_min, y_max + y_step, y_step):
                    # 对于每个y坐标，使用中间x值进行转换
                    x_mid = (x_min + x_max) / 2
                    _, lat = transformer.transform(x_mid, y)
                    lat_ticks.append(y)
                    lat_labels.append(f"{lat:.2f}°N")
                
                # 设置刻度和标签
                ax.set_xticks(lon_ticks)
                ax.set_xticklabels(lon_labels, fontsize=coordinatesFontSize)
                ax.set_yticks(lat_ticks)
                ax.set_yticklabels(lat_labels, fontsize=coordinatesFontSize)
                
                # 添加网格线
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # 删除经纬度标签文本
                ax.set_xlabel('')
                ax.set_ylabel('')
            except Exception as e:
                print(f"显示经纬度网格时出错: {str(e)}")
                # 如果发生错误，回退到简单刻度
                ax.set_xticks([])
                ax.set_yticks([])
        elif gdf.crs and 'epsg:3857' in str(gdf.crs).lower():
            try:
                # 获取当前视图范围（投影坐标系）
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # 创建网格点
                x_step = (x_max - x_min) / 5
                y_step = (y_max - y_min) / 5
                
                # 转换为经纬度坐标
                transformer = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
                
                # 创建经度刻度
                lon_ticks = []
                lon_labels = []
                for x in np.arange(x_min, x_max + x_step, x_step):
                    lon, _ = transformer.transform(x, 0)
                    lon_ticks.append(x)
                    lon_labels.append(f"{lon:.2f}°E")
                
                # 创建纬度刻度
                lat_ticks = []
                lat_labels = []
                for y in np.arange(y_min, y_max + y_step, y_step):
                    _, lat = transformer.transform(0, y)
                    lat_ticks.append(y)
                    lat_labels.append(f"{lat:.2f}°N")
                
                # 设置刻度和标签
                ax.set_xticks(lon_ticks)
                ax.set_xticklabels(lon_labels, fontsize=coordinatesFontSize)
                ax.set_yticks(lat_ticks)
                ax.set_yticklabels(lat_labels, fontsize=coordinatesFontSize)
                
                # 添加网格线
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # 删除经纬度标签文本
                ax.set_xlabel('')
                ax.set_ylabel('')
            except Exception as e:
                print(f"显示经纬度网格时出错: {str(e)}")
                # 如果发生错误，回退到简单刻度
                ax.set_xticks([])
                ax.set_yticks([])
        else:
            # 如果已经是地理坐标系，直接添加经纬度刻度
            try:
                # 获取当前视图范围
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # 创建刻度
                lon_ticks = np.linspace(x_min, x_max, 6)
                lat_ticks = np.linspace(y_min, y_max, 6)
                
                # 设置刻度和标签
                ax.set_xticks(lon_ticks)
                ax.set_xticklabels([f"{x:.2f}°E" for x in lon_ticks], fontsize=coordinatesFontSize)
                ax.set_yticks(lat_ticks)
                ax.set_yticklabels([f"{y:.2f}°N" for y in lat_ticks], fontsize=coordinatesFontSize)
                
                # 添加网格线
                ax.grid(True, linestyle='--', alpha=0.5)
                
                # 删除经纬度标签文本
                ax.set_xlabel('')
                ax.set_ylabel('')
            except Exception as e:
                print(f"显示经纬度网格时出错: {str(e)}")
                ax.set_xticks([])
                ax.set_yticks([])
    else:
        # 不显示经纬度时完全隐藏坐标轴
        ax.set_axis_off()
    
    # 设置标题
    if showTitle:
        if customTitle and customTitle.strip():
            # 使用自定义标题
            map_title = customTitle.strip()
        else:
            # 使用默认标题逻辑
            if is_national_map:
                if map_type == '省':
                    map_title = "全国省级地图 - 中国行政区划"
                elif map_type == '市':
                    map_title = "全国市级地图 - 中国行政区划"
                else:
                    map_title = "全国县级地图 - 中国行政区划"
            else:
                map_title = f"{map_type}级地图 - 中国行政区划"
                if filtered and original_region_name:
                    map_title = f"{map_type}级地图 - {original_region_name}区域"
            
            if highlight_region:
                map_title += f" (高亮: {highlight_region})"
        
        # 设置标题及字体大小
        ax.set_title(map_title, fontsize=titleFontSize)
        print(f"设置地图标题: '{map_title}', 字体大小: {titleFontSize}")
    else:
        print("不显示地图标题")
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4().hex[:8])
    
    if is_national_map:
        if map_type == '省':
            filename = f"全国省级_{timestamp}_{unique_id}.png"
        elif map_type == '市':
            filename = f"全国市级_{timestamp}_{unique_id}.png"
        else:
            filename = f"全国县级_{timestamp}_{unique_id}.png"
    else:
        filename = f"{map_type}_{timestamp}_{unique_id}.png"
    
    # 如果有区域名和高亮区域，加入文件名
    name_parts = []
    if original_region_name and (filtered or is_national_map):
        if original_region_name == '全国':
            safe_region_name = 'China'
        else:
            safe_region_name = ''.join(e for e in original_region_name if e.isalnum())
        name_parts.append(safe_region_name)
    
    if highlight_region:
        safe_highlight_name = ''.join(e for e in highlight_region if e.isalnum())
        name_parts.append(f"hl_{safe_highlight_name}")
    
    if name_parts:
        if is_national_map:
            filename = f"全国_{'_'.join(name_parts)}_{timestamp}_{unique_id}.png"
        else:
            filename = f"{map_type}_{'_'.join(name_parts)}_{timestamp}_{unique_id}.png"
    
    # 区分是保存到本地还是直接返回Base64
    if save_local:
        # 如果需要保存到本地
        output_path = os.path.join(MAPS_OUTPUT_FOLDER, filename)
        fig.savefig(output_path, bbox_inches='tight')
        print(f"地图生成成功，保存至: {output_path}")
        # 返回相对路径
        return f"maps/{filename}"
    else:
        # 直接返回Base64编码的图片，不保存到本地
        import io
        import base64
        
        # 将图表保存到内存中的BytesIO对象
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        
        # 将图像转换为Base64编码
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        print("地图生成成功，作为Base64编码返回")
        
        # 返回Base64编码的图片数据
        return f"data:image/png;base64,{img_base64}" 