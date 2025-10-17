import apiClient from './api'

export default {
  // Get financial aid
  getMyFinancialAid() {
    return apiClient.get('/services/financial-aid/my_aid/')
  },

  // Get parking permits
  getMyParkingPermits() {
    return apiClient.get('/services/parking/my_permits/')
  },

  // Get events
  getEvents(params) {
    return apiClient.get('/services/events/', { params })
  },

  // Get upcoming events
  getUpcomingEvents() {
    return apiClient.get('/services/events/upcoming/')
  },
}
