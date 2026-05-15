<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import api from '../api';

const props = defineProps(['vibe', 'isMine']);

const localLikes = ref(Number(props.vibe.likes_count) || 0);
const isLiked = ref(!!props.vibe.is_liked);

const audioEl = ref(null);
const isPlaying = ref(false);
const trackDetails = ref(null);

onMounted(async () => {
  if (props.vibe.track_id) {
    try {
      const res = await api.get('/music/details/', {
        params: { track_id: props.vibe.track_id }
      });
      trackDetails.value = res.data;
    } catch (err) {
      console.error("Failed fetching track details", err);
    }
  }
});

const handleLike = async () => {
  try {
    const res = await api.post(`/vibes/${props.vibe.id}/like/`);

    if (res.data && typeof res.data.likes_count !== 'undefined') {
      localLikes.value = Number(res.data.likes_count);
    }

    isLiked.value = !isLiked.value;
  } catch (err) {
    if (err.response?.status === 400) {
      alert("You cannot vibe with your own post.");
    }
    console.error(err);
  }
};

const toggleSnippet = () => {
  if (!props.vibe.track_id) return;

  if (!audioEl.value) {
    const streamUrl = trackDetails.value?.stream_url || `https://data.freetouse.com/music/tracks/${props.vibe.track_id}/file/mp3/file.mp3`;
    audioEl.value = new Audio(streamUrl);
    audioEl.value.preload = "metadata";

    audioEl.value.addEventListener('timeupdate', () => {
      if (audioEl.value.currentTime >= props.vibe.snippet_end) {
        audioEl.value.pause();
        audioEl.value.currentTime = props.vibe.snippet_start;
        isPlaying.value = false;
      }
    });

    audioEl.value.addEventListener('ended', () => {
      isPlaying.value = false;
    });
  }

  if (isPlaying.value) {
    audioEl.value.pause();
    isPlaying.value = false;
  } else {
    if (
        audioEl.value.currentTime < props.vibe.snippet_start ||
        audioEl.value.currentTime >= props.vibe.snippet_end
    ) {
      audioEl.value.currentTime = props.vibe.snippet_start;
    }
    audioEl.value.play();
    isPlaying.value = true;
  }
};

onUnmounted(() => {
  if (audioEl.value) {
    audioEl.value.pause();
  }
});

const likeText = computed(() => {
  const count = localLikes.value;

  if (props.isMine) {
    const verb = count === 1 ? 'person is' : 'people are';
    return `${count} ${verb} vibing with you`;
  }

  if (isLiked.value) {
    const others = count - 1;
    if (others <= 0) {
      return `You are vibing with this`;
    }
    const verb = others === 1 ? 'other person is' : 'other people are';
    return `You and ${others} ${verb} vibing with this`;
  }

  if (count === 0) {
    return `0 people are vibing with this`;
  }

  const verb = count === 1 ? 'person vibes' : 'people are vibing';
  return `${count} ${verb} with this`;
});
</script>

<template>
  <div class="vibe-card" :class="{ 'mine': isMine }">
    <div class="user-row">
      <span class="user">{{ vibe.user }}</span>
    </div>

    <div class="media-row">
      <div class="emoji-wrapper">
        <span class="vibe-emoji">{{ vibe.emoji }}</span>
      </div>

      <div v-if="vibe.track_id" class="player-wrapper">
        <button type="button" class="inline-play-btn" @click="toggleSnippet">
          {{ isPlaying ? '❚❚' : '▶' }}
        </button>

        <img
            v-if="trackDetails?.cover_url"
            :src="trackDetails.cover_url"
            alt="Cover"
            class="track-cover"
        />
        <div v-else class="track-cover-placeholder"></div>

        <div class="track-info">
          <span class="track-title">{{ trackDetails?.title || 'Loading track...' }}</span>
          <span class="track-artist">{{ trackDetails?.artist || vibe.track_id.slice(0, 8) }}</span>
        </div>
      </div>
    </div>

    <div v-if="vibe.content" class="content-row">
      <p class="text">{{ vibe.content }}</p>
    </div>

    <div class="vibe-actions">
      <button @click="handleLike" class="fire-btn" :class="{ active: isLiked }">
        <span class="fire-icon">🔥</span>
        <span class="label">{{ likeText }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.vibe-card {
  background: #1e293b;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 1.25rem;
  width: 100%;
  max-width: 580px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-sizing: border-box;
}

.mine {
  border-color: #6366f1;
}

.user-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user {
  font-weight: 700;
  color: #94a3b8;
  font-size: 1rem;
}

.media-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.emoji-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.vibe-emoji {
  font-size: 2.5rem;
  line-height: 1;
}

.player-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(15, 23, 42, 0.6);
  padding: 6px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  flex: 1;
  min-width: 0;
}

.inline-play-btn {
  background: #6366f1;
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.inline-play-btn:hover {
  background: #4f46e5;
}

.track-cover {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}

.track-cover-placeholder {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  background: #334155;
  flex-shrink: 0;
}

.track-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.track-title {
  color: #f8fafc;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  color: #64748b;
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.content-row {
  margin-top: 2px;
}

.text {
  color: #f8fafc;
  font-size: 1.05rem;
  line-height: 1.4;
  word-break: break-word;
  margin: 0;
}

.vibe-actions {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
  margin-top: 4px;
}

.fire-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  outline: none;
}

.fire-icon {
  font-size: 1.2rem;
  filter: grayscale(1) opacity(0.4);
  transition: all 0.2s ease;
}

.fire-btn.active .fire-icon {
  filter: grayscale(0) opacity(1);
  transform: scale(1.15);
}

.label {
  color: #94a3b8;
  font-size: 0.85rem;
}

.active .label {
  color: #f8fafc;
  font-weight: 600;
}
</style>