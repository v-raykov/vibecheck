<script setup>
import {computed, ref} from 'vue';
import api from '../api';

const props = defineProps(['vibe', 'isMine']);

const localLikes = ref(Number(props.vibe.likes_count) || 0);
const isLiked = ref(!!props.vibe.is_liked);

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
    <div class="vibe-main">
      <div class="emoji-box">
        <span class="vibe-emoji">{{ vibe.emoji }}</span>
      </div>
      <div class="content-box">
        <div class="meta-row">
          <span class="user">@{{ vibe.user }}</span>
          <span class="intensity">{{ vibe.percentage }}%</span>
        </div>
        <p class="text">{{ vibe.content }}</p>
      </div>
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
  padding: 1rem;
  width: 100%;
}

.mine {
  border-color: #6366f1;
}

.vibe-main {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.vibe-emoji {
  font-size: 2.2rem;
}

.content-box {
  flex: 1;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.user {
  font-weight: 700;
  color: #94a3b8;
  font-size: 0.85rem;
}

.intensity {
  color: #6366f1;
  font-weight: 800;
  font-size: 0.85rem;
}

.text {
  color: #f8fafc;
  font-size: 1rem;
  line-height: 1.4;
  word-break: break-word;
}

.vibe-actions {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 0.75rem;
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
  transform: scale(1.2);
}

.label {
  color: #94a3b8;
  font-size: 0.8rem;
}

.active .label {
  color: #f8fafc;
  font-weight: 600;
}
</style>