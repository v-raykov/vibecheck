<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';
import VibeForm from '../components/VibeForm.vue';
import VibeCard from '../components/VibeCard.vue';

const router = useRouter();
const vibes = ref([]);

const currentPage = ref(1);
const hasNext = ref(false);
const hasPrev = ref(false);

const loading = ref(false);
const showForm = ref(false);
const currentUser = localStorage.getItem('username');

const activeVibeId = ref(null);

const fetchVibes = async (page = 1) => {
  loading.value = true;
  try {
    const res = await api.get('/vibes/', {
      params: { page: page }
    });
    vibes.value = res.data.results || [];
    hasNext.value = !!res.data.next;
    hasPrev.value = !!res.data.previous;
    currentPage.value = page;
    activeVibeId.value = null;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const nextPage = () => {
  if (hasNext.value && !loading.value) {
    fetchVibes(currentPage.value + 1);
  }
};

const prevPage = () => {
  if (hasPrev.value && !loading.value) {
    fetchVibes(currentPage.value - 1);
  }
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  router.push('/auth');
};

const addNewVibe = (vibe) => {
  if (currentPage.value === 1) {
    vibes.value.unshift(vibe);
    // Keep it looking tight if we exceed standard view capacity on first page
    if (vibes.value.length > 6) vibes.value.pop();
  } else {
    fetchVibes(1);
  }
  showForm.value = false;
};

const handleTrackPlaybackToggle = (vibeId) => {
  if (activeVibeId.value === vibeId) {
    activeVibeId.value = null;
  } else {
    activeVibeId.value = vibeId;
  }
};

onMounted(() => {
  fetchVibes(1);
});
</script>

<template>
  <div class="feed-container">
    <header class="main-nav">
      <div class="nav-content">
        <h1 class="logo">VibeCheck</h1>

        <div class="nav-actions">
          <div class="pagination-controls">
            <button
                @click="prevPage"
                class="nav-arrow-btn"
                :disabled="!hasPrev || loading"
                title="Previous Page"
            >
              ←
            </button>
            <span class="page-indicator">Page {{ currentPage }}</span>
            <button
                @click="nextPage"
                class="nav-arrow-btn"
                :disabled="!hasNext || loading"
                title="Next Page"
            >
              →
            </button>
          </div>

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

    <main class="feed-wrapper">
      <div v-if="loading && vibes.length === 0" class="loader-state">
        <div class="spinner"></div>
      </div>

      <div v-else class="grid-scroll-container">
        <div class="vibe-grid">
          <VibeCard
              v-for="vibe in vibes"
              :key="vibe.id"
              :vibe="vibe"
              :is-mine="vibe.user === currentUser"
              :is-currently-playing="activeVibeId === vibe.id"
              @toggle-playback="handleTrackPlaybackToggle"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.feed-container {
  height: 100vh;
  width: 100vw;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Prevents global page scroll */
  box-sizing: border-box;
}

.main-nav {
  height: 70px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.nav-content {
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
  padding: 0 1rem;
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
  gap: 20px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(15, 23, 42, 0.6);
  padding: 4px 8px;
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.nav-arrow-btn {
  background: #334155;
  color: #f8fafc;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.nav-arrow-btn:hover:not(:disabled) {
  background: #475569;
  color: #6366f1;
}

.nav-arrow-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-indicator {
  color: #94a3b8;
  font-size: 0.85rem;
  font-weight: 700;
  min-width: 55px;
  text-align: center;
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

.create-trigger:hover {
  background: #4f46e5;
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

.feed-wrapper {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  box-sizing: border-box;
  min-height: 0; /* Critical structure item for nested flex box containment */
  display: flex;
  flex-direction: column;
}

.grid-scroll-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto; /* Just in case extra rows spill over on compact resolution screens */
  padding-right: 4px;
}

/* Custom minimal scrollbar styling for the inner grid box if necessary */
.grid-scroll-container::-webkit-scrollbar {
  width: 6px;
}
.grid-scroll-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.vibe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
  align-items: start;
}

.loader-state {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(99, 102, 241, 0.1);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>