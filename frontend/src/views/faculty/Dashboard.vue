<template>
  <Layout>
    <div class="faculty-dashboard">
      <h1 class="page-title">Faculty Dashboard</h1>

      <div v-if="loading" class="loading">Loading dashboard...</div>

      <div v-else class="dashboard-grid">
        <!-- Overview Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Active Sections</h3>
            <p class="stat-value">{{ sections.length }}</p>
          </div>

          <div class="stat-card">
            <h3>Total Students</h3>
            <p class="stat-value">{{ totalStudents }}</p>
          </div>

          <div class="stat-card">
            <h3>Total Assignments</h3>
            <p class="stat-value">{{ totalAssignments }}</p>
          </div>

          <div class="stat-card">
            <h3>Pending Submissions</h3>
            <p class="stat-value">{{ pendingSubmissions }}</p>
          </div>
        </div>

        <!-- Current Sections -->
        <div class="card">
          <h2>My Sections</h2>
          <div v-if="sections.length === 0">
            No sections assigned
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Course</th>
                <th>Section</th>
                <th>Semester</th>
                <th>Schedule</th>
                <th>Enrolled</th>
                <th>Capacity</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="section in sections" :key="section.section_id">
                <td>
                  <strong>{{ section.course_id }}</strong>
                  <br />
                  <small>{{ section.course_name }}</small>
                </td>
                <td>{{ section.section_number }}</td>
                <td>{{ section.semester }}</td>
                <td>{{ section.meeting_days }} {{ section.meeting_time }}</td>
                <td>{{ section.enrolled }}</td>
                <td>{{ section.capacity }}</td>
                <td>
                  <span
                    :class="{
                      'badge badge-success': section.status === 'Open',
                      'badge badge-danger': section.status === 'Closed',
                      'badge': section.status === 'Cancelled'
                    }"
                  >
                    {{ section.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Recent Assignments -->
        <div class="card">
          <h2>Recent Assignments</h2>
          <div v-if="assignments.length === 0">
            No assignments created yet
          </div>
          <div v-else class="assignments-list">
            <div
              v-for="assignment in assignments.slice(0, 5)"
              :key="assignment.assignment_id"
              class="assignment-item"
            >
              <div>
                <strong>{{ assignment.title }}</strong>
                <p>{{ assignment.course_name }} - Due: {{ formatDate(assignment.due_date) }}</p>
              </div>
              <div class="assignment-stats">
                <span class="badge">{{ assignment.type }}</span>
                <span class="badge badge-warning">{{ assignment.total_points }} pts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import Layout from '@/components/layout/Layout.vue'
import academicsService from '@/services/academics'
import assessmentsService from '@/services/assessments'
import { format } from 'date-fns'

const loading = ref(true)
const sections = ref([])
const assignments = ref([])
const submissions = ref([])

const totalStudents = computed(() => {
  return sections.value.reduce((sum, section) => sum + section.enrolled, 0)
})

const totalAssignments = computed(() => {
  return assignments.value.length
})

const pendingSubmissions = computed(() => {
  return submissions.value.filter(s => s.status === 'Submitted').length
})

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

onMounted(async () => {
  try {
    // Fetch faculty sections
    const sectionsResponse = await academicsService.getMySections()
    sections.value = sectionsResponse.data.results || sectionsResponse.data

    // Fetch assignments (filter by faculty sections)
    const assignmentsResponse = await assessmentsService.getAssignments()
    assignments.value = assignmentsResponse.data.results || assignmentsResponse.data

    // Fetch submissions for grading
    const submissionsResponse = await assessmentsService.getSubmissions()
    submissions.value = submissionsResponse.data.results || submissionsResponse.data
  } catch (error) {
    console.error('Failed to fetch faculty dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: var(--text-primary);
}

.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
}

.assignments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.assignment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-secondary);
  border-radius: 0.375rem;
}

.assignment-item strong {
  display: block;
  margin-bottom: 0.25rem;
}

.assignment-item p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.assignment-stats {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>
