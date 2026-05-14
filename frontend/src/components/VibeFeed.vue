<script setup>
import {onMounted, ref} from 'vue';
import {useRouter} from 'vue-router';
import api from '../api';
import VibeForm from '../components/VibeForm.vue';
import VibeCard from '../components/VibeCard.vue';

const router = useRouter();
const vibes = ref([]);
const nextPage = ref(null);
const loading = ref(false);
const showForm = ref(false);
const currentUser = localStorage.getItem('username');

const fetchVibes = async (url = '/vibes/') => {
  loading.value = true;
  try {
    const res = await api.get(url);
    if (url === '/vibes/') {
      vibes.value = res.data.results;
    } else {
      vibes.value.push(...res.data.results);
    }
    nextPage.value = res.data.next;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  router.push('/auth');
};

const addNewVibe = (vibe) => {
  vibes.value.unshift(vibe);
  showForm.value = false;
};

onMounted(fetchVibes);
</script>

<template>
  <div class="feed-container">
    <header class="main-nav">
      <div class="nav-content">
        <h1 class="logo">VibeCheck</h1>

        <div class="nav-actions">
          <button @click="showForm = !showForm" class="create-trigger" :class="{ active: showForm }">
            {{ showForm ? 'Close' : 'Post Vibe' }}
          </button>

          <button @click="handleLogout" class="logout-btn" title="Logout">
            <span class="icon">🚪</span>
          </button>
        </div>
      </div>
    </header>

    <Transition name="fade-slide">
      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal-content">
          <VibeForm @vibeCreated="addNewVibe" @close="showForm = false"/>
        </div>
      </div>
    </Transition>

    <main class="vibe-stack">
      <VibeCard
          v-for="vibe in vibes"
          :key="vibe.id"
          :vibe="vibe"
          :is-mine="vibe.user === currentUser"
      />

      <div v-if="nextPage" class="pagination">
        <button @click="fetchVibes(nextPage)" :disabled="loading" class="load-more-btn">
          {{ loading ? '...' : 'Show More' }}
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.feed-container {
  min-height: 100vh;
  background: #0f172a;
  padding-top: 80px;
}

.main-nav {
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  z-index: 100;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 900;
  color: #f8fafc;
  letter-spacing: -1px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.create-trigger {
  background: #6366f1;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 50px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #ef4444;
  border-color: #ef4444;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 200;
}

.modal-content {
  width: 100%;
  max-width: 450px;
  padding: 20px;
}

.vibe-stack {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.pagination {
  margin-top: 20px;
}

.load-more-btn {
  width: 100%;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #94a3b8;
  padding: 1rem;
  border-radius: 12px;
  cursor: pointer;
}

.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>