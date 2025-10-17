<template>
  <Layout>
    <div class="sections-page">
      <h1 class="page-title">My Sections</h1>

      <div v-if="loading" class="loading">Loading sections...</div>

      <div v-else class="sections-list">
        <div v-if="sections.length === 0" class="card">
          <p>No sections assigned</p>
        </div>

        <div
          v-for="section in sections"
          :key="section.section_id"
          class="section-card card"
        >
          <div class="section-header">
            <div>
              <h2>{{ section.course_name }}</h2>
              <p class="section-code">
                {{ section.course_id }} - Section {{ section.section_number }} ({{ section.semester }})
              </p>
            </div>
            <span
              :class="{
                'badge badge-success': section.status === 'Open',
                'badge badge-danger': section.status === 'Closed',
                'badge': section.status === 'Cancelled'
              }"
            >
              {{ section.status }}
            </span>
          </div>

          <div class="section-details">
            <div class="detail-item">
              <span class="detail-label">Schedule:</span>
              <span>{{ section.meeting_days }} {{ section.meeting_time }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Room:</span>
              <span>{{ section.room_number || 'TBA' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Enrollment:</span>
              <span>{{ section.enrolled }} / {{ section.capacity }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Available Seats:</span>
              <span :class="{ 'text-danger': section.enrolled >= section.capacity }">
                {{ section.capacity - section.enrolled }}
              </span>
            </div>
          </div>

          <div class="section-actions">
            <button
              @click="viewEnrollments(section.section_id)"
              class="btn btn-primary"
            >
              View Enrollments ({{ section.enrolled }})
            </button>
            <button
              @click="manageAttendance(section.section_id)"
              class="btn btn-secondary"
            >
              Manage Attendance
            </button>
          </div>

          <!-- Enrollments Table (shown when selected) -->
          <div
            v-if="selectedSection === section.section_id"
            class="enrollments-section"
          >
            <h3>Students Enrolled</h3>
            <div v-if="loadingEnrollments" class="loading">Loading students...</div>
            <table v-else-if="enrollments.length > 0" class="table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Grade</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="enrollment in enrollments" :key="enrollment.enrollment_id">
                  <td>{{ enrollment.student_id }}</td>
                  <td>{{ enrollment.student_name }}</td>
                  <td>{{ enrollment.student_email }}</td>
                  <td>
                    <span class="badge badge-success">{{ enrollment.status }}</span>
                  </td>
                  <td>
                    <span v-if="enrollment.grade" class="badge">
                      {{ enrollment.grade }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else>No students enrolled yet</div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Layout from '@/components/layout/Layout.vue'
import academicsService from '@/services/academics'

const loading = ref(true)
const loadingEnrollments = ref(false)
const sections = ref([])
const enrollments = ref([])
const selectedSection = ref(null)

const viewEnrollments = async (sectionId) => {
  if (selectedSection.value === sectionId) {
    selectedSection.value = null
    enrollments.value = []
    return
  }

  selectedSection.value = sectionId
  loadingEnrollments.value = true

  try {
    const response = await academicsService.getSectionEnrollments(sectionId)
    enrollments.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch enrollments:', error)
  } finally {
    loadingEnrollments.value = false
  }
}

const manageAttendance = (sectionId) => {
  // Navigate to attendance management (would need attendance view)
  alert(`Attendance management for section ${sectionId} - Feature coming soon!`)
}

onMounted(async () => {
  try {
    const response = await academicsService.getMySections()
    sections.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch sections:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.sections-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.section-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.section-header h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.section-code {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
}

.section-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 600;
}

.section-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-color-dark);
}

.btn-secondary {
  background: var(--background-secondary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--border-color);
}

.enrollments-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.enrollments-section h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.text-danger {
  color: #dc3545;
}

.text-muted {
  color: var(--text-secondary);
}
</style>
