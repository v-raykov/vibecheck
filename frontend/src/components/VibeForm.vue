<script setup>
import {ref} from 'vue';
import api from '../api';
import EmojiPicker from 'vue3-emoji-picker';
import 'vue3-emoji-picker/css';

const emit = defineEmits(['vibeCreated', 'close']);
const showPicker = ref(false);
const form = ref({content: '', percentage: 50, emoji: '😎'});

const onSelectEmoji = (emoji) => {
  form.value.emoji = emoji.i;
  showPicker.value = false;
};

const submit = async () => {
  try {
    const res = await api.post('/vibes/', form.value);
    emit('vibeCreated', res.data);
  } catch (err) {
    alert("Error");
  }
};
</script>

<template>
  <div class="vibe-form-dark">
    <div class="modal-header">
      <h3>New Vibe</h3>
      <button class="close-x" @click="$emit('close')">✕</button>
    </div>

    <form @submit.prevent="submit">
      <div class="input-group">
        <button type="button" @click.stop="showPicker = !showPicker" class="picker-trigger">
          {{ form.emoji }}
        </button>
        <div v-if="showPicker" class="floating-picker">
          <EmojiPicker theme="dark" :native="true" @select="onSelectEmoji"/>
        </div>
        <div class="slider-box">
          <input v-model="form.percentage" type="range" min="0" max="100">
          <span>{{ form.percentage }}%</span>
        </div>
      </div>

      <textarea v-model="form.content" placeholder="What's happening?" required></textarea>
      <button type="submit" class="submit-btn">Post</button>
    </form>
  </div>
</template>

<style scoped>
.vibe-form-dark {
  background: #0f172a;
  padding: 1.5rem;
  border-radius: 20px;
  border: 1px solid #334155;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  color: white;
}

.close-x {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 1.2rem;
}

.input-group {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
  position: relative;
}

.picker-trigger {
  font-size: 2rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 10px;
  cursor: pointer;
}

.floating-picker {
  position: absolute;
  top: 60px;
  left: 0;
  z-index: 1000;
}

.slider-box {
  flex: 1;
  color: #94a3b8;
  font-size: 0.8rem;
}

.slider-box input {
  width: 100%;
}

textarea {
  width: 100%;
  background: #1e293b;
  border: 1px solid #334155;
  color: white;
  padding: 12px;
  border-radius: 8px;
  resize: none;
  height: 100px;
  margin-bottom: 15px;
}

.submit-btn {
  width: 100%;
  background: #6366f1;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}
</style>