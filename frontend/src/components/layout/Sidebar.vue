<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <template v-if="authStore.isStudent">
        <RouterLink to="/dashboard" class="nav-item">
          <span>📊</span> Dashboard
        </RouterLink>
        <RouterLink to="/courses" class="nav-item">
          <span>📚</span> My Courses
        </RouterLink>
        <RouterLink to="/grades" class="nav-item">
          <span>🎓</span> Grades
        </RouterLink>
        <RouterLink to="/attendance" class="nav-item">
          <span>📅</span> Attendance
        </RouterLink>
        <RouterLink to="/library" class="nav-item">
          <span>📖</span> Library
        </RouterLink>
        <RouterLink to="/financial-aid" class="nav-item">
          <span>💰</span> Financial Aid
        </RouterLink>
      </template>

      <template v-if="authStore.isFaculty">
        <RouterLink to="/faculty/dashboard" class="nav-item">
          <span>📊</span> Dashboard
        </RouterLink>
        <RouterLink to="/faculty/sections" class="nav-item">
          <span>📚</span> My Sections
        </RouterLink>
        <RouterLink to="/faculty/assignments" class="nav-item">
          <span>📝</span> Assignments
        </RouterLink>
      </template>

      <div class="nav-divider"></div>

      <RouterLink to="/catalog" class="nav-item">
        <span>🔍</span> Course Catalog
      </RouterLink>
      <RouterLink to="/events" class="nav-item">
        <span>🎉</span> Events
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid var(--border-color);
  padding: 1.5rem 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--background-secondary);
  color: var(--primary-color);
}

.nav-item.router-link-active {
  background: var(--background-secondary);
  color: var(--primary-color);
  font-weight: 600;
  border-right: 3px solid var(--primary-color);
}

.nav-divider {
  height: 1px;
  background: var(--border-color);
  margin: 1rem 1.5rem;
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }

  .nav-item span:last-child {
    display: none;
  }
}
</style>
