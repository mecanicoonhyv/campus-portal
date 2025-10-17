<template>
  <header class="header">
    <div class="header-content">
      <div class="header-left">
        <h1 class="header-title">University Portal</h1>
      </div>
      <div class="header-right">
        <span class="user-info">{{ authStore.userFullName }}</span>
        <span class="user-role badge badge-primary">{{ authStore.userRole }}</span>
        <button @click="handleLogout" class="btn btn-sm">Logout</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background: white;
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  font-weight: 500;
}

.badge-primary {
  background: var(--primary-color);
  color: white;
  text-transform: capitalize;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}
</style>
