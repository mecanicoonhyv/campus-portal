<template>
  <Layout>
    <div class="grades-page">
      <h1 class="page-title">My Grades</h1>

      <div v-if="loading" class="loading">Loading grades...</div>

      <div v-else>
        <!-- GPA Summary -->
        <div class="card gpa-card">
          <div class="gpa-content">
            <div class="gpa-section">
              <h3>Current GPA</h3>
              <p class="gpa-value">{{ grades?.gpa?.toFixed(2) || '0.00' }}</p>
            </div>
            <div class="gpa-section">
              <h3>Total Credits</h3>
              <p class="gpa-value">{{ grades?.total_credits || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Grades Table -->
        <div class="card">
          <h2>Course Grades</h2>
          <div v-if="!grades || grades.enrollments.length === 0">
            No grades available yet
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Course</th>
                <th>Credits</th>
                <th>Semester</th>
                <th>Instructor</th>
                <th>Grade</th>
                <th>Grade Points</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="enrollment in grades.enrollments" :key="enrollment.enrollment_id">
                <td>
                  <strong>{{ enrollment.course }}</strong>
                  <br />
                  <small>{{ enrollment.course_name }}</small>
                </td>
                <td>{{ enrollment.course_credits }}</td>
                <td>{{ enrollment.semester }}</td>
                <td>{{ enrollment.instructor_name }}</td>
                <td>
                  <span
                    :class="{
                      'badge badge-success': ['A', 'A-', 'B+', 'B'].includes(enrollment.grade),
                      'badge badge-warning': ['B-', 'C+', 'C'].includes(enrollment.grade),
                      'badge badge-danger': ['C-', 'D+', 'D', 'D-', 'F'].includes(enrollment.grade)
                    }"
                  >
                    {{ enrollment.grade }}
                  </span>
                </td>
                <td>{{ enrollment.grade_points }}</td>
              </tr>
            </tbody>
          </table>
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
const grades = ref(null)

onMounted(async () => {
  await studentStore.fetchGrades()
  grades.value = studentStore.grades
  loading.value = false
})
</script>

<style scoped>
.gpa-card {
  margin-bottom: 2rem;
}

.gpa-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.gpa-section h3 {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.gpa-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}
</style>
