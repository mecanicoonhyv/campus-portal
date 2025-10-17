<template>
  <Layout>
    <div class="dashboard">
      <h1 class="page-title">Student Dashboard</h1>

      <div v-if="loading" class="loading">Loading dashboard...</div>

      <div v-else class="dashboard-grid">
        <!-- Overview Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Current GPA</h3>
            <p class="stat-value">{{ studentStore.currentGPA.toFixed(2) }}</p>
          </div>

          <div class="stat-card">
            <h3>Total Credits</h3>
            <p class="stat-value">{{ studentStore.totalCredits }}</p>
          </div>

          <div class="stat-card">
            <h3>Active Courses</h3>
            <p class="stat-value">{{ studentStore.activeEnrollments.length }}</p>
          </div>

          <div class="stat-card">
            <h3>Library Books</h3>
            <p class="stat-value">{{ activeCheckouts }}</p>
          </div>
        </div>

        <!-- Current Courses -->
        <div class="card">
          <h2>Current Enrollments</h2>
          <div v-if="studentStore.activeEnrollments.length === 0">
            No active enrollments
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Course</th>
                <th>Section</th>
                <th>Instructor</th>
                <th>Schedule</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="enrollment in studentStore.activeEnrollments" :key="enrollment.enrollment_id">
                <td>{{ enrollment.course_name }}</td>
                <td>{{ enrollment.section_number }}</td>
                <td>{{ enrollment.instructor_name }}</td>
                <td>{{ enrollment.meeting_days }} {{ enrollment.meeting_time }}</td>
                <td>
                  <span v-if="enrollment.grade" class="badge badge-success">
                    {{ enrollment.grade }}
                  </span>
                  <span v-else class="badge">In Progress</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Attendance Summary -->
        <div class="card">
          <h2>Attendance Summary</h2>
          <div v-if="studentStore.attendanceSummary.length === 0">
            No attendance records
          </div>
          <div v-else class="attendance-list">
            <div
              v-for="summary in studentStore.attendanceSummary"
              :key="summary.section_id"
              class="attendance-item"
            >
              <div>
                <strong>{{ summary.course_name }}</strong>
                <p>{{ summary.present }}/{{ summary.total_classes }} classes attended</p>
              </div>
              <div class="attendance-percentage">
                <span
                  :class="{
                    'badge badge-success': summary.attendance_percentage >= 80,
                    'badge badge-warning': summary.attendance_percentage >= 70 && summary.attendance_percentage < 80,
                    'badge badge-danger': summary.attendance_percentage < 70
                  }"
                >
                  {{ summary.attendance_percentage.toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useStudentStore } from '@/stores/student'
import Layout from '@/components/layout/Layout.vue'

const studentStore = useStudentStore()
const loading = ref(true)

const activeCheckouts = computed(() => {
  return studentStore.libraryCheckouts.filter(c => c.status === 'Active').length
})

onMounted(async () => {
  await studentStore.fetchAllData()
  loading.value = false
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

.attendance-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.attendance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--background-secondary);
  border-radius: 0.375rem;
}

.attendance-item strong {
  display: block;
  margin-bottom: 0.25rem;
}

.attendance-item p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}
</style>
