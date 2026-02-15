/**
 * Horus Web Player - Main Player Controller
 * OpenRV-inspired video playback system for VFX review
 */

class HorusPlayer {
    constructor() {
        this.video = document.getElementById('videoPlayer');
        this.isPlaying = false;
        this.currentFPS = 24;
        this.totalFrames = 0;
        this.currentFrame = 0;
        this.isLooping = false;
        this.markers = [];

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFileInput();
        this.setupTransportControls();
        this.setupKeyboardShortcuts();
        this.updateStatus('Ready - Load a media file to begin');
    }

    setupEventListeners() {
        // Video events
        this.video.addEventListener('loadedmetadata', () => this.onVideoLoaded());
        this.video.addEventListener('timeupdate', () => this.onTimeUpdate());
        this.video.addEventListener('ended', () => this.onVideoEnded());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());

        // FPS input
        document.getElementById('fpsInput').addEventListener('change', (e) => {
            this.currentFPS = parseInt(e.target.value);
            this.updateFrameInfo();
        });

        // Playback speed
        document.getElementById('playbackSpeed').addEventListener('change', (e) => {
            this.video.playbackRate = parseFloat(e.target.value);
        });
    }

    setupFileInput() {
        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.loadMedia(file);
            }
        });

        // Drag and drop support
        document.body.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
        });

        document.body.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('video/')) {
                this.loadMedia(file);
            }
        });
    }

    setupTransportControls() {
        // Play/Pause
        document.getElementById('playPause').addEventListener('click', () => {
            this.togglePlayPause();
        });

        // First frame
        document.getElementById('firstFrame').addEventListener('click', () => {
            this.goToFrame(0);
        });

        // Previous frame
        document.getElementById('prevFrame').addEventListener('click', () => {
            this.stepBackward();
        });

        // Next frame
        document.getElementById('nextFrame').addEventListener('click', () => {
            this.stepForward();
        });

        // Last frame
        document.getElementById('lastFrame').addEventListener('click', () => {
            this.goToFrame(this.totalFrames);
        });

        // Loop toggle
        document.getElementById('loop').addEventListener('click', () => {
            this.toggleLoop();
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input fields
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch(e.key) {
                case ' ':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.stepBackward();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.stepForward();
                    break;
                case 'Home':
                    e.preventDefault();
                    this.goToFrame(0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToFrame(this.totalFrames);
                    break;
                case 'l':
                case 'L':
                    this.toggleLoop();
                    break;
                case 'm':
                case 'M':
                    this.addMarker();
                    break;
            }
        });
    }

    loadMedia(file) {
        const url = URL.createObjectURL(file);
        this.video.src = url;
        this.video.load();

        this.updateStatus(`Loading: ${file.name}`);
        document.getElementById('fileInfo').textContent = file.name;
    }

    onVideoLoaded() {
        const duration = this.video.duration;
        this.totalFrames = Math.floor(duration * this.currentFPS);

        // Update UI
        document.getElementById('totalFrames').textContent = this.totalFrames;
        document.getElementById('resolution').textContent =
            `${this.video.videoWidth}x${this.video.videoHeight}`;

        // Update media info
        this.updateMediaInfo();

        // Initialize timeline
        if (window.timelineController) {
            window.timelineController.setDuration(duration);
        }

        this.updateStatus('Media loaded successfully');
        this.updateFrameInfo();
    }

    onTimeUpdate() {
        this.currentFrame = Math.floor(this.video.currentTime * this.currentFPS);
        this.updateFrameInfo();
        this.updateTimecode();

        // Update timeline
        if (window.timelineController) {
            window.timelineController.updateProgress(
                this.video.currentTime / this.video.duration
            );
        }
    }

    onVideoEnded() {
        if (this.isLooping) {
            this.video.currentTime = 0;
            this.video.play();
        } else {
            this.isPlaying = false;
            this.updatePlayButton();
        }
    }

    onPlay() {
        this.isPlaying = true;
        this.updatePlayButton();
    }

    onPause() {
        this.isPlaying = false;
        this.updatePlayButton();
    }

    togglePlayPause() {
        if (this.isPlaying) {
            this.video.pause();
        } else {
            this.video.play();
        }
    }

    stepForward() {
        const frameDuration = 1 / this.currentFPS;
        this.video.currentTime = Math.min(
            this.video.currentTime + frameDuration,
            this.video.duration
        );
        this.video.pause();
    }

    stepBackward() {
        const frameDuration = 1 / this.currentFPS;
        this.video.currentTime = Math.max(
            this.video.currentTime - frameDuration,
            0
        );
        this.video.pause();
    }

    goToFrame(frameNumber) {
        const time = frameNumber / this.currentFPS;
        this.video.currentTime = Math.min(time, this.video.duration);
        this.video.pause();
    }

    toggleLoop() {
        this.isLooping = !this.isLooping;
        this.video.loop = this.isLooping;

        const loopBtn = document.getElementById('loop');
        if (this.isLooping) {
            loopBtn.classList.add('active');
        } else {
            loopBtn.classList.remove('active');
        }
    }

    addMarker() {
        if (!this.video.src) return;

        const marker = {
            frame: this.currentFrame,
            time: this.video.currentTime,
            label: `Marker ${this.markers.length + 1}`
        };

        this.markers.push(marker);

        if (window.timelineController) {
            window.timelineController.addMarker(marker);
        }

        this.updateStatus(`Added marker at frame ${this.currentFrame}`);
    }

    updatePlayButton() {
        const btn = document.getElementById('playPause');
        btn.textContent = this.isPlaying ? '⏸' : '▶';
    }

    updateFrameInfo() {
        document.getElementById('currentFrame').textContent = this.currentFrame;
        document.getElementById('totalFrames').textContent = this.totalFrames;
    }

    updateTimecode() {
        const totalSeconds = this.video.currentTime;
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = Math.floor(totalSeconds % 60);
        const frames = Math.floor((totalSeconds % 1) * this.currentFPS);

        const timecode = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;

        document.getElementById('timecode').textContent = timecode;
    }

    updateMediaInfo() {
        const info = `
            <p><strong>Duration:</strong> ${this.video.duration.toFixed(2)}s</p>
            <p><strong>Resolution:</strong> ${this.video.videoWidth}x${this.video.videoHeight}</p>
            <p><strong>FPS:</strong> ${this.currentFPS}</p>
            <p><strong>Total Frames:</strong> ${this.totalFrames}</p>
            <p><strong>Format:</strong> ${this.video.src.split('.').pop().toUpperCase()}</p>
        `;

        document.getElementById('mediaInfo').innerHTML = info;
    }

    updateStatus(message) {
        document.getElementById('statusMessage').textContent = message;
    }

    seekToTime(time) {
        this.video.currentTime = time;
    }

    seekToPercent(percent) {
        this.video.currentTime = this.video.duration * percent;
    }
}

// Initialize player when DOM is ready
let player;
document.addEventListener('DOMContentLoaded', () => {
    player = new HorusPlayer();
    window.horusPlayer = player;
});
