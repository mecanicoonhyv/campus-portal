import { defineStore } from 'pinia'
import academicsService from '@/services/academics'
import attendanceService from '@/services/attendance'
import assessmentsService from '@/services/assessments'
import libraryService from '@/services/library'
import servicesService from '@/services/services'

export const useStudentStore = defineStore('student', {
  state: () => ({
    enrollments: [],
    grades: null,
    attendance: [],
    attendanceSummary: [],
    submissions: [],
    libraryCheckouts: [],
    financialAid: null,
    parkingPermits: [],
    loading: {
      enrollments: false,
      grades: false,
      attendance: false,
      submissions: false,
      library: false,
      financialAid: false,
      parking: false,
    },
  }),

  getters: {
    currentGPA: (state) => state.grades?.gpa || 0,
    totalCredits: (state) => state.grades?.total_credits || 0,
    activeEnrollments: (state) => state.enrollments.filter(e => e.status === 'Enrolled'),
    overdueCheckouts: (state) => state.libraryCheckouts.filter(c => c.is_overdue),
  },

  actions: {
    async fetchEnrollments() {
      this.loading.enrollments = true
      try {
        const response = await academicsService.getMyEnrollments()
        this.enrollments = response.data
      } catch (error) {
        console.error('Failed to fetch enrollments:', error)
      } finally {
        this.loading.enrollments = false
      }
    },

    async fetchGrades() {
      this.loading.grades = true
      try {
        const response = await academicsService.getMyGrades()
        this.grades = response.data
      } catch (error) {
        console.error('Failed to fetch grades:', error)
      } finally {
        this.loading.grades = false
      }
    },

    async fetchAttendance() {
      this.loading.attendance = true
      try {
        const [attendanceResponse, summaryResponse] = await Promise.all([
          attendanceService.getMyAttendance(),
          attendanceService.getMyAttendanceSummary(),
        ])
        this.attendance = attendanceResponse.data
        this.attendanceSummary = summaryResponse.data
      } catch (error) {
        console.error('Failed to fetch attendance:', error)
      } finally {
        this.loading.attendance = false
      }
    },

    async fetchSubmissions() {
      this.loading.submissions = true
      try {
        const response = await assessmentsService.getMySubmissions()
        this.submissions = response.data
      } catch (error) {
        console.error('Failed to fetch submissions:', error)
      } finally {
        this.loading.submissions = false
      }
    },

    async fetchLibraryCheckouts() {
      this.loading.library = true
      try {
        const response = await libraryService.getMyCheckouts()
        this.libraryCheckouts = response.data
      } catch (error) {
        console.error('Failed to fetch library checkouts:', error)
      } finally {
        this.loading.library = false
      }
    },

    async fetchFinancialAid() {
      this.loading.financialAid = true
      try {
        const response = await servicesService.getMyFinancialAid()
        this.financialAid = response.data
      } catch (error) {
        console.error('Failed to fetch financial aid:', error)
      } finally {
        this.loading.financialAid = false
      }
    },

    async fetchParkingPermits() {
      this.loading.parking = true
      try {
        const response = await servicesService.getMyParkingPermits()
        this.parkingPermits = response.data
      } catch (error) {
        console.error('Failed to fetch parking permits:', error)
      } finally {
        this.loading.parking = false
      }
    },

    async fetchAllData() {
      await Promise.all([
        this.fetchEnrollments(),
        this.fetchGrades(),
        this.fetchAttendance(),
        this.fetchSubmissions(),
        this.fetchLibraryCheckouts(),
        this.fetchFinancialAid(),
        this.fetchParkingPermits(),
      ])
    },
  },
})
