import { createRouter, createWebHistory } from 'vue-router'
import VibeFeed from '../components/VibeFeed.vue'
import AuthView from '../views/AuthView.vue'

const routes = [
    {
        path: '/',
        name: 'feed',
        component: VibeFeed,
        meta: { requiresAuth: true }
    },
    {
        path: '/auth',
        name: 'auth',
        component: AuthView,
        meta: { requiresAuth: false }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to) => {
    const token = localStorage.getItem('access_token')

    if (to.meta.requiresAuth && !token) {
        return { name: 'auth' }
    }

    if (to.name === 'auth' && token) {
        return { name: 'feed' }
    }

})

export default router