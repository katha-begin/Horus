/**
 * Horus Web Player - Image Sequence Support
 * Load and playback image sequences (EXR, DPX, PNG, JPG sequences)
 */

class ImageSequencePlayer {
    constructor(player) {
        this.player = player;
        this.canvas = document.getElementById('imageSequenceCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.videoElement = document.getElementById('videoPlayer');

        this.images = [];
        this.currentIndex = 0;
        this.isPlaying = false;
        this.playbackInterval = null;
        this.fps = 24;

        this.isSequenceMode = false;

        this.init();
    }

    init() {
        this.setupFileInput();
    }

    setupFileInput() {
        const fileInput = document.getElementById('fileInput');
        const originalHandler = fileInput.onchange;

        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);

            // Check if multiple image files are selected
            const imageFiles = files.filter(f =>
                f.type.startsWith('image/')
            );

            if (imageFiles.length > 1) {
                e.stopPropagation();
                this.loadImageSequence(imageFiles);
            } else if (imageFiles.length === 1) {
                // Single image, display it
                this.loadSingleImage(imageFiles[0]);
            }
        });
    }

    loadImageSequence(files) {
        this.isSequenceMode = true;
        this.images = [];

        // Sort files by name (assumes naming like frame_0001.png, frame_0002.png, etc.)
        const sortedFiles = files.sort((a, b) => a.name.localeCompare(b.name));

        this.player.updateStatus(`Loading ${sortedFiles.length} images...`);

        // Load all images
        const loadPromises = sortedFiles.map(file => {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = URL.createObjectURL(file);
            });
        });

        Promise.all(loadPromises)
            .then(loadedImages => {
                this.images = loadedImages;
                this.setupSequencePlayback();
                this.player.updateStatus(`Loaded ${this.images.length} frame sequence`);
            })
            .catch(error => {
                this.player.updateStatus('Error loading image sequence');
                console.error('Image sequence load error:', error);
            });
    }

    loadSingleImage(file) {
        this.isSequenceMode = true;
        this.images = [];

        const img = new Image();
        img.onload = () => {
            this.images = [img];
            this.setupSequencePlayback();
            this.player.updateStatus('Single image loaded');
        };
        img.onerror = () => {
            this.player.updateStatus('Error loading image');
        };
        img.src = URL.createObjectURL(file);
    }

    setupSequencePlayback() {
        if (this.images.length === 0) return;

        // Hide video, show canvas
        this.videoElement.style.display = 'none';
        this.canvas.style.display = 'block';

        // Set canvas size to first image
        const firstImage = this.images[0];
        this.canvas.width = firstImage.width;
        this.canvas.height = firstImage.height;

        // Update player state
        this.player.totalFrames = this.images.length - 1;
        this.currentIndex = 0;

        // Update UI
        document.getElementById('totalFrames').textContent = this.player.totalFrames;
        document.getElementById('resolution').textContent =
            `${firstImage.width}x${firstImage.height}`;

        // Update media info
        this.updateMediaInfo();

        // Display first frame
        this.displayFrame(0);

        // Override player controls for sequence playback
        this.setupSequenceControls();
    }

    setupSequenceControls() {
        // Override play/pause
        const playPauseBtn = document.getElementById('playPause');
        playPauseBtn.onclick = () => this.togglePlayback();

        // Override frame navigation
        document.getElementById('firstFrame').onclick = () => this.goToFrame(0);
        document.getElementById('prevFrame').onclick = () => this.previousFrame();
        document.getElementById('nextFrame').onclick = () => this.nextFrame();
        document.getElementById('lastFrame').onclick = () => this.goToFrame(this.images.length - 1);

        // FPS control
        document.getElementById('fpsInput').onchange = (e) => {
            this.fps = parseInt(e.target.value);
            if (this.isPlaying) {
                this.stopPlayback();
                this.startPlayback();
            }
        };
    }

    displayFrame(index) {
        if (index < 0 || index >= this.images.length) return;

        this.currentIndex = index;
        const img = this.images[index];

        // Clear and draw
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(img, 0, 0);

        // Update UI
        this.player.currentFrame = index;
        document.getElementById('currentFrame').textContent = index;

        // Update timeline
        if (window.timelineController) {
            const progress = index / (this.images.length - 1);
            window.timelineController.updateProgress(progress);
        }

        // Update timecode
        this.updateTimecode();
    }

    togglePlayback() {
        if (this.isPlaying) {
            this.stopPlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        this.isPlaying = true;
        const frameTime = 1000 / this.fps;

        this.playbackInterval = setInterval(() => {
            this.nextFrame();

            // Loop or stop at end
            if (this.currentIndex >= this.images.length - 1) {
                if (this.player.isLooping) {
                    this.goToFrame(0);
                } else {
                    this.stopPlayback();
                }
            }
        }, frameTime);

        // Update button
        document.getElementById('playPause').textContent = '⏸';
    }

    stopPlayback() {
        this.isPlaying = false;

        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
            this.playbackInterval = null;
        }

        // Update button
        document.getElementById('playPause').textContent = '▶';
    }

    nextFrame() {
        const nextIndex = Math.min(this.currentIndex + 1, this.images.length - 1);
        this.displayFrame(nextIndex);
    }

    previousFrame() {
        const prevIndex = Math.max(this.currentIndex - 1, 0);
        this.displayFrame(prevIndex);
    }

    goToFrame(index) {
        this.displayFrame(index);
    }

    updateTimecode() {
        const totalSeconds = this.currentIndex / this.fps;
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = Math.floor(totalSeconds % 60);
        const frames = this.currentIndex % this.fps;

        const timecode = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}:${String(frames).padStart(2, '0')}`;

        document.getElementById('timecode').textContent = timecode;
    }

    updateMediaInfo() {
        const duration = (this.images.length / this.fps).toFixed(2);
        const firstImage = this.images[0];

        const info = `
            <p><strong>Type:</strong> Image Sequence</p>
            <p><strong>Frames:</strong> ${this.images.length}</p>
            <p><strong>Duration:</strong> ${duration}s</p>
            <p><strong>Resolution:</strong> ${firstImage.width}x${firstImage.height}</p>
            <p><strong>FPS:</strong> ${this.fps}</p>
        `;

        document.getElementById('mediaInfo').innerHTML = info;
    }

    seekToPercent(percent) {
        const index = Math.floor(percent * (this.images.length - 1));
        this.goToFrame(index);
    }
}

// Initialize image sequence player when ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.horusPlayer) {
            window.imageSequencePlayer = new ImageSequencePlayer(window.horusPlayer);

            // Override player's seekToPercent for timeline scrubbing
            const originalSeekToPercent = window.horusPlayer.seekToPercent.bind(window.horusPlayer);
            window.horusPlayer.seekToPercent = function(percent) {
                if (window.imageSequencePlayer.isSequenceMode) {
                    window.imageSequencePlayer.seekToPercent(percent);
                } else {
                    originalSeekToPercent(percent);
                }
            };
        }
    }, 100);
});
