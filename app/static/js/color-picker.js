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
                save: true
            }
        }
    };
    
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
        
        pickr.on('save', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
                if (onChange) onChange(hexColor);
                pickr.hide();
            }
        });
        
        pickr.on('change', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
            }
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
        
        pickr.on('save', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
                pickr.hide();
            }
        });
        
        pickr.on('change', (color, instance) => {
            if (color) {
                const hexColor = color.toHEXA().toString();
                element.value = hexColor;
            }
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

