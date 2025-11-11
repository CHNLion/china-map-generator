from flask import Flask, render_template, request, jsonify, send_file
import os
import traceback
from app.controllers.map_controller import generate_map, get_region_data
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

@app.route('/')
def index():
    """渲染首页"""
    return render_template('index.html')

@app.route('/api/generate-map', methods=['POST'])
def create_map():
    """生成地图API"""
    data = request.json
    map_type = data.get('mapType', '省')  # 默认是省级地图
    region_name = data.get('regionName', '').strip()  # 可选的区域名称筛选
    
    # 新增高亮和颜色自定义参数
    highlight_regions = data.get('highlightRegions', [])  # 多个高亮区域（包含区域名和颜色）
    # 兼容旧版单区域参数
    if not highlight_regions and data.get('highlightRegion'):
        highlight_regions = [{
            'name': data.get('highlightRegion').strip(),
            'color': data.get('highlightColor', '#FF5733')
        }]
    base_color = data.get('baseColor', '#EAEAEA')  # 底图颜色
    border_color = data.get('borderColor', 'white')  # 边界线颜色
    border_width = float(data.get('borderWidth', 0.5))  # 边界线宽度
    show_labels = data.get('showLabels', True)  # 是否显示标签
    
    # 新增标题自定义参数
    show_title = data.get('showTitle', True)  # 是否显示标题
    custom_title = data.get('customTitle', '').strip()  # 自定义标题
    title_font_size = int(data.get('titleFontSize', 15))  # 标题字体大小
    
    # 新增经纬度显示参数
    show_coordinates = data.get('showCoordinates', False)  # 是否显示经纬度
    coordinates_font_size = int(data.get('coordinatesFontSize', 8))  # 经纬度字体大小
    
    # 新增本地保存控制参数
    save_local = data.get('saveLocal', False)  # 是否保存到本地文件系统
    
    print(f"接收到地图生成请求: 类型={map_type}, 区域名称={region_name}, 高亮区域={highlight_regions}")
    if show_title and custom_title:
        print(f"自定义标题: '{custom_title}', 字体大小: {title_font_size}")
    if show_coordinates:
        print(f"显示经纬度, 字体大小: {coordinates_font_size}")
    print(f"保存方式: {'本地保存' if save_local else 'Base64编码'}")
    
    try:
        # 调用地图生成函数
        result = generate_map(
            map_type=map_type, 
            region_name=region_name,
            highlight_regions=highlight_regions,  # 传递多区域数组
            base_color=base_color,
            border_color=border_color,
            border_width=border_width,
            show_labels=show_labels,
            showTitle=show_title,
            customTitle=custom_title,
            titleFontSize=title_font_size,
            showCoordinates=show_coordinates,
            coordinatesFontSize=coordinates_font_size,
            save_local=save_local
        )
        
        response_data = {
            'success': True,
            'mapType': map_type,
            'regionName': region_name,
            'highlightRegions': highlight_regions
        }
        
        # 根据保存模式返回不同的数据
        if save_local:
            response_data['imagePath'] = result  # 返回相对路径
        else:
            response_data['imageData'] = result  # 返回Base64数据
        
        return jsonify(response_data)
    except Exception as e:
        # 获取详细的错误跟踪
        error_trace = traceback.format_exc()
        print(f"生成地图时出错: {str(e)}")
        print(f"错误详情: {error_trace}")
        
        # 返回错误信息
        return jsonify({
            'success': False,
            'error': str(e),
            'mapType': map_type,
            'regionName': region_name,
            'highlightRegions': highlight_regions
        }), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """获取区域数据（省、市、县）"""
    try:
        # 获取区域数据
        region_type = request.args.get('type', 'province')  # province, city, county
        parent_name = request.args.get('parent', '')  # 父级区域名称
        
        # 调用获取数据的函数
        regions = get_region_data(region_type, parent_name)
        
        return jsonify({
            'success': True,
            'data': regions
        })
    except Exception as e:
        # 获取详细的错误跟踪
        error_trace = traceback.format_exc()
        print(f"获取区域数据时出错: {str(e)}")
        print(f"错误详情: {error_trace}")
        
        # 返回错误信息
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/maps/<path:filename>')
def get_map_image(filename):
    """获取生成的地图图片"""
    return send_file(os.path.join('app/static/maps', filename))

if __name__ == '__main__':
    # 确保地图保存目录存在
    os.makedirs('app/static/maps', exist_ok=True)
    
    # 启动应用
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug) 