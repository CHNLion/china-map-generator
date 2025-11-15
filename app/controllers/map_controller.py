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
    """
    设置matplotlib中文字体
    优先级：
    1. 项目字体目录 (app/static/fonts/)
    2. Linux系统字体
    3. Windows系统字体
    4. 字体族名称后备方案
    """
    font_path = None
    font_found = False
    
    # 定义字体搜索列表（按优先级）
    font_search_list = []
    
    # 1. 优先搜索项目字体目录
    project_fonts_dir = FONTS_FOLDER
    if os.path.exists(project_fonts_dir):
        project_font_files = [
            'NotoSansSC-Regular.otf',
            'NotoSansSC-Regular.ttf',
            'NotoSansCJKsc-Regular.otf',
            'wqy-microhei.ttc',
            'wqy-zenhei.ttc',
        ]
        for font_file in project_font_files:
            font_search_list.append(os.path.join(project_fonts_dir, font_file))
    
    # 2. Linux系统字体路径
    if platform.system() == 'Linux':
        linux_font_paths = [
            # Noto Sans CJK SC (思源黑体)
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf',
            '/usr/local/share/fonts/NotoSansCJKsc-Regular.otf',
            # WenQuanYi (文泉驿)
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc',
            # Droid Sans Fallback
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
            '/usr/share/fonts/droid/DroidSansFallback.ttf',
            # AR PL UMing (文鼎)
            '/usr/share/fonts/truetype/arphic/uming.ttc',
        ]
        font_search_list.extend(linux_font_paths)
    
    # 3. Windows系统字体
    elif platform.system() == 'Windows':
        windows_fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:/Windows'), 'Fonts')
        windows_font_files = [
            'msyh.ttc',      # 微软雅黑
            'msyh.ttf',
            'msyhbd.ttf',
            'simhei.ttf',    # 黑体
            'simsun.ttc',    # 宋体
            'SIMHEI.TTF',
            'SIMSUN.TTC',
        ]
        for font_file in windows_font_files:
            font_search_list.append(os.path.join(windows_fonts_dir, font_file))
    
    # 4. macOS系统字体
    elif platform.system() == 'Darwin':
        macos_font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
        ]
        font_search_list.extend(macos_font_paths)
    
    # 搜索字体文件
    for font_file_path in font_search_list:
        if os.path.exists(font_file_path):
            try:
                # 尝试加载字体
                font_prop = fm.FontProperties(fname=font_file_path)
                font_name = font_prop.get_name()
                
                # 设置为默认字体
                rcParams['font.family'] = 'sans-serif'
                rcParams['font.sans-serif'] = [font_name] + rcParams['font.sans-serif']
                rcParams['axes.unicode_minus'] = False  # 正确显示负号
                
                font_path = font_file_path
                font_found = True
                print(f"✓ 成功加载中文字体: {font_file_path}")
                print(f"  字体名称: {font_name}")
                break
            except Exception as e:
                print(f"  尝试加载字体失败 {font_file_path}: {str(e)}")
                continue
    
    # 如果没有找到字体文件，使用字体族名称作为后备
    if not font_found:
        print("⚠ 未找到字体文件，使用字体族名称后备方案")
        # 按优先级设置字体族
        font_families = [
            'Noto Sans CJK SC',
            'Noto Sans SC', 
            'WenQuanYi Micro Hei',
            'WenQuanYi Zen Hei',
            'Droid Sans Fallback',
            'Microsoft YaHei',
            'SimHei',
            'SimSun',
            'Arial Unicode MS',
            'DejaVu Sans',
            'sans-serif'
        ]
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = font_families
        rcParams['axes.unicode_minus'] = False
        print(f"  使用字体族: {', '.join(font_families[:3])}")
    
    # 清除matplotlib字体缓存（有时需要）
    try:
        fm._load_fontmanager(try_read_cache=False)
    except:
        pass
    
    return font_found

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

def find_region_in_gdf(gdf, region_name, map_type, region_name_for_msg=''):
    """
    在GeoDataFrame中查找指定区域
    
    参数:
        gdf: GeoDataFrame数据
        region_name: 要查找的区域名称
        map_type: 地图类型
        region_name_for_msg: 用于筛选的父区域名称
        
    返回:
        GeoDataFrame或None: 找到的区域数据
    """
    if not region_name or not region_name.strip():
        return None
    
    region_name = region_name.strip()
    
    # 创建搜索变体
    search_variants = []
    if map_type == '市':
        if not region_name.endswith('市'):
            search_variants.append(region_name + '市')
        search_variants.append(region_name)
        if region_name.endswith('市'):
            search_variants.append(region_name[:-1])
    else:
        search_variants = [region_name]
    
    # 定义可能的名称字段
    name_fields = ['市', '省', '县', 'NAME', 'Name', 'name', 'CNAME', 'CName', 'cname']
    
    # 在当前地图中查找
    for field in name_fields:
        if field in gdf.columns:
            for search_term in search_variants:
                try:
                    # 精确匹配
                    exact_match = gdf[gdf[field] == search_term]
                    if not exact_match.empty:
                        print(f"找到精确匹配'{search_term}'的区域: {len(exact_match)}条")
                        return exact_match
                    
                    # 包含匹配
                    contains_match = gdf[gdf[field].str.contains(search_term, case=False, na=False)]
                    if not contains_match.empty:
                        print(f"找到包含'{search_term}'的区域: {len(contains_match)}条")
                        return contains_match
                except Exception as e:
                    print(f"查找区域时出错: {str(e)}")
    
    # 尝试在下一级地图中查找（市级地图查县级）
    if map_type == '市':
        try:
            county_path = os.path.join(SHP_FOLDER, '县.shp')
            if os.path.exists(county_path):
                county_gdf = gpd.read_file(county_path, encoding='utf-8')
                if 'NAME' in county_gdf.columns and '市' in county_gdf.columns and region_name_for_msg:
                    city_counties = county_gdf[county_gdf['市'] == region_name_for_msg]
                    if not city_counties.empty:
                        for search_term in search_variants:
                            county_match = city_counties[city_counties['NAME'] == search_term]
                            if not county_match.empty:
                                # 确保坐标系一致
                                if county_match.crs != gdf.crs:
                                    county_match = county_match.to_crs(gdf.crs)
                                print(f"在县级地图中找到'{search_term}'")
                                return county_match
        except Exception as e:
            print(f"在县级地图中查找时出错: {str(e)}")
    
    # 尝试在市级地图中查找（省级地图查市级）
    # 只有当指定了父区域（省份）时才查找
    elif map_type == '省' and region_name_for_msg:
        try:
            city_path = os.path.join(SHP_FOLDER, '市.shp')
            if os.path.exists(city_path):
                city_gdf = gpd.read_file(city_path, encoding='utf-8')
                if '市' in city_gdf.columns and '省' in city_gdf.columns:
                    # 只查找当前省份下的市
                    province_cities = city_gdf[city_gdf['省'] == region_name_for_msg]
                    if not province_cities.empty:
                        for search_term in search_variants:
                            city_match = province_cities[province_cities['市'] == search_term]
                            if not city_match.empty:
                                # 确保坐标系一致
                                if city_match.crs != gdf.crs:
                                    city_match = city_match.to_crs(gdf.crs)
                                print(f"在市级地图中找到'{search_term}'（属于{region_name_for_msg}）")
                                return city_match
        except Exception as e:
            print(f"在市级地图中查找时出错: {str(e)}")
    
    return None

def generate_map(map_type='省', region_name=None, highlight_regions=None, 
                 base_color="#EAEAEA", 
                 border_color="white", border_width=0.5,
                 show_labels=True, showTitle=True, customTitle='', titleFontSize=15,
                 showCoordinates=False, coordinatesFontSize=20,
                 showScaleBar=False, scaleBarStyle='default', scaleBarLocation='lower right', scaleBarFontSize=12,
                 save_local=False):
    """
    生成地图图片，可以高亮显示多个区域（每个区域可以有独立颜色）
    
    参数:
        map_type (str): 地图类型，可选 '省', '市', '县'
        region_name (str, optional): 筛选指定的区域名称
        highlight_regions (list, optional): 高亮显示的区域列表，每项包含 {'name': '区域名', 'color': '#颜色'}
        base_color (str): 底图颜色(十六进制)
        border_color (str): 边界线颜色
        border_width (float): 边界线宽度
        show_labels (bool): 是否显示标签
        showTitle (bool): 是否显示标题
        customTitle (str): 自定义标题，为空则使用默认标题
        titleFontSize (int): 标题字体大小
        showCoordinates (bool): 是否显示经纬度坐标
        coordinatesFontSize (int): 经纬度字体大小
        showScaleBar (bool): 是否显示比例尺
        scaleBarStyle (str): 比例尺样式，可选 'segmented'(分段式), 'tick_only'(刻度线式), 'double_row'(双行交替式)
        scaleBarLocation (str): 比例尺位置，可选 'lower right', 'lower left', 'upper right', 'upper left'
        scaleBarFontSize (int): 比例尺字体大小
        save_local (bool): 是否保存到本地文件系统
        
    返回:
        str: 如果save_local=True，返回生成的图片路径；否则返回Base64编码的图片数据
    """
    # 设置中文字体
    set_chinese_font()
    
    # 处理高亮区域参数（支持新旧格式）
    if highlight_regions is None:
        highlight_regions = []
    
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
    # 调整图形尺寸比例为16:9
    fig = matplotlib.figure.Figure(figsize=(16, 9))
    
    # 使用标准的子图，而不使用投影（避免与GeoPandas兼容性问题）
    ax = fig.add_subplot(111)
    
    # 投影转换 - 将地理坐标转换为适合中国地图的投影系统
    try:
        print(f"原始坐标系统: {gdf.crs}")
        original_crs = gdf.crs  # 保存原始坐标系以便后续使用
        
        # 定义Lambert正形圆锥投影（中国测绘标准）
        # 两个标准纬线覆盖中国南北跨度（海南到黑龙江）
        asia_lcc_crs = CRS.from_proj4(
            "+proj=lcc "
            "+lat_1=25 +lat_2=47 "  # 两个标准纬线（纬度跨度覆盖南北中国）
            "+lon_0=105 "            # 中心经度设在中国中部
            "+lat_0=0 "
            "+x_0=0 +y_0=0 "
            "+datum=WGS84 "
            "+units=m +no_defs"
        )
        
        # 强制转换为Lambert正形圆锥投影（确保使用平面投影）
        gdf = gdf.to_crs(asia_lcc_crs)
        print(f"[OK] 坐标系统已转换为Lambert正形圆锥投影（中国测绘标准：lat_1=25, lat_2=47）")
        print(f"[OK] 投影参数：中心经度105，标准纬线25和47")
    except Exception as e:
        print(f"尝试转换坐标系统时出错: {str(e)}")
        # 使用PROJ字符串定义Lambert正形圆锥投影
        try:
            asia_lcc_crs = CRS.from_proj4(
                "+proj=lcc "
                "+lat_1=25 +lat_2=47 "  # 两个标准纬线（纬度跨度覆盖南北中国）
                "+lon_0=105 "            # 中心经度设在中国中部
                "+lat_0=0 "
                "+x_0=0 +y_0=0 "
                "+datum=WGS84 "
                "+units=m +no_defs"
            )
            gdf = gdf.to_crs(asia_lcc_crs)
            print(f"坐标系统已转换为Lambert正形圆锥投影（中国测绘标准：lat_1=25, lat_2=47）")
        except Exception as e2:
            print(f"使用PROJ字符串转换坐标系时出错: {str(e2)}")
            original_crs = gdf.crs
    
    # 处理多个高亮区域
    highlight_gdfs_with_colors = []
    
    print(f"收到 {len(highlight_regions)} 个高亮区域")
    print(f"底图区域: {region_name if region_name else '全国'}, 地图类型: {map_type}")
    
    for hr_item in highlight_regions:
        if not isinstance(hr_item, dict):
            print(f"跳过无效的高亮区域项: {hr_item}")
            continue
        
        hr_name = hr_item.get('name', '').strip()
        hr_color = hr_item.get('color', '#FF5733')
        
        if not hr_name:
            continue
        
        print(f"查找高亮区域: {hr_name} (颜色: {hr_color})")
        
        # 使用辅助函数查找区域
        found_gdf = find_region_in_gdf(gdf, hr_name, map_type, region_name)
        
        if found_gdf is not None and not found_gdf.empty:
            # 确保坐标系一致
            if found_gdf.crs != gdf.crs:
                found_gdf = found_gdf.to_crs(gdf.crs)
            
            highlight_gdfs_with_colors.append((found_gdf, hr_color))
            print(f"[OK] 成功添加高亮区域 '{hr_name}' (颜色: {hr_color})")
        else:
            print(f"警告: 未找到高亮区域 '{hr_name}'")
    
    # 绘制地图
    # 先绘制底图
    gdf.plot(ax=ax, color=base_color, edgecolor=border_color, linewidth=border_width)
    
    # 再绘制所有高亮区域（按顺序，每个用各自的颜色）
    for highlight_gdf, highlight_color in highlight_gdfs_with_colors:
        try:
            highlight_gdf.plot(ax=ax, color=highlight_color, edgecolor=border_color, linewidth=border_width)
            print(f"成功绘制高亮区域 (颜色: {highlight_color})")
        except Exception as e:
            print(f"绘制高亮区域时出错: {str(e)}")
    
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
                        is_highlighted = any(idx in h_gdf.index for h_gdf, _ in highlight_gdfs_with_colors)
                        label_color = 'white' if is_highlighted else 'black'
                        
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
            
            if highlight_regions and len(highlight_regions) > 0:
                if len(highlight_regions) == 1:
                    map_title += f" (高亮: {highlight_regions[0]['name']})"
                else:
                    map_title += f" (高亮: {len(highlight_regions)}个区域)"
        
        # 设置标题及字体大小
        ax.set_title(map_title, fontsize=titleFontSize)
        print(f"设置地图标题: '{map_title}', 字体大小: {titleFontSize}")
    else:
        print("不显示地图标题")
    
    # 添加自定义绘制的比例尺函数
    def draw_custom_scalebar(ax, style, location, font_size):
        """绘制自定义的黑白交替分段式比例尺"""
        from matplotlib.patches import Rectangle
        from matplotlib.lines import Line2D
        
        # 获取坐标轴范围
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # 计算地图的实际宽度（米）
        map_width_m = xlim[1] - xlim[0]
        map_height_m = ylim[1] - ylim[0]
        
        # 自动选择合适的比例尺长度（千米）- 选择地图宽度的30-40%
        total_km = map_width_m / 1000
        target_scale_km = total_km * 0.35  # 比例尺占地图宽度的35%
        
        # 选择最接近的"整数"公里数
        if target_scale_km >= 1500:
            scale_km = 2000
        elif target_scale_km >= 1000:
            scale_km = 1500
        elif target_scale_km >= 750:
            scale_km = 1000
        elif target_scale_km >= 400:
            scale_km = 500
        elif target_scale_km >= 250:
            scale_km = 300
        elif target_scale_km >= 150:
            scale_km = 200
        elif target_scale_km >= 75:
            scale_km = 100
        elif target_scale_km >= 40:
            scale_km = 50
        elif target_scale_km >= 15:
            scale_km = 20
        elif target_scale_km >= 7:
            scale_km = 10
        else:
            scale_km = 5
        
        # 计算比例尺的像素长度（与实际地理距离匹配）
        scale_m = scale_km * 1000
        scale_pixel_length = scale_m  # 精确匹配实际距离
        
        # 根据位置确定比例尺的起始坐标
        margin_x = map_width_m * 0.03  # 减小边距
        margin_y = map_height_m * 0.05
        
        if 'right' in location:
            start_x = xlim[1] - margin_x - scale_pixel_length
        else:  # left
            start_x = xlim[0] + margin_x
        
        if 'lower' in location:
            start_y = ylim[0] + margin_y
        else:  # upper
            start_y = ylim[1] - margin_y - map_height_m * 0.03
        
        # 比例尺的高度
        bar_height = map_height_m * 0.018  # 增加高度
        
        # 分段数量
        num_segments = 5
        segment_length = scale_pixel_length / num_segments
        
        # 绘制黑白交替的矩形
        for i in range(num_segments):
            color = 'black' if i % 2 == 0 else 'white'
            rect = Rectangle(
                (start_x + i * segment_length, start_y),
                segment_length,
                bar_height,
                facecolor=color,
                edgecolor='black',
                linewidth=0.8,
                zorder=1000
            )
            ax.add_patch(rect)
        
        # 添加刻度标记和数字
        for i in range(num_segments + 1):
            tick_x = start_x + i * segment_length
            # 绘制刻度线
            line = Line2D(
                [tick_x, tick_x],
                [start_y, start_y - bar_height * 0.3],
                color='black',
                linewidth=0.8,
                zorder=1000
            )
            ax.add_line(line)
            
            # 添加数字标签（所有刻度都显示）
            label_text = f"{int(scale_km * i / num_segments)}"
            ax.text(
                tick_x,
                start_y - bar_height * 0.8,
                label_text,
                ha='center',
                va='top',
                fontsize=font_size,
                fontweight='normal',
                zorder=1001
            )
        
        # 添加单位标签
        ax.text(
            start_x + scale_pixel_length / 2,
            start_y + bar_height * 1.5,
            'km',
            ha='center',
            va='bottom',
            fontsize=font_size,
            fontweight='normal',
            zorder=1001
        )
        
        print(f"[OK] 已绘制自定义比例尺: {scale_km} km, {num_segments}段")
    
    def draw_tick_only_scalebar(ax, location, font_size):
        """绘制刻度线式比例尺（只有刻度和数字，无填充）"""
        from matplotlib.lines import Line2D
        
        # 获取坐标轴范围
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # 计算地图的实际宽度（米）
        map_width_m = xlim[1] - xlim[0]
        map_height_m = ylim[1] - ylim[0]
        
        # 自动选择合适的比例尺长度（千米）- 选择地图宽度的30-40%
        total_km = map_width_m / 1000
        target_scale_km = total_km * 0.35  # 比例尺占地图宽度的35%
        
        # 选择最接近的"整数"公里数
        if target_scale_km >= 1500:
            scale_km = 2000
        elif target_scale_km >= 1000:
            scale_km = 1500
        elif target_scale_km >= 750:
            scale_km = 1000
        elif target_scale_km >= 400:
            scale_km = 500
        elif target_scale_km >= 250:
            scale_km = 300
        elif target_scale_km >= 150:
            scale_km = 200
        elif target_scale_km >= 75:
            scale_km = 100
        elif target_scale_km >= 40:
            scale_km = 50
        elif target_scale_km >= 15:
            scale_km = 20
        elif target_scale_km >= 7:
            scale_km = 10
        else:
            scale_km = 5
        
        # 计算比例尺的像素长度（与实际地理距离匹配）
        scale_m = scale_km * 1000
        scale_pixel_length = scale_m  # 精确匹配实际距离
        
        # 根据位置确定比例尺的起始坐标
        margin_x = map_width_m * 0.03  # 减小边距
        margin_y = map_height_m * 0.05
        
        if 'right' in location:
            start_x = xlim[1] - margin_x - scale_pixel_length
        else:
            start_x = xlim[0] + margin_x
        
        if 'lower' in location:
            start_y = ylim[0] + margin_y
        else:
            start_y = ylim[1] - margin_y - map_height_m * 0.02
        
        # 绘制主线
        main_line = Line2D(
            [start_x, start_x + scale_pixel_length],
            [start_y, start_y],
            color='black',
            linewidth=1.2,
            zorder=1000
        )
        ax.add_line(main_line)
        
        # 分段数量
        num_segments = 4
        segment_length = scale_pixel_length / num_segments
        tick_height = map_height_m * 0.008
        
        # 绘制刻度线和数字
        for i in range(num_segments + 1):
            tick_x = start_x + i * segment_length
            # 绘制刻度线
            line = Line2D(
                [tick_x, tick_x],
                [start_y - tick_height, start_y + tick_height],
                color='black',
                linewidth=1.0,
                zorder=1000
            )
            ax.add_line(line)
            
            # 添加数字标签
            label_text = f"{int(scale_km * i / num_segments)}"
            ax.text(
                tick_x,
                start_y - tick_height * 2.5,
                label_text,
                ha='center',
                va='top',
                fontsize=font_size,
                fontweight='normal',
                zorder=1001
            )
        
        # 添加单位标签
        ax.text(
            start_x + scale_pixel_length + margin_x * 0.2,
            start_y,
            'km',
            ha='left',
            va='center',
            fontsize=font_size,
            fontweight='normal',
            zorder=1001
        )
        
        print(f"[OK] 已绘制刻度线式比例尺: {scale_km} km")
    
    def draw_double_row_scalebar(ax, location, font_size):
        """绘制双行交替式比例尺（上下两行黑白交替错位）"""
        from matplotlib.patches import Rectangle
        from matplotlib.lines import Line2D
        
        # 获取坐标轴范围
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # 计算地图的实际宽度（米）
        map_width_m = xlim[1] - xlim[0]
        map_height_m = ylim[1] - ylim[0]
        
        # 自动选择合适的比例尺长度（千米）- 选择地图宽度的30-40%
        total_km = map_width_m / 1000
        target_scale_km = total_km * 0.35  # 比例尺占地图宽度的35%
        
        # 选择最接近的"整数"公里数
        if target_scale_km >= 1500:
            scale_km = 2000
        elif target_scale_km >= 1000:
            scale_km = 1500
        elif target_scale_km >= 750:
            scale_km = 1000
        elif target_scale_km >= 400:
            scale_km = 500
        elif target_scale_km >= 250:
            scale_km = 300
        elif target_scale_km >= 150:
            scale_km = 200
        elif target_scale_km >= 75:
            scale_km = 100
        elif target_scale_km >= 40:
            scale_km = 50
        elif target_scale_km >= 15:
            scale_km = 20
        elif target_scale_km >= 7:
            scale_km = 10
        else:
            scale_km = 5
        
        # 计算比例尺的像素长度（与实际地理距离匹配）
        scale_m = scale_km * 1000
        scale_pixel_length = scale_m  # 精确匹配实际距离
        
        # 根据位置确定比例尺的起始坐标
        margin_x = map_width_m * 0.03  # 减小边距
        margin_y = map_height_m * 0.05
        
        if 'right' in location:
            start_x = xlim[1] - margin_x - scale_pixel_length
        else:
            start_x = xlim[0] + margin_x
        
        if 'lower' in location:
            start_y = ylim[0] + margin_y
        else:
            start_y = ylim[1] - margin_y - map_height_m * 0.05
        
        # 每行的高度
        row_height = map_height_m * 0.012  # 增加高度
        
        # 分段数量
        num_segments = 10
        segment_length = scale_pixel_length / num_segments
        
        # 绘制上行（第一行）
        for i in range(num_segments):
            if i % 2 == 0:
                color = 'black'
            else:
                color = 'white'
            rect = Rectangle(
                (start_x + i * segment_length, start_y + row_height),
                segment_length,
                row_height,
                facecolor=color,
                edgecolor='black',
                linewidth=0.5,
                zorder=1000
            )
            ax.add_patch(rect)
        
        # 绘制下行（第二行，颜色相反）
        for i in range(num_segments):
            if i % 2 == 0:
                color = 'white'
            else:
                color = 'black'
            rect = Rectangle(
                (start_x + i * segment_length, start_y),
                segment_length,
                row_height,
                facecolor=color,
                edgecolor='black',
                linewidth=0.5,
                zorder=1000
            )
            ax.add_patch(rect)
        
        # 添加刻度标记和数字（每隔2段标注）
        for i in range(0, num_segments + 1, 2):
            tick_x = start_x + i * segment_length
            # 绘制刻度线
            line = Line2D(
                [tick_x, tick_x],
                [start_y - row_height * 0.3, start_y],
                color='black',
                linewidth=0.8,
                zorder=1000
            )
            ax.add_line(line)
            
            # 添加数字标签
            label_text = f"{int(scale_km * i / num_segments)}"
            ax.text(
                tick_x,
                start_y - row_height * 1.2,
                label_text,
                ha='center',
                va='top',
                fontsize=font_size,
                fontweight='normal',
                zorder=1001
            )
        
        # 添加单位标签
        ax.text(
            start_x + scale_pixel_length / 2,
            start_y + row_height * 2.8,
            'km',
            ha='center',
            va='bottom',
            fontsize=font_size,
            fontweight='normal',
            zorder=1001
        )
        
        print(f"[OK] 已绘制双行交替式比例尺: {scale_km} km")
    
    # 添加比例尺
    if showScaleBar:
        # 使用自定义绘制的专业比例尺样式
        try:
            if scaleBarStyle == 'tick_only':
                draw_tick_only_scalebar(ax, scaleBarLocation, scaleBarFontSize)
            elif scaleBarStyle == 'double_row':
                draw_double_row_scalebar(ax, scaleBarLocation, scaleBarFontSize)
            else:  # 默认使用分段式
                draw_custom_scalebar(ax, scaleBarStyle, scaleBarLocation, scaleBarFontSize)
        except Exception as e:
            print(f"绘制比例尺时出错: {str(e)}")
    
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
    
    if highlight_regions and len(highlight_regions) > 0:
        if len(highlight_regions) == 1:
            safe_highlight_name = ''.join(e for e in highlight_regions[0]['name'] if e.isalnum())
            name_parts.append(f"hl_{safe_highlight_name}")
        else:
            name_parts.append(f"hl_{len(highlight_regions)}regions")
    
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