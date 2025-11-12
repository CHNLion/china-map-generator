// Color Picker Initialization using Pickr
console.log('=== color-picker.js loaded ===');

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== Initializing Pickr color pickers ===');
    
    const pickrInstances = {};
    
    // Pickr configuration
    const pickrConfig = {
        theme: 'nano',
        swatches: [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
            '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
            '#EAEAEA', '#FFFFFF', '#000000', '#FF0000',
            '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'
        ],
        components: {
            preview: true,
            opacity: false,
            hue: true,
            interaction: {
                hex: true,
                rgba: false,
                hsla: false,
                hsva: false,
                cmyk: false,
                input: true,
                clear: false,
                save: false,  // 禁用 Save 按钮
                cancel: false  // 禁用 Cancel 按钮
            }
        },
        useAsButton: false,
        inline: false,
        autoReposition: true,
        closeWithKey: 'Escape',
        closeOnScroll: false,
        appClass: 'custom-pickr'
    };
    
    // Helper function to add eyedropper button
    function addEyedropperButton(pickr, element) {
        if (!window.EyeDropper) {
            console.warn('EyeDropper API not supported in this browser');
            return;
        }
        
        // Check if button already added
        const existingBtn = document.querySelector('.pcr-eyedropper-btn-' + element.id);
        if (existingBtn) {
            console.log('Eyedropper button already exists for', element.id);
            return;
        }
        
        // Wait for Pickr to render
        setTimeout(() => {
            const pickrRoot = pickr.getRoot();
            if (!pickrRoot) {
                console.warn('Pickr root not found');
                return;
            }
            
            console.log('Pickr root found:', pickrRoot);
            
            // Find the interaction container (where buttons are)
            const interactionDiv = pickrRoot.interaction;
            if (!interactionDiv) {
                console.warn('Interaction div not found');
                return;
            }
            
            console.log('Interaction div found:', interactionDiv);
            
            // The interaction is an object, we need to find the actual DOM element
            // Find all visible pickr apps (the one that's currently open)
            const allPickrApps = document.querySelectorAll('.pcr-app');
            let pickrApp = null;
            
            // Find the visible one
            for (let app of allPickrApps) {
                if (app.classList.contains('visible')) {
                    pickrApp = app;
                    break;
                }
            }
            
            if (!pickrApp && allPickrApps.length > 0) {
                // If no visible class, just use the last one (usually the most recently opened)
                pickrApp = allPickrApps[allPickrApps.length - 1];
            }
            
            if (!pickrApp) {
                console.warn('Pickr app element not found');
                return;
            }
            
            console.log('Pickr app found:', pickrApp);
            
            // Find the interaction section
            const interactionElement = pickrApp.querySelector('.pcr-interaction');
            if (!interactionElement) {
                console.warn('Interaction element not found in DOM');
                return;
            }
            
            console.log('Interaction element found:', interactionElement);
            
            // Create eyedropper button
            const eyedropperBtn = document.createElement('button');
            eyedropperBtn.type = 'button';
            eyedropperBtn.className = 'pcr-eyedropper-btn pcr-eyedropper-btn-' + element.id;
            // 使用 SVG 吸管图标
            eyedropperBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M13.354.646a1.207 1.207 0 0 0-1.708 0L8.5 3.793l-.646-.647a.5.5 0 1 0-.708.708L8.293 5l-7.147 7.146A.5.5 0 0 0 1 12.5v1.793l-.854.853a.5.5 0 1 0 .708.707L1.707 15H3.5a.5.5 0 0 0 .354-.146L11 7.707l1.146 1.147a.5.5 0 0 0 .708-.708l-.647-.646 3.147-3.146a1.207 1.207 0 0 0 0-1.708l-2-2zM2 12.707l7-7L10.293 7l-7 7H2v-1.293z"/>
            </svg>`;
            eyedropperBtn.title = '吸管取色工具';
            eyedropperBtn.style.cssText = 'margin: 0 4px; padding: 6px 10px; cursor: pointer; border: 1px solid #42445a; border-radius: 3px; background: white; display: inline-flex; align-items: center; justify-content: center;';
            
            eyedropperBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                try {
                    console.log('Opening eyedropper...');
                    const eyeDropper = new EyeDropper();
                    const result = await eyeDropper.open();
                    if (result && result.sRGBHex) {
                        console.log('Color selected:', result.sRGBHex);
                        pickr.setColor(result.sRGBHex);
                        element.value = result.sRGBHex;
                        // 取色成功后，更新按钮显示并关闭调色板
                        pickr.applyColor(true);
                        setTimeout(() => {
                            pickr.hide();
                        }, 100);
                    }
                } catch (err) {
                    if (err.name !== 'AbortError') {
                        console.error('Eyedropper error:', err);
                        alert('吸管工具出错: ' + err.message);
                    }
                }
            });
            
            // Find the result input field and insert eyedropper button next to it
            const resultInput = interactionElement.querySelector('.pcr-result');
            if (resultInput && resultInput.parentNode) {
                console.log('Inserting eyedropper button next to result input');
                
                // Create a wrapper to hold both the input and eyedropper button
                const wrapper = document.createElement('div');
                wrapper.style.cssText = 'display: flex; align-items: center; gap: 4px; width: 100%;';
                
                // Adjust the eyedropper button style for better alignment
                eyedropperBtn.style.cssText = 'padding: 4px 8px; cursor: pointer; border: 1px solid #42445a; border-radius: 3px; background: white; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; height: 26px;';
                
                // Wrap the input
                resultInput.parentNode.insertBefore(wrapper, resultInput);
                wrapper.appendChild(resultInput);
                wrapper.appendChild(eyedropperBtn);
                
                return;
            }
            
            // Fallback: Try to find the save button and insert before it
            const saveBtn = interactionElement.querySelector('.pcr-save');
            if (saveBtn && saveBtn.parentNode) {
                console.log('Inserting eyedropper button before save button');
                saveBtn.parentNode.insertBefore(eyedropperBtn, saveBtn);
                return;
            }
            
            // Final fallback: Append to interaction element
            console.log('Appending eyedropper button to interaction element');
            interactionElement.appendChild(eyedropperBtn);
        }, 500); // Increase timeout to ensure Pickr is fully rendered
    }
    
    // Initialize base color pickers
    function initializeColorPicker(elementId, defaultColor, onChange) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Element ${elementId} not found`);
            return null;
        }
        
        // Create a button wrapper for Pickr
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'pickr-button';
        button.style.cssText = 'width: 100%; height: 38px; border-radius: 4px;';
        
        element.parentNode.insertBefore(button, element);
        element.style.display = 'none'; // Hide original input
        
        const pickr = Pickr.create({
            el: button,
            ...pickrConfig,
            default: defaultColor
        });
        
        // 实时更新颜色（拖动时就更新）
        pickr.on('change', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
                if (onChange) onChange(hexColor);
                console.log('Color changed:', hexColor);
            }
        });
        
        // 鼠标释放时也更新并关闭调色板
        pickr.on('changestop', (source, instance) => {
            // 给一点时间让 change 事件先完成
            setTimeout(() => {
                const color = pickr.getColor();
                if (color) {
                    const hexColor = color.toHEXA().toString();
                    element.value = hexColor;
                    // 使用 Pickr 的 applyColor 方法更新按钮显示
                    pickr.applyColor(true);
                    if (onChange) onChange(hexColor);
                    console.log('Color selected on changestop:', hexColor);
                }
                // 关闭调色板
                pickr.hide();
            }, 50);
        });
        
        // 点击预设色块时更新并立即关闭
        pickr.on('swatchselect', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
                // 使用 Pickr 的 applyColor 方法更新按钮显示
                pickr.applyColor(true);
                if (onChange) onChange(hexColor);
                console.log('Swatch selected:', hexColor);
                // 点击色块后立即关闭
                pickr.hide();
            }
        });
        
        // Add eyedropper button when pickr is shown
        pickr.on('show', () => {
            addEyedropperButton(pickr, element);
        });
        
        return pickr;
    }
    
    // Initialize main color pickers
    pickrInstances.baseColor = initializeColorPicker('baseColor', '#EAEAEA');
    pickrInstances.borderColor = initializeColorPicker('borderColor', '#FFFFFF');
    pickrInstances.highlightColor = initializeColorPicker('highlightColor', '#7ED2F7');
    
    console.log('Main color pickers initialized:', Object.keys(pickrInstances));
    
    // Function to initialize dynamic color pickers (for multi-highlight regions)
    window.initDynamicColorPicker = function(element, defaultColor) {
        if (!element || element.dataset.pickrInitialized) return;
        
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'pickr-button';
        button.style.cssText = 'width: 60px; height: 38px; border-radius: 4px;';
        
        element.parentNode.insertBefore(button, element);
        element.style.display = 'none';
        element.dataset.pickrInitialized = 'true';
        
        const pickr = Pickr.create({
            el: button,
            ...pickrConfig,
            default: defaultColor || element.value
        });
        
        // 实时更新颜色（拖动时就更新）
        pickr.on('change', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
            }
        });
        
        // 鼠标释放时也更新并关闭调色板
        pickr.on('changestop', (source, instance) => {
            // 给一点时间让 change 事件先完成
            setTimeout(() => {
                const color = pickr.getColor();
                if (color) {
                    const hexColor = color.toHEXA().toString();
                    element.value = hexColor;
                    // 使用 Pickr 的 applyColor 方法更新按钮显示
                    pickr.applyColor(true);
                    console.log('Color selected on changestop (dynamic):', hexColor);
                }
                // 关闭调色板
                pickr.hide();
            }, 50);
        });
        
        // 点击预设色块时更新并立即关闭
        pickr.on('swatchselect', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
                // 使用 Pickr 的 applyColor 方法更新按钮显示
                pickr.applyColor(true);
                console.log('Swatch selected (dynamic):', hexColor);
                // 点击色块后立即关闭
                pickr.hide();
            }
        });
        
        // Add eyedropper button when pickr is shown
        pickr.on('show', () => {
            addEyedropperButton(pickr, element);
        });
        
        return pickr;
    };
    
    // Observer to watch for dynamically added color inputs
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    const colorInputs = node.querySelectorAll('input[type="color"].region-color');
                    colorInputs.forEach(input => {
                        if (!input.dataset.pickrInitialized) {
                            console.log('Initializing dynamic color picker for:', input);
                            window.initDynamicColorPicker(input, input.value);
                        }
                    });
                }
            });
        });
    });
    
    // Start observing
    const container = document.getElementById('highlightRegionsContainer');
    if (container) {
        observer.observe(container, {
            childList: true,
            subtree: true
        });
        console.log('Started observing for dynamic color pickers');
    }
    
    console.log('=== Pickr color pickers initialization complete ===');
});

