import apiClient from './api'

export default {
  // Get student enrollments
  getMyEnrollments() {
    return apiClient.get('/academics/enrollments/my_enrollments/')
  },

  // Get student grades
  getMyGrades() {
    return apiClient.get('/academics/enrollments/my_grades/')
  },

  // Get courses
  getCourses(params) {
    return apiClient.get('/academics/courses/', { params })
  },

  // Get course details
  getCourse(id) {
    return apiClient.get(`/academics/courses/${id}/`)
  },

  // Get sections
  getSections(params) {
    return apiClient.get('/academics/sections/', { params })
  },

  // Get departments
  getDepartments() {
    return apiClient.get('/academics/departments/')
  },

  // Faculty: Get my sections
  getMySections() {
    return apiClient.get('/academics/sections/', { params: { my_sections: true } })
  },

  // Faculty: Get section enrollments
  getSectionEnrollments(sectionId) {
    return apiClient.get('/academics/enrollments/', { params: { section: sectionId } })
  },
}
