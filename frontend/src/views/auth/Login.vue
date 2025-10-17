<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <h1 class="login-title">University Portal</h1>
        <p class="login-subtitle">Sign in to access your account</p>

        <div v-if="error" class="error">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="credentials.email"
              type="email"
              class="form-input"
              placeholder="your.email@university.edu"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">Password</label>
            <input
              v-model="credentials.password"
              type="password"
              class="form-input"
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="login-info">
          <p><strong>Demo Credentials:</strong></p>
          <p>Default password: <code>password123</code></p>
          <p>Use any email from students.csv, faculty_professors.csv, or staff.csv</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

const handleLogin = async () => {
  loading.value = true
  error.value = null

  try {
    await authStore.login(credentials.value)

    // Redirect based on role
    if (authStore.isStudent) {
      router.push('/dashboard')
    } else if (authStore.isFaculty) {
      router.push('/faculty/dashboard')
    } else {
      router.push('/dashboard')
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 1rem;
}

.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-title {
  font-size: 1.875rem;
  font-weight: 700;
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.login-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.btn-full {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-top: 0.5rem;
}

.login-info {
  background: var(--background-secondary);
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.login-info p {
  margin: 0.5rem 0;
}

.login-info code {
  background: white;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: monospace;
  color: var(--primary-color);
}
</style>
