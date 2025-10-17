import { defineStore } from 'pinia'
import authService from '@/services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    loading: false,
    error: null,
  }),

  getters: {
    isStudent: (state) => state.user?.role === 'student',
    isFaculty: (state) => state.user?.role === 'faculty',
    isStaff: (state) => state.user?.role === 'staff',
    isAdmin: (state) => state.user?.role === 'admin',
    userRole: (state) => state.user?.role || null,
    userFullName: (state) => {
      if (!state.user) return ''
      return `${state.user.first_name} ${state.user.last_name}`
    },
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        const response = await authService.login(credentials)
        const { access, refresh } = response.data

        // Store tokens
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        this.accessToken = access
        this.refreshToken = refresh
        this.isAuthenticated = true

        // Fetch user profile
        await this.fetchUserProfile()

        this.loading = false
        return true
      } catch (error) {
        this.loading = false
        this.error = error.response?.data?.detail || 'Login failed'
        throw error
      }
    },

    async fetchUserProfile() {
      try {
        const response = await authService.getCurrentUser()
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))

        // Fetch role-specific profile
        if (this.isStudent) {
          const studentResponse = await authService.getStudentProfile()
          this.user.student_profile = studentResponse.data
          localStorage.setItem('user', JSON.stringify(this.user))
        } else if (this.isFaculty) {
          const facultyResponse = await authService.getFacultyProfile()
          this.user.faculty_profile = facultyResponse.data
          localStorage.setItem('user', JSON.stringify(this.user))
        } else if (this.isStaff) {
          const staffResponse = await authService.getStaffProfile()
          this.user.staff_profile = staffResponse.data
          localStorage.setItem('user', JSON.stringify(this.user))
        }
      } catch (error) {
        console.error('Failed to fetch user profile:', error)
      }
    },

    logout() {
      // Clear tokens and user data
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.isAuthenticated = false
    },

    checkAuth() {
      const token = localStorage.getItem('access_token')
      const user = localStorage.getItem('user')

      if (token && user) {
        this.accessToken = token
        this.refreshToken = localStorage.getItem('refresh_token')
        this.user = JSON.parse(user)
        this.isAuthenticated = true
      } else {
        this.logout()
      }
    },
  },
})
