// 在文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素 - 主要区域选择
    const generateBtn = document.getElementById('generateBtn');
    const mapType = document.getElementById('mapType');
    const mapTypeRadios = document.querySelectorAll('input[name="mapTypeRadio"]');
    const provinceSelectContainer = document.getElementById('provinceSelectContainer');
    const citySelectContainer = document.getElementById('citySelectContainer');
    const countySelectContainer = document.getElementById('countySelectContainer');
    const provinceSelect = document.getElementById('provinceSelect');
    const citySelect = document.getElementById('citySelect');
    const countySelect = document.getElementById('countySelect');
    
    // 获取DOM元素 - 高亮区域选择
    const enableHighlight = document.getElementById('enableHighlight');
    const highlightOptions = document.getElementById('highlightOptions');
    // 旧的高亮选择器已移除，创建兼容对象避免错误
    const highlightProvinceSelect = document.getElementById('highlightProvinceSelect') || { 
        value: '', disabled: false, options: [], selectedIndex: 0, 
        addEventListener: function() {}, dispatchEvent: function() {}, innerHTML: '' 
    };
    const highlightCitySelect = document.getElementById('highlightCitySelect') || { 
        value: '', disabled: true, options: [], selectedIndex: 0, 
        addEventListener: function() {}, innerHTML: '' 
    };
    const highlightCountySelect = document.getElementById('highlightCountySelect') || { 
        value: '', disabled: true, options: [], selectedIndex: 0, 
        addEventListener: function() {}, innerHTML: '' 
    };
    
    // 获取DOM元素 - 颜色设置
    const baseColor = document.getElementById('baseColor');
    const highlightColor = document.getElementById('highlightColor');
    const borderColor = document.getElementById('borderColor');
    const borderWidth = document.getElementById('borderWidth');
    const borderWidthInput = document.getElementById('borderWidthInput');
    const showLabels = document.getElementById('showLabels');
    const showCoordinates = document.getElementById('showCoordinates');
    const coordinatesFontSize = document.getElementById('coordinatesFontSize');
    const coordinatesFontSizeInput = document.getElementById('coordinatesFontSizeInput');
    const coordinatesFontSizeContainer = document.getElementById('coordinatesFontSizeContainer');
    
    // 获取DOM元素 - 自定义标题
    const enableCustomTitle = document.getElementById('enableCustomTitle');
    const titleOptions = document.getElementById('titleOptions');
    const customTitle = document.getElementById('customTitle');
    const titleFontSize = document.getElementById('titleFontSize');
    
    // 获取DOM元素 - 比例尺
    const showScaleBar = document.getElementById('showScaleBar');
    const scaleBarOptions = document.getElementById('scaleBarOptions');
    const scaleBarStyle = document.getElementById('scaleBarStyle');
    const scaleBarLocation = document.getElementById('scaleBarLocation');
    const scaleBarFontSize = document.getElementById('scaleBarFontSize');
    
    // 设置默认值
    highlightColor.value = '#7ED2F7'; // 设置高亮颜色默认值为 rgb(126,210,247)
    borderWidth.value = 1.5; // 设置边界线宽度默认值为1.5
    borderWidthInput.value = 1.5;
    coordinatesFontSize.value = 20; // 设置经纬度字体大小默认值为20
    coordinatesFontSizeInput.value = 20;
    
    // 获取DOM元素 - 结果显示
    const loadingIndicator = document.getElementById('loadingIndicator');
    const mapResult = document.getElementById('mapResult');
    const mapImage = document.getElementById('mapImage');
    const downloadLink = document.getElementById('downloadLink');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    // 加载省份数据
    loadProvinces();
    // loadHighlightProvinces(); // 已由multi-highlight.js处理
    
    // 添加自定义标题切换事件
    enableCustomTitle.addEventListener('change', function() {
        if (this.checked) {
            titleOptions.style.display = 'block';
            
            // 自动生成默认标题
            if (!customTitle.value.trim()) {
                generateDefaultTitle();
            }
        } else {
            titleOptions.style.display = 'none';
        }
    });
    
    // 添加比例尺切换事件
    showScaleBar.addEventListener('change', function() {
        if (this.checked) {
            scaleBarOptions.style.display = 'block';
        } else {
            scaleBarOptions.style.display = 'none';
        }
    });
    
    // 添加高亮切换事件
    enableHighlight.addEventListener('change', function() {
        if (this.checked) {
            highlightOptions.style.display = 'block';
            
            // 获取当前地图类型和选择的区域，自动同步高亮区域
            const currentMapType = getCurrentMapType();
            
            // 只有当底图选择了内容时才同步高亮区域
            // 同步省份选择
            if (provinceSelect.value) {
                const selectedProvince = provinceSelect.value;
                
                // 在高亮省份下拉列表中选择相同的省份
                let provinceFound = false;
                for (let i = 0; i < highlightProvinceSelect.options.length; i++) {
                    if (highlightProvinceSelect.options[i].value === selectedProvince) {
                        highlightProvinceSelect.selectedIndex = i;
                        provinceFound = true;
                        
                        // 若为省级地图，则禁用高亮省份选择
                        if (currentMapType === '省') {
                            highlightProvinceSelect.disabled = true;
                        }
                        break;
                    }
                }
                
                if (provinceFound) {
                    console.log("同步高亮省份成功: " + selectedProvince);
                    
                    // 加载高亮城市，传入回调函数处理城市和县区同步
                    loadHighlightCities(selectedProvince, function() {
                        console.log("高亮省份对应的城市加载完成");
                        
                        // 同步城市选择
                        if (citySelect.value) {
                            const selectedCity = citySelect.value;
                            console.log("尝试同步高亮城市: " + selectedCity);
                            
                            // 直接使用辅助函数同步城市选择
                            selectHighlightCity(selectedCity, currentMapType);
                            
                            // 同步县区选择 (在selectHighlightCity中已经触发了城市变更事件，
                            // 会加载县区数据，此处使用定时器确保县区数据已加载)
                            if (countySelect.value) {
                                const selectedCounty = countySelect.value;
                                // 等待县区数据加载完成后同步选择
                                setTimeout(() => {
                                    console.log("尝试同步高亮县区: " + selectedCounty);
                                    if (highlightCountySelect.options.length > 1) {
                                        let countyFound = false;
                                        for (let i = 0; i < highlightCountySelect.options.length; i++) {
                                            if (highlightCountySelect.options[i].value === selectedCounty) {
                                                highlightCountySelect.selectedIndex = i;
                                                countyFound = true;
                                                console.log("同步高亮县区成功: " + selectedCounty);
                                                break;
                                            }
                                        }
                                        if (!countyFound) {
                                            console.log("未找到匹配的高亮县区: " + selectedCounty);
                                        }
                                    } else {
                                        console.log("高亮县区数据尚未加载或无数据");
                                    }
                                }, 500);
                            }
                        }
                    });
                } else {
                    console.log("未找到匹配的高亮省份: " + selectedProvince);
                }
            }
        } else {
            highlightOptions.style.display = 'none';
        }
        
        // 切换高亮状态后，更新图片标题
        if (enableCustomTitle.checked) {
            generateDefaultTitle();
        }
    });
    
    // 边界线宽度滑块事件
    borderWidth.addEventListener('input', function() {
        const value = parseFloat(this.value).toFixed(1);
        borderWidthInput.value = value;
    });
    
    // 边界线宽度输入框事件
    borderWidthInput.addEventListener('input', function() {
        let value = parseFloat(this.value);
        if (isNaN(value)) {
            value = 0.5;
        } else if (value < 0.1) {
            value = 0.1;
        } else if (value > 3.0) {
            value = 3.0;
        }
        value = Math.round(value * 10) / 10; // 保留一位小数
        this.value = value;
        borderWidth.value = value;
    });
    
    // 经纬度字号滑块事件
    coordinatesFontSize.addEventListener('input', function() {
        const value = parseInt(this.value);
        coordinatesFontSizeInput.value = value;
    });
    
    // 经纬度字号输入框事件
    coordinatesFontSizeInput.addEventListener('input', function() {
        let value = parseInt(this.value);
        if (isNaN(value)) {
            value = 20;
        } else if (value < 10) {
            value = 10;
        } else if (value > 30) {
            value = 30;
        }
        this.value = value;
        coordinatesFontSize.value = value;
    });
    
    // 显示经纬度选项事件
    showCoordinates.addEventListener('change', function() {
        if (this.checked) {
            coordinatesFontSizeContainer.style.display = 'flex';
        } else {
            coordinatesFontSizeContainer.style.display = 'none';
        }
    });
    
    // 添加地图类型变更事件
    mapTypeRadios.forEach(function(radio) {
        radio.addEventListener('change', function() {
            if (this.checked) {
                // 更新隐藏的mapType值
                const selectedValue = this.value;
                mapType.value = selectedValue === 'national' ? '省' : selectedValue;
                
                // 更新UI显示
                updateUIByMapType(selectedValue);
                
                // 重置高亮区域禁用状态
                highlightProvinceSelect.disabled = false;
                highlightCitySelect.disabled = true;
                highlightCountySelect.disabled = true;
                
                // 如果开启了高亮，同步选择
                if (enableHighlight.checked) {
                    // 获取当前地图类型
                    const currentMapType = getCurrentMapType();
                    
                    // 同步省份选择
                    if (provinceSelect.value && currentMapType === '省') {
                        const selectedProvince = provinceSelect.value;
                        for (let i = 0; i < highlightProvinceSelect.options.length; i++) {
                            if (highlightProvinceSelect.options[i].value === selectedProvince) {
                                highlightProvinceSelect.selectedIndex = i;
                                highlightProvinceSelect.disabled = true;
                                break;
                            }
                        }
                    }
                }
            }
        });
    });
    
    // 添加省份选择事件
    provinceSelect.addEventListener('change', function() {
        const selectedProvince = provinceSelect.value;
        if (selectedProvince) {
            citySelect.innerHTML = '<option value="">请选择城市</option>';
            countySelect.innerHTML = '<option value="">请先选择城市</option>';
            
            // 获取当前地图类型
            const currentMapType = getCurrentMapType();
            
            // 只有在市级或县级地图时才加载城市
            if (currentMapType === '市' || currentMapType === '县') {
                loadCities(selectedProvince);
            }
            
            // 只有在底图省份有选择且高亮功能已启用时才联动高亮区域
            if (enableHighlight.checked && !enableHighlight.disabled) {
                // 在高亮省份下拉列表中选择相同的省份
                if (highlightProvinceSelect.options.length > 0) {
                    for (let i = 0; i < highlightProvinceSelect.options.length; i++) {
                        if (highlightProvinceSelect.options[i].value === selectedProvince) {
                            highlightProvinceSelect.selectedIndex = i;
                            // 触发change事件，加载对应的城市
                            highlightProvinceSelect.dispatchEvent(new Event('change'));
                            break;
                        }
                    }
                    
                    // 在省级地图模式下，高亮省份不可更改
                    if (currentMapType === '省') {
                        highlightProvinceSelect.disabled = true;
                    } else {
                        highlightProvinceSelect.disabled = false;
                    }
                }
            }
            
            // 自动更新图片标题
            if (enableCustomTitle.checked) {
                generateDefaultTitle();
            }
        }
    });
    
    // 添加城市选择事件
    citySelect.addEventListener('change', function() {
        const selectedCity = citySelect.value;
        if (selectedCity) {
            countySelect.innerHTML = '<option value="">请选择县区</option>';
            
            // 获取当前地图类型
            const currentMapType = getCurrentMapType();
            
            // 只有在县级地图时才加载县区
            if (currentMapType === '县') {
                loadCounties(selectedCity);
            }
            
            // 同步高亮区域的城市选择（如果启用了高亮显示）
            if (enableHighlight.checked && !enableHighlight.disabled) {
                // 先确保高亮区域的省份与底图选择的省份一致
                const selectedProvince = provinceSelect.value;
                if (selectedProvince && highlightProvinceSelect.value !== selectedProvince) {
                    // 先同步高亮省份
                    for (let i = 0; i < highlightProvinceSelect.options.length; i++) {
                        if (highlightProvinceSelect.options[i].value === selectedProvince) {
                            highlightProvinceSelect.selectedIndex = i;
                            break;
                        }
                    }
                    
                    // 先加载高亮省份对应的城市
                    loadHighlightCities(selectedProvince, function() {
                        // 加载完成后，再同步城市选择
                        syncHighlightCity(selectedCity, currentMapType);
                    });
                } else {
                    // 如果高亮区域的省份已经与底图选择的省份一致，直接同步城市
                    syncHighlightCity(selectedCity, currentMapType);
                }
            }
            
            // 自动更新图片标题
            if (enableCustomTitle.checked) {
                generateDefaultTitle();
            }
        }
    });
    
    // 同步高亮城市的辅助函数
    function syncHighlightCity(selectedCity, currentMapType) {
        // 检查高亮城市下拉列表是否有选项
        if (highlightCitySelect.options.length <= 1) {
            // 如果没有选项(只有默认选项)，可能是因为还没有加载城市数据
            // 这种情况下，直接加载城市数据
            const selectedProvince = highlightProvinceSelect.value;
            if (selectedProvince) {
                loadHighlightCities(selectedProvince, function() {
                    selectHighlightCity(selectedCity, currentMapType);
                });
            }
        } else {
            // 高亮城市下拉列表已有选项，直接选择
            selectHighlightCity(selectedCity, currentMapType);
        }
    }
    
    // 选择高亮城市的辅助函数
    function selectHighlightCity(selectedCity, currentMapType) {
        console.log("执行selectHighlightCity函数，当前高亮城市选项数量: " + highlightCitySelect.options.length);
        
        // 标记是否找到匹配的城市
        let found = false;
        
        // 只有当有选项时才进行处理
        if (highlightCitySelect.options.length > 1) {
            for (let i = 0; i < highlightCitySelect.options.length; i++) {
                if (highlightCitySelect.options[i].value === selectedCity) {
                    highlightCitySelect.selectedIndex = i;
                    found = true;
                    console.log("找到并选择了匹配的高亮城市: " + selectedCity);
                    
                    // 在市级地图模式下，高亮城市不可更改
                    if (currentMapType === '市') {
                        highlightCitySelect.disabled = true;
                    } else {
                        highlightCitySelect.disabled = false;
                    }
                    
                    // 触发change事件，加载对应的县区
                    highlightCitySelect.dispatchEvent(new Event('change'));
                    break;
                }
            }
        }
        
        if (!found) {
            if (highlightCitySelect.options.length > 1) {
                console.log(`未找到匹配城市"${selectedCity}"，使用高亮城市下拉列表中的第一个选项`);
                // 如果找不到匹配的城市，可以选择高亮城市下拉列表中的第一个有效选项
                highlightCitySelect.selectedIndex = 1; // 跳过第一个空选项
                highlightCitySelect.dispatchEvent(new Event('change'));
            } else {
                console.log("高亮城市下拉列表为空或只有默认选项，无法选择城市");
            }
        }
        
        return found;
    }
    
    // 添加县区选择事件
    countySelect.addEventListener('change', function() {
        const selectedCounty = countySelect.value;
        if (selectedCounty && enableHighlight.checked && !enableHighlight.disabled) {
            // 同步高亮区域的县区选择
            if (highlightCountySelect.options.length > 0) {
                for (let i = 0; i < highlightCountySelect.options.length; i++) {
                    if (highlightCountySelect.options[i].value === selectedCounty) {
                        highlightCountySelect.selectedIndex = i;
                        break;
                    }
                }
            }
        }
        
        // 自动更新图片标题
        if (enableCustomTitle.checked) {
            generateDefaultTitle();
        }
    });
    
    // 添加高亮省份选择事件
    highlightProvinceSelect.addEventListener('change', function() {
        const selectedProvince = highlightProvinceSelect.value;
        if (selectedProvince) {
            // 加载高亮城市数据，不需要回调函数
            loadHighlightCities(selectedProvince, null);
            highlightCountySelect.disabled = true;
            highlightCountySelect.innerHTML = '<option value="">请先选择城市</option>';
            
            // 自动更新图片标题（如果启用了高亮显示）
            if (enableHighlight.checked && enableCustomTitle.checked) {
                generateDefaultTitle();
            }
        } else {
            highlightCitySelect.disabled = true;
            highlightCitySelect.innerHTML = '<option value="">请先选择省份</option>';
            highlightCountySelect.disabled = true;
            highlightCountySelect.innerHTML = '<option value="">请先选择城市</option>';
        }
    });
    
    // 添加高亮城市选择事件
    highlightCitySelect.addEventListener('change', function() {
        const selectedCity = highlightCitySelect.value;
        if (selectedCity) {
            loadHighlightCounties(selectedCity);
            highlightCountySelect.disabled = false;
            
            // 自动更新图片标题（如果启用了高亮显示）
            if (enableHighlight.checked && enableCustomTitle.checked) {
                generateDefaultTitle();
            }
        } else {
            highlightCountySelect.disabled = true;
            highlightCountySelect.innerHTML = '<option value="">请先选择城市</option>';
        }
    });
    
    // 添加高亮县区选择事件
    highlightCountySelect.addEventListener('change', function() {
        // 自动更新图片标题（如果启用了高亮显示）
        if (enableHighlight.checked && enableCustomTitle.checked) {
            generateDefaultTitle();
        }
    });
    
    // 添加生成按钮点击事件
    generateBtn.addEventListener('click', function() {
        console.log('=== 生成按钮被点击 ===');
        generateMap();
    });
    
    // 获取当前选择的地图类型
    function getCurrentMapType() {
        let selectedType = '';
        mapTypeRadios.forEach(function(radio) {
            if (radio.checked) {
                selectedType = radio.value;
            }
        });
        return selectedType === 'national' ? '省' : selectedType;
    }
    
    // 根据地图类型更新UI
    function updateUIByMapType(mapType) {
        // 重置并隐藏所有选择器
        provinceSelectContainer.style.display = 'none';
        citySelectContainer.style.display = 'none';
        countySelectContainer.style.display = 'none';
        
        if (mapType === 'national') {
            // 全国地图不需要选择区域
        } else if (mapType === '省') {
            // 省级地图，需要选择省份
            provinceSelectContainer.style.display = 'block';
        } else if (mapType === '市') {
            // 市级地图，需要选择省份和城市
            provinceSelectContainer.style.display = 'block';
            citySelectContainer.style.display = 'block';
        } else if (mapType === '县') {
            // 县级地图，需要选择省份、城市和县区
            provinceSelectContainer.style.display = 'block';
            citySelectContainer.style.display = 'block';
            countySelectContainer.style.display = 'block';
        }
    }
    
    // 加载省份数据
    function loadProvinces() {
        showLoading(true);
        
        fetch('/api/regions?type=province')
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    provinceSelect.innerHTML = '<option value="">请选择省份</option>';
                    
                    // 添加选项，排除"全国"选项
                    data.data.forEach(province => {
                        if (province.value !== '全国') {
                            const option = document.createElement('option');
                            option.value = province.value;
                            option.textContent = province.name;
                            provinceSelect.appendChild(option);
                        }
                    });
                } else {
                    showError(data.error || '加载省份数据失败');
                }
            })
            .catch(error => {
                showLoading(false);
                showError('网络错误或服务器无响应');
                console.error('Error:', error);
            });
    }
    
    // 加载高亮省份数据
    function loadHighlightProvinces() {
        fetch('/api/regions?type=province')
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    highlightProvinceSelect.innerHTML = '<option value="">请选择省份</option>';
                    
                    // 添加选项，排除"全国"选项
                    data.data.forEach(province => {
                        if (province.value !== '全国') {
                            const option = document.createElement('option');
                            option.value = province.value;
                            option.textContent = province.name;
                            highlightProvinceSelect.appendChild(option);
                        }
                    });
                } else {
                    console.error('加载高亮省份数据失败:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
    // 加载城市数据
    function loadCities(province) {
        showLoading(true);
        
        fetch(`/api/regions?type=city&parent=${encodeURIComponent(province)}`)
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    citySelect.innerHTML = '<option value="">请选择城市</option>';
                    
                    // 添加选项
                    data.data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.value;
                        option.textContent = city.name;
                        citySelect.appendChild(option);
                    });
                } else {
                    showError(data.error || '加载城市数据失败');
                }
            })
            .catch(error => {
                showLoading(false);
                showError('网络错误或服务器无响应');
                console.error('Error:', error);
            });
    }
    
    // 加载高亮城市数据
    function loadHighlightCities(province, callback) {
        fetch(`/api/regions?type=city&parent=${encodeURIComponent(province)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    highlightCitySelect.innerHTML = '<option value="">请选择城市</option>';
                    
                    // 添加选项
                    data.data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.value;
                        option.textContent = city.name;
                        highlightCitySelect.appendChild(option);
                    });
                    
                    // 启用高亮城市选择器
                    highlightCitySelect.disabled = false;
                    
                    // 如果有回调函数，执行回调
                    if (typeof callback === 'function') {
                        callback();
                    }
                } else {
                    console.error('加载高亮城市数据失败:', data.error);
                    highlightCitySelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                highlightCitySelect.disabled = true;
            });
    }
    
    // 加载县区数据
    function loadCounties(city) {
        showLoading(true);
        
        fetch(`/api/regions?type=county&parent=${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    countySelect.innerHTML = '<option value="">请选择县区</option>';
                    
                    // 添加选项
                    data.data.forEach(county => {
                        const option = document.createElement('option');
                        option.value = county.value;
                        option.textContent = county.name;
                        countySelect.appendChild(option);
                    });
                } else {
                    showError(data.error || '加载县区数据失败');
                }
            })
            .catch(error => {
                showLoading(false);
                showError('网络错误或服务器无响应');
                console.error('Error:', error);
            });
    }
    
    // 加载高亮县区数据
    function loadHighlightCounties(city) {
        fetch(`/api/regions?type=county&parent=${encodeURIComponent(city)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.data)) {
                    // 清空现有选项
                    highlightCountySelect.innerHTML = '<option value="">请选择县区</option>';
                    
                    // 添加选项
                    data.data.forEach(county => {
                        const option = document.createElement('option');
                        option.value = county.value;
                        option.textContent = county.name;
                        highlightCountySelect.appendChild(option);
                    });
                } else {
                    console.error('加载高亮县区数据失败:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
    
    // 获取高亮区域名称
    function getHighlightRegionName() {
        if (!enableHighlight.checked || enableHighlight.disabled) {
            return '';
        }
        
        // 始终使用最低级别的选择作为高亮区域
        // 例如：如果选择了县级，优先使用县级作为高亮
        if (highlightCountySelect.value) {
            return highlightCountySelect.value;
        } else if (highlightCitySelect.value) {
            return highlightCitySelect.value;
        } else if (highlightProvinceSelect.value) {
            return highlightProvinceSelect.value;
        }
        
        return '';
    }
    
    // 获取颜色设置
    function getColorSettings() {
        return {
            baseColor: baseColor.value,
            highlightColor: highlightColor.value,
            borderColor: borderColor.value,
            borderWidth: parseFloat(borderWidth.value),
            showLabels: showLabels.checked,
            showCoordinates: showCoordinates.checked,
            coordinatesFontSize: parseInt(coordinatesFontSize.value)
        };
    }
    
    // 获取标题设置
    function getTitleSettings() {
        // 检查是否启用标题显示
        if (enableCustomTitle.checked) {
            // 如果没有输入自定义标题，自动生成默认标题
            let titleText = customTitle.value.trim();
            if (!titleText) {
                titleText = generateDefaultTitle();
            }
            
            return {
                showTitle: true,
                customTitle: titleText,
                titleFontSize: parseInt(titleFontSize.value)
            };
        } else {
            // 标题功能未启用
            return {
                showTitle: false,
                customTitle: '',
                titleFontSize: parseInt(titleFontSize.value)
            };
        }
    }
    
    // 检查是否为全国地图
    function isNational() {
        let isNationalMap = false;
        mapTypeRadios.forEach(function(radio) {
            if (radio.checked && radio.value === 'national') {
                isNationalMap = true;
            }
        });
        return isNationalMap;
    }
    
    // 获取当前选择的区域名称
    function getSelectedRegionName() {
        const mapTypeValue = getCurrentMapType();
        
        // 按照级联选择的最后一级来确定区域
        if (mapTypeValue === '省') {
            if (isNational()) {
                return '全国';
            } else {
                return provinceSelect.value || '全国';
            }
        } else if (mapTypeValue === '市') {
            if (citySelect.value) {
                return citySelect.value;
            } else if (provinceSelect.value) {
                return provinceSelect.value;
            } else {
                return '全国';
            }
        } else if (mapTypeValue === '县') {
            if (countySelect.value) {
                return countySelect.value;
            } else if (citySelect.value) {
                return citySelect.value;
            } else if (provinceSelect.value) {
                return provinceSelect.value;
            } else {
                return '全国';
            }
        }
        
        return '全国';
    }
    
    // 生成地图并显示
    function generateMap() {
        console.log('=== generateMap函数被调用 ===');
        
        // 获取选择的地图类型
        const mapTypeValue = getSelectedMapType();
        console.log('地图类型:', mapTypeValue);
        
        // 获取区域名称
        const regionName = getSelectedRegionName();
        console.log('区域名称:', regionName);
        
        // 获取多个高亮区域（从multi-highlight.js）
        const highlightRegions = typeof window.getAllHighlightRegions === 'function' 
            ? window.getAllHighlightRegions() 
            : [];
        console.log('高亮区域:', highlightRegions);
        
        // 获取颜色设置
        const colorSettings = getColorSettings();
        console.log('颜色设置:', colorSettings);
        
        // 获取标题设置
        const titleSettings = getTitleSettings();
        console.log('标题设置:', titleSettings);
        
        // 准备请求数据
        const requestData = {
            mapType: mapTypeValue === 'national' ? '省' : mapTypeValue,
            regionName: regionName,
            highlightRegions: highlightRegions,  // 新的多区域参数
            baseColor: colorSettings.baseColor,
            borderColor: colorSettings.borderColor,
            borderWidth: colorSettings.borderWidth,
            showLabels: colorSettings.showLabels,
            showCoordinates: colorSettings.showCoordinates,
            coordinatesFontSize: colorSettings.coordinatesFontSize,
            showTitle: titleSettings.showTitle,
            customTitle: titleSettings.customTitle,
            titleFontSize: titleSettings.titleFontSize,
            showScaleBar: showScaleBar.checked,
            scaleBarStyle: scaleBarStyle.value,
            scaleBarLocation: scaleBarLocation.value,
            scaleBarFontSize: parseInt(scaleBarFontSize.value),
            saveLocal: false  // 不保存到本地，使用Base64传输
        };
        
        console.log('请求数据:', requestData);
        
        // 显示加载指示器
        showLoadingIndicator();
        
        // 发送API请求
        fetch('/api/generate-map', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            // 如果不是200，先读取文本看看是什么错误
            if (!response.ok) {
                return response.text().then(text => {
                    console.error('Error response text:', text);
                    throw new Error(`HTTP ${response.status}: ${text.substring(0, 200)}`);
                });
            }
            
            return response.json();
        })
        .then(data => {
            hideLoadingIndicator();
            
            if (data.success) {
                // 显示生成的地图
                const mapResult = document.getElementById('mapResult');
                const mapImage = document.getElementById('mapImage');
                const downloadLink = document.getElementById('downloadLink');
                
                mapResult.classList.remove('d-none');
                
                // 根据返回数据类型处理图片显示
                if (data.imagePath) {
                    // 如果是本地保存的图片路径
                    mapImage.src = data.imagePath;
                    downloadLink.href = data.imagePath;
                    downloadLink.download = data.imagePath.split('/').pop();
                } else if (data.imageData) {
                    // 如果是Base64编码的图片数据
                    mapImage.src = data.imageData;
                    downloadLink.href = data.imageData;
                    
                    // 为下载链接设置文件名
                    let fileName = `地图_${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
                    if (data.regionName) {
                        fileName = `${data.regionName}_${fileName}`;
                    }
                    downloadLink.download = fileName;
                }
                
                // 滚动到地图显示区域
                mapResult.scrollIntoView({ behavior: 'smooth' });
            } else {
                // 显示错误消息
                showError(data.error || '生成地图时出错，请检查输入参数');
            }
        })
        .catch(error => {
            hideLoadingIndicator();
            showError('网络请求出错: ' + error.message);
        });
    }
    
    // 显示加载指示器
    function showLoading(show) {
        if (show) {
            loadingIndicator.classList.remove('d-none');
        } else {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    // 显示错误信息
    function showError(message) {
        showLoading(false);
        errorText.textContent = message;
        errorMessage.classList.remove('d-none');
        errorMessage.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 生成默认标题
    function generateDefaultTitle() {
        let defaultTitle = '';
        
        // 优先使用"突出显示区域"生成标题
        if (enableHighlight.checked) {
            // 使用多区域API
            const highlightRegions = typeof window.getAllHighlightRegions === 'function' 
                ? window.getAllHighlightRegions() 
                : [];
            
            if (highlightRegions.length > 0) {
                if (highlightRegions.length === 1) {
                    defaultTitle = `${highlightRegions[0].name}行政区划图`;
                } else {
                    defaultTitle = `${highlightRegions[0].name}等${highlightRegions.length}个区域行政区划图`;
                }
            } else {
                defaultTitle = "中国行政区划图";
            }
        } else {
            // 如果没有"突出显示区域"，使用"底图区域"
            const mapTypeValue = getCurrentMapType();
            const isNationalMap = mapTypeValue === '省' && isNational();
            
            if (isNationalMap) {
                defaultTitle = "中国行政区划图";
            } else {
                // 构建完整的底图区域路径
                let pathParts = [];
                
                if (provinceSelect.value && provinceSelect.value !== '全国') {
                    pathParts.push(provinceSelect.value);
                    
                    if (citySelect.value) {
                        pathParts.push(citySelect.value);
                        
                        if (countySelect.value) {
                            pathParts.push(countySelect.value);
                        }
                    }
                }
                
                if (pathParts.length > 0) {
                    defaultTitle = `${pathParts.join('')}行政区划图`;
                } else {
                    defaultTitle = "中国行政区划图";
                }
            }
        }
        
        // 设置默认标题
        customTitle.value = defaultTitle;
        return defaultTitle;
    }
    
    // 初始化界面
    updateUIByMapType('national');
    
    // 显示加载指示器
    function showLoadingIndicator() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const mapResult = document.getElementById('mapResult');
        const errorMessage = document.getElementById('errorMessage');
        
        loadingIndicator.classList.remove('d-none');
        mapResult.classList.add('d-none');
        errorMessage.classList.add('d-none');
    }
    
    // 隐藏加载指示器
    function hideLoadingIndicator() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.classList.add('d-none');
    }
    
    // 获取当前地图类型
    function getSelectedMapType() {
        // 获取被选中的地图类型单选按钮
        const selectedRadio = document.querySelector('input[name="mapTypeRadio"]:checked');
        return selectedRadio ? selectedRadio.value : '省';
    }
}); 