<script setup>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue';
import api from '../api';

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  },
  moodPercentage: {
    type: Number,
    default: 50
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const searchQuery = ref('');
const tracksList = ref([]);
const isLoading = ref(false);

const selectedTrack = ref(null);
const audioEl = ref(null);
const isPlaying = ref(false);
const duration = ref(180);
const startSeconds = ref(30);
const endSeconds = ref(50);
const currentPlaybackTime = ref(30);

const sliderTrackRef = ref(null);

const fetchSuggestions = async () => {
  if (searchQuery.value.trim() || !isOpen.value) return;
  isLoading.value = true;
  try {
    const res = await api.get('/music/suggestions/', {
      params: { percentage: props.moodPercentage }
    });
    tracksList.value = res.data.tracks || [];
  } catch (err) {
    console.error("Failed fetching suggestions", err);
  } finally {
    isLoading.value = false;
  }
};

watch(isOpen, (newVal) => {
  if (newVal) fetchSuggestions();
});

let sliderDebounce = null;
watch(() => props.moodPercentage, () => {
  clearTimeout(sliderDebounce);
  sliderDebounce = setTimeout(() => {
    fetchSuggestions();
  }, 300);
});

let searchDebounce = null;
const handleSearchInput = () => {
  clearTimeout(searchDebounce);
  if (!searchQuery.value.trim()) {
    fetchSuggestions();
    return;
  }
  isLoading.value = true;
  searchDebounce = setTimeout(async () => {
    try {
      const res = await api.get('/music/search/', { params: { q: searchQuery.value } });
      tracksList.value = res.data.tracks || [];
    } catch (err) {
      console.error("Search query failed", err);
    } finally {
      isLoading.value = false;
    }
  }, 400);
};

const selectTrack = (track) => {
  selectedTrack.value = track;
  isPlaying.value = false;

  startSeconds.value = track.default_snippet?.start_seconds || 30;
  endSeconds.value = track.default_snippet?.end_seconds || 50;
  currentPlaybackTime.value = startSeconds.value;

  if (audioEl.value) audioEl.value.pause();

  audioEl.value = new Audio(track.stream_url);
  audioEl.value.preload = "metadata";

  audioEl.value.addEventListener('loadedmetadata', () => {
    duration.value = Math.floor(audioEl.value.duration) || 180;
  });

  audioEl.value.addEventListener('timeupdate', () => {
    currentPlaybackTime.value = audioEl.value.currentTime;
    if (audioEl.value.currentTime >= endSeconds.value) {
      audioEl.value.currentTime = startSeconds.value;
    }
  });

  audioEl.value.addEventListener('ended', () => {
    isPlaying.value = false;
  });

  emitPayload();
};

const togglePlayback = () => {
  if (!audioEl.value) return;
  if (isPlaying.value) {
    audioEl.value.pause();
    isPlaying.value = false;
  } else {
    if (audioEl.value.currentTime < startSeconds.value || audioEl.value.currentTime >= endSeconds.value) {
      audioEl.value.currentTime = startSeconds.value;
    }
    audioEl.value.play();
    isPlaying.value = true;
  }
};

const getSecondsFromEvent = (e) => {
  if (!sliderTrackRef.value) return 0;
  const rect = sliderTrackRef.value.getBoundingClientRect();
  const offsetX = e.clientX - rect.left;
  const percentage = Math.max(0, Math.min(1, offsetX / rect.width));
  return Math.floor(percentage * duration.value);
};

const handleTrackClick = (e) => {
  if (!audioEl.value) return;
  if (e.target.classList.contains('handle')) return;

  const clickedSeconds = getSecondsFromEvent(e);

  audioEl.value.currentTime = clickedSeconds;
  currentPlaybackTime.value = clickedSeconds;

  if (clickedSeconds < startSeconds.value) {
    startSeconds.value = clickedSeconds;
  } else if (clickedSeconds > endSeconds.value) {
    endSeconds.value = clickedSeconds;
  }

  if (!isPlaying.value) {
    audioEl.value.play();
    isPlaying.value = true;
  }
  emitPayload();
};

const initiateDrag = (targetHandle) => {
  const onMouseMove = (e) => {
    const activeSeconds = getSecondsFromEvent(e);
    if (targetHandle === 'start') {
      startSeconds.value = Math.max(0, Math.min(activeSeconds, endSeconds.value - 1));
      if (audioEl.value && audioEl.value.currentTime < startSeconds.value) {
        audioEl.value.currentTime = startSeconds.value;
      }
    } else {
      endSeconds.value = Math.max(startSeconds.value + 1, Math.min(activeSeconds, duration.value));
    }
    emitPayload();
  };

  const onMouseUp = () => {
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
};

const startPercent = computed(() => (startSeconds.value / duration.value) * 100);
const endPercent = computed(() => (endSeconds.value / duration.value) * 100);
const playheadPercent = computed(() => (currentPlaybackTime.value / duration.value) * 100);

const emitPayload = () => {
  emit('update:modelValue', {
    track_id: selectedTrack.value.track_id,
    start_seconds: startSeconds.value,
    end_seconds: endSeconds.value
  });
};

const removeTrack = () => {
  if (audioEl.value) audioEl.value.pause();
  selectedTrack.value = null;
  isPlaying.value = false;
  emit('update:modelValue', null);
};

onUnmounted(() => {
  if (audioEl.value) audioEl.value.pause();
});
</script>

<template>
  <div class="music-picker-wrapper">
    <button v-if="!isOpen && !modelValue" type="button" class="toggle-menu-btn" @click="isOpen = true">
      🎵 Add Background Music
    </button>

    <div v-if="isOpen || modelValue" class="music-menu">
      <div class="menu-header">
        <label v-if="!searchQuery.trim()">Suggested Sounds</label>
        <label v-else>Search Results</label>
        <button v-if="isOpen && !modelValue" type="button" class="close-panel-btn" @click="isOpen = false">
          Hide
        </button>
      </div>

      <div v-if="!selectedTrack" class="search-bar-container">
        <input
            v-model="searchQuery"
            type="text"
            placeholder="Search custom tracks..."
            @input="handleSearchInput"
            class="music-search-input"
        />
        <div v-if="isLoading" class="loader-status">...</div>
      </div>

      <div v-if="selectedTrack" class="attached-track-panel">
        <div class="track-meta-row">
          <img :src="selectedTrack.cover_url" alt="Cover" />
          <div class="banner-details">
            <span class="title">{{ selectedTrack.title }}</span>
            <span class="artist">{{ selectedTrack.artist }}</span>
          </div>
          <button type="button" class="play-preview-btn" @click="togglePlayback">
            {{ isPlaying ? '⏸ Pause' : '▶ Play Preview' }}
          </button>
          <button type="button" class="clear-track" @click="removeTrack">✕</button>
        </div>

        <div class="timeline-container">
          <div class="timeline-timestamps">
            <span>Trim Snippet: {{ startSeconds }}s</span>
            <span>Current: {{ Math.floor(currentPlaybackTime) }}s</span>
            <span>End: {{ endSeconds }}s</span>
          </div>

          <div class="custom-slider-track" ref="sliderTrackRef" @mousedown="handleTrackClick">
            <div
                class="active-highlight-bar"
                :style="{ left: startPercent + '%', width: (endPercent - startPercent) + '%' }"
            ></div>

            <div
                class="live-playhead-needle"
                :style="{ left: playheadPercent + '%' }"
            ></div>

            <div
                class="handle start-handle"
                :style="{ left: startPercent + '%' }"
                @mousedown.stop.prevent="initiateDrag('start')"
            ></div>

            <div
                class="handle end-handle"
                :style="{ left: endPercent + '%' }"
                @mousedown.stop.prevent="initiateDrag('end')"
            ></div>
          </div>
          <div class="window-duration-badge">{{ endSeconds - startSeconds }}s snippet window</div>
        </div>
      </div>

      <div v-if="!selectedTrack" class="tracks-scroll-container">
        <div v-for="track in tracksList" :key="track.track_id" class="track-item-row" @click="selectTrack(track)">
          <img :src="track.cover_url" alt="Cover" class="row-thumb" />
          <div class="row-meta">
            <span class="row-title">{{ track.title }}</span>
            <span class="row-artist">{{ track.artist }}</span>
          </div>
        </div>
        <div v-if="!isLoading && !tracksList.length" class="empty-results">No tracks found</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toggle-menu-btn {
  width: 100%;
  background: #1e293b;
  border: 1px dashed #475569;
  color: #94a3b8;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 15px;
}
.toggle-menu-btn:hover {
  border-color: #6366f1;
  color: white;
}
.music-menu {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 20px;
}
.menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.music-menu label {
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}
.close-panel-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 0.75rem;
}
.search-bar-container {
  position: relative;
  margin-bottom: 10px;
}
.music-search-input {
  width: 100%;
  background: #0f172a;
  border: 1px solid #334155;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 0.85rem;
}
.music-search-input:focus {
  outline: none;
  border-color: #6366f1;
}
.loader-status {
  position: absolute;
  right: 12px;
  top: 8px;
  color: #64748b;
}
.attached-track-panel {
  background: #0f172a;
  border: 1px solid #6366f1;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 5px;
}
.track-meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid #1e293b;
}
.track-meta-row img {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  object-fit: cover;
}
.banner-details {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.banner-details .title {
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
}
.banner-details .artist {
  color: #94a3b8;
  font-size: 0.75rem;
}
.play-preview-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.clear-track {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 5px;
}
.timeline-timestamps {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 0.75rem;
}
.custom-slider-track {
  position: relative;
  height: 8px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 4px;
  cursor: pointer;
  margin: 12px 0;
}
.active-highlight-bar {
  position: absolute;
  height: 100%;
  background: rgba(99, 102, 241, 0.3);
  border-radius: 4px;
}

/* Instagram Live Scanning Needle Style */
.live-playhead-needle {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 3px;
  background: #38bdf8; /* Bright distinctive neon blue tint */
  border-radius: 2px;
  transform: translateX(-50%);
  pointer-events: none; /* Make clicks fall straight through it to the track */
  z-index: 4;
  box-shadow: 0 0 8px #38bdf8;
}

.handle {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  background: #ffffff;
  border: 3px solid #6366f1;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: ew-resize;
  z-index: 5;
  box-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.window-duration-badge {
  text-align: right;
  font-size: 0.7rem;
  color: #6366f1;
  font-weight: 600;
}

.tracks-scroll-container {
  max-height: 140px;
  overflow-y: auto;
}
.track-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
}
.track-item-row:hover {
  background: #334155;
}
.row-thumb {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  object-fit: cover;
}
.row-meta {
  display: flex;
  flex-direction: column;
}
.row-title {
  color: white;
  font-size: 0.8rem;
}
.row-artist {
  color: #94a3b8;
  font-size: 0.7rem;
}
.empty-results {
  text-align: center;
  color: #64748b;
  font-size: 0.8rem;
  padding: 15px 0;
}
</style>