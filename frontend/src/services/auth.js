import apiClient from './api'

export default {
  // Login
  login(credentials) {
    return apiClient.post('/auth/login/', credentials)
  },

  // Refresh token
  refreshToken(refresh) {
    return apiClient.post('/auth/refresh/', { refresh })
  },

  // Get current user
  getCurrentUser() {
    return apiClient.get('/users/me/')
  },

  // Get student profile
  getStudentProfile() {
    return apiClient.get('/users/students/me/')
  },

  // Get faculty profile
  getFacultyProfile() {
    return apiClient.get('/users/faculty/me/')
  },

  // Get staff profile
  getStaffProfile() {
    return apiClient.get('/users/staff/me/')
  },
}
