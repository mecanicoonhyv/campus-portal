<template>
  <Layout>
    <div class="attendance-page">
      <h1 class="page-title">My Attendance</h1>

      <div v-if="loading" class="loading">Loading attendance...</div>

      <div v-else>
        <!-- Attendance Summary -->
        <div class="card">
          <h2>Attendance Summary by Course</h2>
          <div v-if="studentStore.attendanceSummary.length === 0">
            No attendance records
          </div>
          <div v-else class="attendance-summary-list">
            <div
              v-for="summary in studentStore.attendanceSummary"
              :key="summary.section_id"
              class="summary-item"
            >
              <div class="summary-info">
                <h3>{{ summary.course_name }}</h3>
                <div class="summary-stats">
                  <span>Present: {{ summary.present }}</span>
                  <span>Absent: {{ summary.absent }}</span>
                  <span>Late: {{ summary.late }}</span>
                  <span>Excused: {{ summary.excused }}</span>
                  <span>Total: {{ summary.total_classes }}</span>
                </div>
              </div>
              <div class="summary-percentage">
                <span
                  :class="{
                    'badge badge-large badge-success': summary.attendance_percentage >= 80,
                    'badge badge-large badge-warning': summary.attendance_percentage >= 70 && summary.attendance_percentage < 80,
                    'badge badge-large badge-danger': summary.attendance_percentage < 70
                  }"
                >
                  {{ summary.attendance_percentage.toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Detailed Records -->
        <div class="card">
          <h2>Recent Attendance Records</h2>
          <div v-if="recentRecords.length === 0">
            No recent attendance records
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Course</th>
                <th>Status</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in recentRecords" :key="record.record_id">
                <td>{{ formatDate(record.date) }}</td>
                <td>{{ record.course_name }}</td>
                <td>
                  <span
                    :class="{
                      'badge badge-success': record.status === 'Present',
                      'badge badge-warning': record.status === 'Late',
                      'badge': record.status === 'Excused',
                      'badge badge-danger': record.status === 'Absent'
                    }"
                  >
                    {{ record.status }}
                  </span>
                </td>
                <td>{{ record.notes || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useStudentStore } from '@/stores/student'
import Layout from '@/components/layout/Layout.vue'
import { format } from 'date-fns'

const studentStore = useStudentStore()
const loading = ref(true)

const recentRecords = computed(() => {
  return studentStore.attendance.slice(0, 20)
})

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

onMounted(async () => {
  await studentStore.fetchAttendance()
  loading.value = false
})
</script>

<style scoped>
.attendance-summary-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: var(--background-secondary);
  border-radius: 0.5rem;
}

.summary-info h3 {
  font-size: 1.125rem;
  margin-bottom: 0.75rem;
}

.summary-stats {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.badge-large {
  font-size: 1.25rem;
  padding: 0.5rem 1rem;
}
</style>
