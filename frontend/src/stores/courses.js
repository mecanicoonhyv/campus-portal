import { defineStore } from 'pinia'
import academicsService from '@/services/academics'

export const useCourseStore = defineStore('courses', {
  state: () => ({
    courses: [],
    selectedCourse: null,
    departments: [],
    sections: [],
    loading: false,
  }),

  actions: {
    async fetchCourses(params = {}) {
      this.loading = true
      try {
        const response = await academicsService.getCourses(params)
        this.courses = response.data.results || response.data
      } catch (error) {
        console.error('Failed to fetch courses:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchDepartments() {
      try {
        const response = await academicsService.getDepartments()
        this.departments = response.data
      } catch (error) {
        console.error('Failed to fetch departments:', error)
      }
    },

    async fetchSections(params = {}) {
      this.loading = true
      try {
        const response = await academicsService.getSections(params)
        this.sections = response.data.results || response.data
      } catch (error) {
        console.error('Failed to fetch sections:', error)
      } finally {
        this.loading = false
      }
    },
  },
})
