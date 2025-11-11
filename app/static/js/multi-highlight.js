// Multi-region highlight functionality with individual colors
console.log('=== multi-highlight.js 加载 ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== multi-highlight.js: DOMContentLoaded ===');
    
    let regionIndex = 0;
    const highlightRegionsContainer = document.getElementById('highlightRegionsContainer');
    const addHighlightBtn = document.getElementById('addHighlightRegion');
    const enableHighlight = document.getElementById('enableHighlight');
    
    console.log('highlightRegionsContainer:', highlightRegionsContainer);
    console.log('addHighlightBtn:', addHighlightBtn);
    console.log('enableHighlight:', enableHighlight);
    
    // Default colors for different regions
    const defaultColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'];
    
    function getNextColor() {
        return defaultColors[regionIndex % defaultColors.length];
    }
    
    // 获取底图信息（从main.js的DOM元素）
    function getBaseMapInfo() {
        const mapTypeRadios = document.querySelectorAll('input[name="mapTypeRadio"]');
        let mapType = 'national';
        mapTypeRadios.forEach(radio => {
            if (radio.checked) {
                mapType = radio.value;
            }
        });
        
        const provinceSelect = document.getElementById('provinceSelect');
        const citySelect = document.getElementById('citySelect');
        const countySelect = document.getElementById('countySelect');
        
        return {
            mapType: mapType,
            province: provinceSelect ? provinceSelect.value : '',
            city: citySelect ? citySelect.value : '',
            county: countySelect ? countySelect.value : ''
        };
    }
    
    // 根据底图类型初始化高亮区域选择器
    function initializeHighlightSelectors(card, baseMapInfo) {
        const provinceSelect = card.querySelector('.province-select');
        const citySelect = card.querySelector('.city-select');
        const countySelect = card.querySelector('.county-select');
        
        // 获取对应的列容器
        const provinceCol = provinceSelect.closest('.col-md-3');
        const cityCol = citySelect.closest('.col-md-3');
        const countyCol = countySelect.closest('.col-md-3');
        
        console.log('初始化高亮选择器，底图信息:', baseMapInfo);
        
        // 根据底图类型决定哪些选择器可用
        if (baseMapInfo.mapType === 'national') {
            // 全国地图 - 只显示省份选择
            provinceCol.style.display = 'block';
            cityCol.style.display = 'none';
            countyCol.style.display = 'none';
            
            loadProvincesAsync(provinceSelect).then(() => {
                provinceSelect.disabled = false;
                citySelect.disabled = true;
                countySelect.disabled = true;
            });
            
        } else if (baseMapInfo.mapType === '省') {
            // 省级底图 - 只显示省份选择（不显示市和县）
            console.log('省级底图，底图省份:', baseMapInfo.province);
            
            provinceCol.style.display = 'block';
            cityCol.style.display = 'none';
            countyCol.style.display = 'none';
            
            loadProvincesAsync(provinceSelect).then(() => {
                if (baseMapInfo.province && baseMapInfo.province !== '' && baseMapInfo.province !== '请选择省份') {
                    console.log('底图已选择省份，锁定为:', baseMapInfo.province);
                    provinceSelect.value = baseMapInfo.province;
                    provinceSelect.disabled = true; // 锁定省份选择
                } else {
                    console.log('底图未选择省份，保持可选');
                    provinceSelect.disabled = false; // 不锁定，可以选择
                }
            });
            
        } else if (baseMapInfo.mapType === '市') {
            // 市级底图 - 显示省份和城市选择（不显示县）
            console.log('市级底图，底图省份:', baseMapInfo.province, '城市:', baseMapInfo.city);
            
            provinceCol.style.display = 'block';
            cityCol.style.display = 'block';
            countyCol.style.display = 'none';
            
            loadProvincesAsync(provinceSelect).then(() => {
                if (baseMapInfo.province && baseMapInfo.province !== '' && baseMapInfo.province !== '请选择省份') {
                    console.log('底图已选择省份，锁定为:', baseMapInfo.province);
                    provinceSelect.value = baseMapInfo.province;
                    provinceSelect.disabled = true; // 锁定省份选择
                    
                    // 加载该省的城市
                    return loadCitiesAsync(citySelect, baseMapInfo.province);
                } else {
                    console.log('底图未选择省份，保持可选');
                    provinceSelect.disabled = false;
                    citySelect.disabled = true;
                }
            }).then(() => {
                if (baseMapInfo.province && baseMapInfo.province !== '' && baseMapInfo.province !== '请选择省份') {
                    if (baseMapInfo.city && baseMapInfo.city !== '' && baseMapInfo.city !== '请选择城市') {
                        console.log('底图已选择城市，锁定为:', baseMapInfo.city);
                        citySelect.value = baseMapInfo.city;
                        citySelect.disabled = true; // 锁定城市选择
                    } else {
                        console.log('底图未选择城市，保持可选');
                        citySelect.disabled = false;
                    }
                }
            });
            
        } else if (baseMapInfo.mapType === '县') {
            // 县级底图 - 显示省份、城市和县区选择
            console.log('县级底图，底图省份:', baseMapInfo.province, '城市:', baseMapInfo.city);
            
            provinceCol.style.display = 'block';
            cityCol.style.display = 'block';
            countyCol.style.display = 'block';
            
            loadProvincesAsync(provinceSelect).then(() => {
                if (baseMapInfo.province && baseMapInfo.province !== '' && baseMapInfo.province !== '请选择省份') {
                    console.log('底图已选择省份，锁定为:', baseMapInfo.province);
                    provinceSelect.value = baseMapInfo.province;
                    provinceSelect.disabled = true; // 锁定省份
                    
                    return loadCitiesAsync(citySelect, baseMapInfo.province);
                } else {
                    console.log('底图未选择省份，保持可选');
                    provinceSelect.disabled = false;
                    citySelect.disabled = true;
                    countySelect.disabled = true;
                }
            }).then(() => {
                if (baseMapInfo.province && baseMapInfo.province !== '' && baseMapInfo.province !== '请选择省份') {
                    if (baseMapInfo.city && baseMapInfo.city !== '' && baseMapInfo.city !== '请选择城市') {
                        console.log('底图已选择城市，锁定为:', baseMapInfo.city);
                        citySelect.value = baseMapInfo.city;
                        citySelect.disabled = true; // 锁定城市
                        
                        return loadCountiesAsync(countySelect, baseMapInfo.city);
                    } else {
                        console.log('底图未选择城市，保持可选');
                        citySelect.disabled = false;
                        countySelect.disabled = true;
                    }
                }
            }).then(() => {
                if (baseMapInfo.city && baseMapInfo.city !== '' && baseMapInfo.city !== '请选择城市') {
                    countySelect.disabled = false;
                } else {
                    countySelect.disabled = true;
                }
            });
        }
    }
    
    function createHighlightRegion() {
        const index = regionIndex++;
        const color = getNextColor();
        
        // 获取底图信息
        const baseMapInfo = getBaseMapInfo();
        console.log('创建高亮区域，底图信息:', baseMapInfo);
        
        const regionHTML = `
            <div class="card mb-3 highlight-region-card" data-index="${index}">
                <div class="card-body">
                    <div class="row align-items-center mb-2">
                        <div class="col">
                            <h5 class="mb-0">区域 #${index + 1}</h5>
                        </div>
                        <div class="col-auto">
                            <button type="button" class="btn btn-sm btn-outline-danger remove-region-btn" data-index="${index}">
                                删除
                            </button>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-3">
                            <label class="form-label">选择省份</label>
                            <select class="form-select province-select" data-index="${index}">
                                <option value="">请选择省份</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">选择城市</label>
                            <select class="form-select city-select" data-index="${index}" disabled>
                                <option value="">请先选择省份</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">选择县区</label>
                            <select class="form-select county-select" data-index="${index}" disabled>
                                <option value="">请先选择城市</option>
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label class="form-label">突出显示颜色</label>
                            <input type="color" class="form-control form-control-color region-color" data-index="${index}" value="${color}">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        highlightRegionsContainer.insertAdjacentHTML('beforeend', regionHTML);
        
        const card = highlightRegionsContainer.querySelector(`.highlight-region-card[data-index="${index}"]`);
        const provinceSelect = card.querySelector('.province-select');
        const citySelect = card.querySelector('.city-select');
        const countySelect = card.querySelector('.county-select');
        
        // 根据底图类型自动设置和锁定选择器
        initializeHighlightSelectors(card, baseMapInfo);
        
        // Bind events
        bindRegionEvents(index);
        
        updateDeleteButtons();
    }
    
    function bindRegionEvents(index) {
        const card = highlightRegionsContainer.querySelector(`.highlight-region-card[data-index="${index}"]`);
        if (!card) return;
        
        const provinceSelect = card.querySelector('.province-select');
        const citySelect = card.querySelector('.city-select');
        const countySelect = card.querySelector('.county-select');
        const removeBtn = card.querySelector('.remove-region-btn');
        
        // Province change event
        if (provinceSelect) {
            provinceSelect.addEventListener('change', function() {
                const provinceName = this.value;
                citySelect.innerHTML = '<option value="">请先选择省份</option>';
                countySelect.innerHTML = '<option value="">请先选择城市</option>';
                countySelect.disabled = true;
                
                if (provinceName && provinceName !== '全国') {
                    loadCities(citySelect, provinceName);
                    citySelect.disabled = false;
                } else {
                    citySelect.disabled = true;
                }
            });
        }
        
        // City change event
        if (citySelect) {
            citySelect.addEventListener('change', function() {
                const cityName = this.value;
                countySelect.innerHTML = '<option value="">请先选择城市</option>';
                
                if (cityName) {
                    loadCounties(countySelect, cityName);
                    countySelect.disabled = false;
                } else {
                    countySelect.disabled = true;
                }
            });
        }
        
        // Remove button event
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                card.remove();
                updateDeleteButtons();
                renumberRegions();
            });
        }
    }
    
    function updateDeleteButtons() {
        const cards = highlightRegionsContainer.querySelectorAll('.highlight-region-card');
        const removeButtons = highlightRegionsContainer.querySelectorAll('.remove-region-btn');
        
        removeButtons.forEach(btn => {
            btn.style.display = cards.length > 1 ? 'inline-block' : 'none';
        });
    }
    
    function renumberRegions() {
        const cards = highlightRegionsContainer.querySelectorAll('.highlight-region-card');
        cards.forEach((card, idx) => {
            const title = card.querySelector('h5');
            if (title) {
                title.textContent = `区域 #${idx + 1}`;
            }
        });
    }
    
    // 异步加载省份（返回Promise）
    function loadProvincesAsync(selectElement) {
        return fetch('/api/regions?type=province')
            .then(response => response.json())
            .then(data => {
                if (data.success && Array.isArray(data.data)) {
                    selectElement.innerHTML = '<option value="">请选择省份</option>';
                    data.data.forEach(province => {
                        const option = document.createElement('option');
                        option.value = province.value;
                        option.textContent = province.name;
                        selectElement.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error loading provinces:', error));
    }
    
    // 异步加载城市（返回Promise）
    function loadCitiesAsync(selectElement, provinceName) {
        return fetch(`/api/regions?type=city&parent=${encodeURIComponent(provinceName)}`)
            .then(response => response.json())
            .then(data => {
                selectElement.innerHTML = '<option value="">请选择城市</option>';
                if (data.success && Array.isArray(data.data)) {
                    data.data.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.value;
                        option.textContent = city.name;
                        selectElement.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error loading cities:', error));
    }
    
    // 异步加载县区（返回Promise）
    function loadCountiesAsync(selectElement, cityName) {
        return fetch(`/api/regions?type=county&parent=${encodeURIComponent(cityName)}`)
            .then(response => response.json())
            .then(data => {
                selectElement.innerHTML = '<option value="">请选择县区</option>';
                if (data.success && Array.isArray(data.data)) {
                    data.data.forEach(county => {
                        const option = document.createElement('option');
                        option.value = county.value;
                        option.textContent = county.name;
                        selectElement.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Error loading counties:', error));
    }
    
    // 同步版本（用于事件处理）
    function loadProvinces(selectElement) {
        loadProvincesAsync(selectElement);
    }
    
    function loadCities(selectElement, provinceName) {
        loadCitiesAsync(selectElement, provinceName);
    }
    
    function loadCounties(selectElement, cityName) {
        loadCountiesAsync(selectElement, cityName);
    }
    
    // Public API: Get all highlight regions with their colors
    window.getAllHighlightRegions = function() {
        console.log('=== getAllHighlightRegions 被调用 ===');
        const regions = [];
        
        if (!highlightRegionsContainer) {
            console.warn('highlightRegionsContainer 不存在');
            return regions;
        }
        
        const cards = highlightRegionsContainer.querySelectorAll('.highlight-region-card');
        console.log(`找到 ${cards.length} 个高亮区域卡片`);
        
        cards.forEach((card, idx) => {
            const index = card.dataset.index;
            console.log(`处理卡片 #${idx}, data-index=${index}`);
            
            const countySelect = card.querySelector('.county-select');
            const citySelect = card.querySelector('.city-select');
            const provinceSelect = card.querySelector('.province-select');
            const colorInput = card.querySelector('.region-color');
            
            console.log('选择器值:', {
                county: countySelect?.value,
                city: citySelect?.value,
                province: provinceSelect?.value,
                color: colorInput?.value
            });
            
            let regionName = '';
            if (countySelect && countySelect.value) {
                regionName = countySelect.value;
            } else if (citySelect && citySelect.value) {
                regionName = citySelect.value;
            } else if (provinceSelect && provinceSelect.value) {
                regionName = provinceSelect.value;
            }
            
            if (regionName) {
                const region = {
                    name: regionName,
                    color: colorInput ? colorInput.value : '#7ED2F7'
                };
                regions.push(region);
                console.log(`添加区域:`, region);
            } else {
                console.log(`卡片 #${idx} 没有选择区域，跳过`);
            }
        });
        
        console.log('最终返回的区域数组:', regions);
        return regions;
    };
    
    // 更新所有现有高亮区域的选择器（当底图改变时）
    function updateAllHighlightRegions() {
        console.log('=== 更新所有高亮区域 ===');
        const baseMapInfo = getBaseMapInfo();
        const cards = highlightRegionsContainer.querySelectorAll('.highlight-region-card');
        
        cards.forEach(card => {
            initializeHighlightSelectors(card, baseMapInfo);
        });
    }
    
    // 暴露给全局，以便main.js可以调用
    window.updateHighlightRegions = updateAllHighlightRegions;
    
    // Initialize
    if (addHighlightBtn) {
        addHighlightBtn.addEventListener('click', createHighlightRegion);
    }
    
    if (enableHighlight) {
        enableHighlight.addEventListener('change', function() {
            if (this.checked && highlightRegionsContainer.children.length === 0) {
                createHighlightRegion();
            }
        });
    }
    
    // 监听底图区域变化
    const baseProvinceSelect = document.getElementById('provinceSelect');
    const baseCitySelect = document.getElementById('citySelect');
    const mapTypeRadios = document.querySelectorAll('input[name="mapTypeRadio"]');
    
    // 监听地图类型变化
    if (mapTypeRadios) {
        mapTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (enableHighlight && enableHighlight.checked) {
                    console.log('地图类型改变，更新高亮区域');
                    updateAllHighlightRegions();
                }
            });
        });
    }
    
    // 监听底图省份变化
    if (baseProvinceSelect) {
        baseProvinceSelect.addEventListener('change', function() {
            if (enableHighlight && enableHighlight.checked) {
                console.log('底图省份改变，更新高亮区域');
                updateAllHighlightRegions();
            }
        });
    }
    
    // 监听底图城市变化
    if (baseCitySelect) {
        baseCitySelect.addEventListener('change', function() {
            if (enableHighlight && enableHighlight.checked) {
                console.log('底图城市改变，更新高亮区域');
                updateAllHighlightRegions();
            }
        });
    }
    
    console.log('=== multi-highlight.js 初始化完成 ===');
});

