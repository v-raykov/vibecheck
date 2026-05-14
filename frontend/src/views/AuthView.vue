<script setup>
import {ref} from 'vue';
import {useRouter} from 'vue-router';
import api from '../api';

const router = useRouter();
const isLogin = ref(true);
const error = ref('');

const form = ref({
  username: '',
  password: '',
});

const handleSubmit = async () => {
  error.value = '';
  try {
    if (isLogin.value) {
      // LOGIN
      const res = await api.post('/login/', {
        username: form.value.username,
        password: form.value.password
      });
      localStorage.setItem('access_token', res.data.access);
      localStorage.setItem('refresh_token', res.data.refresh);
      router.push('/');
    } else {
      // REGISTER
      await api.post('/register/', form.value);
      isLogin.value = true;
      alert('Account created! Please log in.');
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Something went wrong';
  }
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>{{ isLogin ? 'Login' : 'Join the Vibe' }}</h2>

      <form @submit.prevent="handleSubmit">
        <input v-model="form.username" type="text" placeholder="Username" required/>
        <input v-model="form.password" type="password" placeholder="Password" required/>

        <button type="submit" class="btn">
          {{ isLogin ? 'Sign In' : 'Create Account' }}
        </button>
      </form>

      <p v-if="error" class="error">{{ error }}</p>

      <button @click="isLogin = !isLogin" class="toggle-btn">
        {{ isLogin ? "Don't have an account? Register" : "Already have an account? Login" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

input {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.error {
  color: #e11d48;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--primary);
  margin-top: 1rem;
  cursor: pointer;
  text-decoration: underline;
}
</style>