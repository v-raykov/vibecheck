<script setup>
import {onMounted, onUnmounted, ref} from 'vue';
import api from '../api';
import EmojiPicker from 'vue3-emoji-picker';
import SongPicker from './SongPicker.vue';
import 'vue3-emoji-picker/css';

const emit = defineEmits(['vibeCreated', 'close']);

const showPicker = ref(false);
const pickerContainer = ref(null);
const musicData = ref(null);

const form = ref({
  content: '',
  percentage: 50,
  emoji: '😎'
});

const onSelectEmoji = (emoji) => {
  form.value.emoji = emoji.i;
  showPicker.value = false;
};

const handleClickOutside = (event) => {
  if (pickerContainer.value && !pickerContainer.value.contains(event.target)) {
    showPicker.value = false;
  }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));

const submit = async () => {
  try {
    const payload = {
      ...form.value,
      track_id: musicData.value?.track_id || null,
      start_seconds: musicData.value?.start_seconds || null,
      end_seconds: musicData.value?.end_seconds || null
    };

    const res = await api.post('/vibes/', payload);
    emit('vibeCreated', res.data);
  } catch (err) {
    alert("Error creating vibe");
  }
};
</script>

<template>
  <div class="vibe-form-dark">
    <div class="modal-header">
      <h3>Create New Vibe</h3>
      <button class="close-x" @click="$emit('close')">✕</button>
    </div>

    <form @submit.prevent="submit">
      <div class="input-group" ref="pickerContainer">
        <button type="button" @click.stop="showPicker = !showPicker" class="picker-trigger">
          {{ form.emoji }}
        </button>

        <div v-if="showPicker" class="floating-picker">
          <EmojiPicker theme="dark" :native="true" @select="onSelectEmoji"/>
        </div>

        <div class="slider-box">
          <div class="slider-label-row">
            <span>Mood Context</span>
            <span class="percentage-display">{{ form.percentage }}%</span>
          </div>
          <input v-model.number="form.percentage" type="range" min="0" max="100">
        </div>
      </div>

      <textarea
          v-model="form.content"
          placeholder="What's on your mind? Set the tone..."
      ></textarea>

      <SongPicker
          v-model="musicData"
          :mood-percentage="form.percentage"
      />

      <button type="submit" class="submit-btn">Publish Vibe</button>
    </form>
  </div>
</template>

<style scoped>
.vibe-form-dark {
  background: #0f172a;
  padding: 2.25rem;
  border-radius: 24px;
  border: 1px solid #334155;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  box-sizing: border-box;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.close-x {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.5rem;
  transition: color 0.2s;
}

.close-x:hover {
  color: #f1f5f9;
}

.input-group {
  display: flex;
  gap: 24px;
  align-items: center;
  margin-bottom: 2rem;
  position: relative;
}

.picker-trigger {
  font-size: 2.5rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 14px;
  cursor: pointer;
  line-height: 1;
  transition: transform 0.2s, border-color 0.2s;
}

.picker-trigger:hover {
  transform: scale(1.04);
  border-color: #475569;
}

.floating-picker {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  z-index: 1000;
}

.slider-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.slider-label-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 0.95rem;
  font-weight: 600;
}

.percentage-display {
  color: #6366f1;
  font-weight: 700;
}

.slider-box input[type="range"] {
  width: 100%;
  height: 8px;
  cursor: pointer;
}

textarea {
  width: 100%;
  background: #1e293b;
  border: 1px solid #334155;
  color: white;
  padding: 18px;
  border-radius: 12px;
  resize: none;
  height: 140px;
  margin-bottom: 2rem;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 1.1rem;
  line-height: 1.5;
}

textarea:focus {
  outline: none;
  border-color: #6366f1;
  background: #1e293b;
}

.submit-btn {
  width: 100%;
  background: #6366f1;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.submit-btn:hover {
  background: #4f46e5;
}

.submit-btn:active {
  transform: scale(0.99);
}
</style>