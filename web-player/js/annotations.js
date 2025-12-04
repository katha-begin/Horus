/**
 * Horus Web Player - Annotation System
 * Frame-accurate drawing and annotation tools
 */

class AnnotationController {
    constructor(player) {
        this.player = player;
        this.canvas = document.getElementById('annotationCanvas');
        this.ctx = this.canvas.getContext('2d');

        this.currentTool = 'select';
        this.annotations = {}; // Keyed by frame number
        this.currentAnnotations = [];
        this.isDrawing = false;
        this.startPoint = null;
        this.currentShape = null;
        this.color = '#ff0000';

        this.init();
    }

    init() {
        this.setupCanvas();
        this.setupToolbar();
        this.setupEventListeners();
    }

    setupCanvas() {
        // Match canvas size to video
        const resizeCanvas = () => {
            const video = this.player.video;
            if (video.videoWidth && video.videoHeight) {
                this.canvas.width = video.offsetWidth;
                this.canvas.height = video.offsetHeight;
                this.redraw();
            }
        };

        this.player.video.addEventListener('loadedmetadata', resizeCanvas);
        window.addEventListener('resize', resizeCanvas);

        // Initial resize
        resizeCanvas();
    }

    setupToolbar() {
        // Tool selection
        document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
            btn.addEventListener('click', () => {
                this.setTool(btn.dataset.tool);

                // Update active state
                document.querySelectorAll('.tool-btn[data-tool]').forEach(b => {
                    b.classList.remove('active');
                });
                btn.classList.add('active');
            });
        });

        // Color picker
        document.getElementById('annotationColor').addEventListener('change', (e) => {
            this.color = e.target.value;
        });

        // Clear annotations
        document.getElementById('clearAnnotations').addEventListener('click', () => {
            this.clearCurrentFrame();
        });

        // Export/Import
        document.getElementById('exportAnnotations').addEventListener('click', () => {
            this.exportAnnotations();
        });

        document.getElementById('importAnnotations').addEventListener('click', () => {
            this.importAnnotations();
        });
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));

        // Update annotations when video frame changes
        this.player.video.addEventListener('timeupdate', () => {
            this.loadFrameAnnotations();
        });
    }

    setTool(tool) {
        this.currentTool = tool;
        this.canvas.style.cursor = tool === 'select' ? 'default' : 'crosshair';
    }

    onMouseDown(e) {
        if (this.currentTool === 'select') return;

        this.isDrawing = true;
        this.startPoint = this.getMousePos(e);

        if (this.currentTool === 'pen') {
            this.currentShape = {
                type: 'pen',
                points: [this.startPoint],
                color: this.color,
                frame: this.player.currentFrame
            };
        }
    }

    onMouseMove(e) {
        if (!this.isDrawing) return;

        const currentPoint = this.getMousePos(e);

        if (this.currentTool === 'pen') {
            this.currentShape.points.push(currentPoint);
            this.redraw();
            this.drawShape(this.currentShape);
        } else {
            // For shapes, show preview
            this.redraw();
            this.drawShapePreview(this.startPoint, currentPoint);
        }
    }

    onMouseUp(e) {
        if (!this.isDrawing) return;

        this.isDrawing = false;
        const endPoint = this.getMousePos(e);

        if (this.currentTool !== 'pen') {
            this.currentShape = {
                type: this.currentTool,
                start: this.startPoint,
                end: endPoint,
                color: this.color,
                frame: this.player.currentFrame
            };
        }

        if (this.currentShape) {
            this.saveAnnotation(this.currentShape);
            this.currentShape = null;
        }
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    drawShape(shape) {
        this.ctx.strokeStyle = shape.color;
        this.ctx.lineWidth = 2;
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';

        switch (shape.type) {
            case 'pen':
                this.drawPen(shape.points);
                break;
            case 'arrow':
                this.drawArrow(shape.start, shape.end);
                break;
            case 'rect':
                this.drawRect(shape.start, shape.end);
                break;
            case 'circle':
                this.drawCircle(shape.start, shape.end);
                break;
            case 'text':
                this.drawText(shape);
                break;
        }
    }

    drawShapePreview(start, end) {
        this.ctx.strokeStyle = this.color;
        this.ctx.lineWidth = 2;

        switch (this.currentTool) {
            case 'arrow':
                this.drawArrow(start, end);
                break;
            case 'rect':
                this.drawRect(start, end);
                break;
            case 'circle':
                this.drawCircle(start, end);
                break;
        }
    }

    drawPen(points) {
        if (points.length < 2) return;

        this.ctx.beginPath();
        this.ctx.moveTo(points[0].x, points[0].y);

        for (let i = 1; i < points.length; i++) {
            this.ctx.lineTo(points[i].x, points[i].y);
        }

        this.ctx.stroke();
    }

    drawArrow(start, end) {
        const headLength = 15;
        const angle = Math.atan2(end.y - start.y, end.x - start.x);

        // Draw line
        this.ctx.beginPath();
        this.ctx.moveTo(start.x, start.y);
        this.ctx.lineTo(end.x, end.y);
        this.ctx.stroke();

        // Draw arrow head
        this.ctx.beginPath();
        this.ctx.moveTo(end.x, end.y);
        this.ctx.lineTo(
            end.x - headLength * Math.cos(angle - Math.PI / 6),
            end.y - headLength * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.moveTo(end.x, end.y);
        this.ctx.lineTo(
            end.x - headLength * Math.cos(angle + Math.PI / 6),
            end.y - headLength * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.stroke();
    }

    drawRect(start, end) {
        this.ctx.strokeRect(
            start.x,
            start.y,
            end.x - start.x,
            end.y - start.y
        );
    }

    drawCircle(start, end) {
        const radius = Math.sqrt(
            Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2)
        );

        this.ctx.beginPath();
        this.ctx.arc(start.x, start.y, radius, 0, 2 * Math.PI);
        this.ctx.stroke();
    }

    drawText(shape) {
        this.ctx.fillStyle = shape.color;
        this.ctx.font = '16px Arial';
        this.ctx.fillText(shape.text || 'Text', shape.start.x, shape.start.y);
    }

    saveAnnotation(shape) {
        const frame = this.player.currentFrame;

        if (!this.annotations[frame]) {
            this.annotations[frame] = [];
        }

        this.annotations[frame].push(shape);
        this.currentAnnotations.push(shape);
        this.redraw();
        this.updateAnnotationList();
    }

    loadFrameAnnotations() {
        const frame = this.player.currentFrame;
        this.currentAnnotations = this.annotations[frame] || [];
        this.redraw();
    }

    clearCurrentFrame() {
        const frame = this.player.currentFrame;
        delete this.annotations[frame];
        this.currentAnnotations = [];
        this.redraw();
        this.updateAnnotationList();
    }

    redraw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (const shape of this.currentAnnotations) {
            this.drawShape(shape);
        }
    }

    updateAnnotationList() {
        const list = document.getElementById('annotationList');
        const totalAnnotations = Object.keys(this.annotations).reduce(
            (sum, frame) => sum + this.annotations[frame].length,
            0
        );

        if (totalAnnotations === 0) {
            list.innerHTML = '<p class="empty-state">No annotations yet. Use the tools to add annotations.</p>';
            return;
        }

        let html = '';
        for (const [frame, shapes] of Object.entries(this.annotations)) {
            for (const shape of shapes) {
                html += `
                    <div class="annotation-item" data-frame="${frame}">
                        <strong>Frame ${frame}</strong> - ${shape.type}
                    </div>
                `;
            }
        }

        list.innerHTML = html;

        // Add click handlers to jump to frame
        list.querySelectorAll('.annotation-item').forEach(item => {
            item.addEventListener('click', () => {
                const frame = parseInt(item.dataset.frame);
                this.player.goToFrame(frame);
            });
        });
    }

    exportAnnotations() {
        const data = {
            version: '1.0',
            fps: this.player.currentFPS,
            annotations: this.annotations
        };

        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'annotations.json';
        a.click();

        URL.revokeObjectURL(url);
        this.player.updateStatus('Annotations exported successfully');
    }

    importAnnotations() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json';

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    this.annotations = data.annotations || {};
                    this.loadFrameAnnotations();
                    this.updateAnnotationList();
                    this.player.updateStatus('Annotations imported successfully');
                } catch (error) {
                    this.player.updateStatus('Error importing annotations');
                    console.error('Import error:', error);
                }
            };

            reader.readAsText(file);
        });

        input.click();
    }
}

// Initialize annotation controller when player is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.horusPlayer) {
            window.annotationController = new AnnotationController(window.horusPlayer);
        }
    }, 100);
});
