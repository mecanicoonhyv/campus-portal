<template>
  <Layout>
    <div class="courses-page">
      <h1 class="page-title">My Courses</h1>

      <div v-if="loading" class="loading">Loading courses...</div>

      <div v-else class="courses-list">
        <div v-if="studentStore.activeEnrollments.length === 0" class="card">
          <p>No active enrollments</p>
        </div>

        <div
          v-for="enrollment in studentStore.activeEnrollments"
          :key="enrollment.enrollment_id"
          class="course-card card"
        >
          <div class="course-header">
            <div>
              <h2>{{ enrollment.course_name }}</h2>
              <p class="course-code">{{ enrollment.course }} - Section {{ enrollment.section_number }}</p>
            </div>
            <span class="course-credits">{{ enrollment.course_credits }} Credits</span>
          </div>

          <div class="course-details">
            <div class="detail-item">
              <span class="detail-label">Instructor:</span>
              <span>{{ enrollment.instructor_name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Schedule:</span>
              <span>{{ enrollment.meeting_days }} {{ enrollment.meeting_time }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Semester:</span>
              <span>{{ enrollment.semester }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status:</span>
              <span class="badge badge-success">{{ enrollment.status }}</span>
            </div>
            <div v-if="enrollment.grade" class="detail-item">
              <span class="detail-label">Current Grade:</span>
              <span class="badge badge-success">{{ enrollment.grade }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useStudentStore } from '@/stores/student'
import Layout from '@/components/layout/Layout.vue'

const studentStore = useStudentStore()
const loading = ref(true)

onMounted(async () => {
  await studentStore.fetchEnrollments()
  loading.value = false
})
</script>

<style scoped>
.courses-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.course-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.course-header h2 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.course-code {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
}

.course-credits {
  background: var(--background-secondary);
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 600;
  color: var(--primary-color);
}

.course-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
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
</style>
