/**
 * Horus Web Player - Timeline Controller
 * Frame-accurate timeline with scrubbing and markers
 */

class TimelineController {
    constructor(player) {
        this.player = player;
        this.track = document.getElementById('timelineTrack');
        this.progress = document.getElementById('timelineProgress');
        this.scrubber = document.getElementById('timelineScrubber');
        this.markers = document.getElementById('timelineMarkers');
        this.ruler = document.getElementById('timelineRuler');

        this.isDragging = false;
        this.duration = 0;

        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Timeline click to seek
        this.track.addEventListener('mousedown', (e) => {
            this.startDragging(e);
        });

        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.drag(e);
            }
        });

        document.addEventListener('mouseup', () => {
            this.stopDragging();
        });

        // Scrubber dragging
        this.scrubber.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            this.startDragging(e);
        });
    }

    startDragging(e) {
        this.isDragging = true;
        this.drag(e);
    }

    drag(e) {
        const rect = this.track.getBoundingClientRect();
        const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const percent = x / rect.width;

        this.updateProgress(percent);
        this.player.seekToPercent(percent);
    }

    stopDragging() {
        this.isDragging = false;
    }

    setDuration(duration) {
        this.duration = duration;
        this.updateRuler();
    }

    updateProgress(percent) {
        const clampedPercent = Math.max(0, Math.min(1, percent));
        this.progress.style.width = `${clampedPercent * 100}%`;
        this.scrubber.style.left = `${clampedPercent * 100}%`;
    }

    updateRuler() {
        // Clear existing ruler marks
        this.ruler.innerHTML = '';

        // Add time markers every 10% of duration
        for (let i = 0; i <= 10; i++) {
            const mark = document.createElement('span');
            const time = (this.duration / 10) * i;
            const seconds = Math.floor(time);
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;

            mark.textContent = `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
            mark.style.position = 'absolute';
            mark.style.left = `${i * 10}%`;
            mark.style.transform = 'translateX(-50%)';

            this.ruler.appendChild(mark);
        }
    }

    addMarker(marker) {
        const markerElement = document.createElement('div');
        markerElement.className = 'timeline-marker';
        markerElement.style.left = `${(marker.time / this.duration) * 100}%`;
        markerElement.title = marker.label;

        markerElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.player.seekToTime(marker.time);
        });

        this.markers.appendChild(markerElement);
    }

    clearMarkers() {
        this.markers.innerHTML = '';
    }
}

// Initialize timeline controller when player is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for player to be initialized
    setTimeout(() => {
        if (window.horusPlayer) {
            window.timelineController = new TimelineController(window.horusPlayer);
        }
    }, 100);
});
