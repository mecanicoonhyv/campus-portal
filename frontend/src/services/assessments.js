import apiClient from './api'

export default {
  // Get assignments
  getAssignments(params) {
    return apiClient.get('/assessments/assignments/', { params })
  },

  // Get student submissions
  getMySubmissions() {
    return apiClient.get('/assessments/submissions/my_submissions/')
  },

  // Faculty: Get submissions for assignment
  getSubmissions(params) {
    return apiClient.get('/assessments/submissions/', { params })
  },

  // Faculty: Create assignment
  createAssignment(data) {
    return apiClient.post('/assessments/assignments/', data)
  },

  // Faculty: Grade submission
  gradeSubmission(id, data) {
    return apiClient.patch(`/assessments/submissions/${id}/grade/`, data)
  },
}
