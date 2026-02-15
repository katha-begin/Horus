/**
 * Horus Web Player - Color Management System
 * OpenColorIO-inspired color grading controls
 */

class ColorManagement {
    constructor(player) {
        this.player = player;
        this.video = player.video;

        this.brightness = 0;
        this.contrast = 0;
        this.saturation = 0;
        this.exposure = 0;

        this.init();
    }

    init() {
        this.setupControls();
    }

    setupControls() {
        // Brightness
        const brightnessSlider = document.getElementById('brightness');
        const brightnessValue = document.getElementById('brightnessValue');

        brightnessSlider.addEventListener('input', (e) => {
            this.brightness = parseInt(e.target.value);
            brightnessValue.textContent = this.brightness;
            this.applyFilters();
        });

        // Contrast
        const contrastSlider = document.getElementById('contrast');
        const contrastValue = document.getElementById('contrastValue');

        contrastSlider.addEventListener('input', (e) => {
            this.contrast = parseInt(e.target.value);
            contrastValue.textContent = this.contrast;
            this.applyFilters();
        });

        // Saturation
        const saturationSlider = document.getElementById('saturation');
        const saturationValue = document.getElementById('saturationValue');

        saturationSlider.addEventListener('input', (e) => {
            this.saturation = parseInt(e.target.value);
            saturationValue.textContent = this.saturation;
            this.applyFilters();
        });

        // Exposure
        const exposureSlider = document.getElementById('exposure');
        const exposureValue = document.getElementById('exposureValue');

        exposureSlider.addEventListener('input', (e) => {
            this.exposure = parseFloat(e.target.value);
            exposureValue.textContent = this.exposure.toFixed(1);
            this.applyFilters();
        });

        // Reset button
        document.getElementById('resetColor').addEventListener('click', () => {
            this.resetAll();
        });
    }

    applyFilters() {
        // Convert values to CSS filter format
        const brightnessValue = 100 + this.brightness; // 0-200%
        const contrastValue = 100 + this.contrast; // 0-200%
        const saturationValue = 100 + this.saturation; // 0-200%

        // Exposure is simulated with brightness (simplified)
        const exposureValue = 100 + (this.exposure * 50); // Approximate exposure adjustment

        const filterString = `
            brightness(${brightnessValue}%)
            contrast(${contrastValue}%)
            saturate(${saturationValue}%)
        `.trim();

        this.video.style.filter = filterString;

        // If exposure is being used, combine it
        if (this.exposure !== 0) {
            this.video.style.filter = `${filterString} brightness(${exposureValue}%)`;
        }
    }

    resetAll() {
        this.brightness = 0;
        this.contrast = 0;
        this.saturation = 0;
        this.exposure = 0;

        // Reset sliders
        document.getElementById('brightness').value = 0;
        document.getElementById('contrast').value = 0;
        document.getElementById('saturation').value = 0;
        document.getElementById('exposure').value = 0;

        // Reset value displays
        document.getElementById('brightnessValue').textContent = '0';
        document.getElementById('contrastValue').textContent = '0';
        document.getElementById('saturationValue').textContent = '0';
        document.getElementById('exposureValue').textContent = '0.0';

        // Reset video filter
        this.video.style.filter = 'none';

        this.player.updateStatus('Color settings reset');
    }

    // Advanced color grading methods (for future LUT support)
    applyLUT(lutData) {
        // Placeholder for LUT application
        // In a full implementation, this would use WebGL shaders
        // to apply 3D LUTs for professional color grading
        console.log('LUT application not yet implemented');
    }

    applyCDL(slope, offset, power) {
        // Placeholder for ASC CDL (Color Decision List) support
        // slope, offset, and power parameters for primary color correction
        console.log('CDL application not yet implemented');
    }

    exportColorSettings() {
        return {
            brightness: this.brightness,
            contrast: this.contrast,
            saturation: this.saturation,
            exposure: this.exposure
        };
    }

    importColorSettings(settings) {
        if (!settings) return;

        this.brightness = settings.brightness || 0;
        this.contrast = settings.contrast || 0;
        this.saturation = settings.saturation || 0;
        this.exposure = settings.exposure || 0;

        // Update UI
        document.getElementById('brightness').value = this.brightness;
        document.getElementById('contrast').value = this.contrast;
        document.getElementById('saturation').value = this.saturation;
        document.getElementById('exposure').value = this.exposure;

        document.getElementById('brightnessValue').textContent = this.brightness;
        document.getElementById('contrastValue').textContent = this.contrast;
        document.getElementById('saturationValue').textContent = this.saturation;
        document.getElementById('exposureValue').textContent = this.exposure.toFixed(1);

        this.applyFilters();
    }
}

// Initialize color management when player is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.horusPlayer) {
            window.colorManagement = new ColorManagement(window.horusPlayer);
        }
    }, 100);
});
