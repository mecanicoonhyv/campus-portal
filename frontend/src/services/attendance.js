import apiClient from './api'

export default {
  // Get student attendance
  getMyAttendance() {
    return apiClient.get('/attendance/records/my_attendance/')
  },

  // Get attendance summary
  getMyAttendanceSummary() {
    return apiClient.get('/attendance/records/my_summary/')
  },

  // Faculty: Mark attendance
  markAttendance(data) {
    return apiClient.post('/attendance/records/', data)
  },

  // Faculty: Update attendance
  updateAttendance(id, data) {
    return apiClient.patch(`/attendance/records/${id}/`, data)
  },
}
