import apiClient from './api'

export default {
  // Get books
  getBooks(params) {
    return apiClient.get('/library/books/', { params })
  },

  // Get student checkouts
  getMyCheckouts() {
    return apiClient.get('/library/checkouts/my_checkouts/')
  },

  // Get active checkouts
  getActiveCheckouts() {
    return apiClient.get('/library/checkouts/active/')
  },
}
