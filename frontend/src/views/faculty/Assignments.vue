<template>
  <Layout>
    <div class="assignments-page">
      <h1 class="page-title">Assignments & Grading</h1>

      <div v-if="loading" class="loading">Loading assignments...</div>

      <div v-else>
        <!-- Filters -->
        <div class="card filters-card">
          <div class="filters">
            <div class="filter-item">
              <label>Section:</label>
              <select v-model="selectedSectionFilter" @change="filterAssignments" class="select">
                <option value="">All Sections</option>
                <option
                  v-for="section in sections"
                  :key="section.section_id"
                  :value="section.section_id"
                >
                  {{ section.course_id }} - {{ section.section_number }}
                </option>
              </select>
            </div>
            <div class="filter-item">
              <label>Type:</label>
              <select v-model="selectedTypeFilter" @change="filterAssignments" class="select">
                <option value="">All Types</option>
                <option value="Homework">Homework</option>
                <option value="Quiz">Quiz</option>
                <option value="Exam">Exam</option>
                <option value="Project">Project</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Assignments List -->
        <div class="assignments-grid">
          <div v-if="filteredAssignments.length === 0" class="card">
            <p>No assignments found</p>
          </div>

          <div
            v-for="assignment in filteredAssignments"
            :key="assignment.assignment_id"
            class="assignment-card card"
          >
            <div class="assignment-header">
              <div>
                <h3>{{ assignment.title }}</h3>
                <p class="assignment-meta">
                  {{ assignment.course_name }} - {{ assignment.section_number }}
                </p>
              </div>
              <span class="badge">{{ assignment.type }}</span>
            </div>

            <div class="assignment-details">
              <div class="detail-row">
                <span class="detail-label">Due Date:</span>
                <span>{{ formatDate(assignment.due_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Points:</span>
                <span>{{ assignment.total_points }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span
                  :class="{
                    'badge badge-success': assignment.status === 'Published',
                    'badge': assignment.status === 'Draft'
                  }"
                >
                  {{ assignment.status }}
                </span>
              </div>
            </div>

            <p class="assignment-description">{{ assignment.description }}</p>

            <div class="assignment-actions">
              <button
                @click="viewSubmissions(assignment.assignment_id)"
                class="btn btn-primary"
              >
                View Submissions
              </button>
            </div>

            <!-- Submissions Table (shown when selected) -->
            <div
              v-if="selectedAssignment === assignment.assignment_id"
              class="submissions-section"
            >
              <h4>Student Submissions</h4>
              <div v-if="loadingSubmissions" class="loading">Loading submissions...</div>
              <table v-else-if="submissions.length > 0" class="table">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Submitted</th>
                    <th>Status</th>
                    <th>Grade</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="submission in submissions"
                    :key="submission.submission_id"
                  >
                    <td>{{ submission.student_name }}</td>
                    <td>{{ formatDateTime(submission.submission_date) }}</td>
                    <td>
                      <span
                        :class="{
                          'badge badge-warning': submission.status === 'Submitted',
                          'badge badge-success': submission.status === 'Graded',
                          'badge': submission.status === 'Late'
                        }"
                      >
                        {{ submission.status }}
                      </span>
                    </td>
                    <td>
                      <span v-if="submission.points_earned !== null">
                        {{ submission.points_earned }} / {{ assignment.total_points }}
                      </span>
                      <span v-else class="text-muted">Not graded</span>
                    </td>
                    <td>
                      <button
                        v-if="submission.status !== 'Graded'"
                        @click="gradeSubmission(submission, assignment.total_points)"
                        class="btn btn-sm btn-secondary"
                      >
                        Grade
                      </button>
                      <button
                        v-else
                        @click="viewGrade(submission)"
                        class="btn btn-sm btn-secondary"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else>No submissions yet</div>
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
const loadingSubmissions = ref(false)
const sections = ref([])
const assignments = ref([])
const submissions = ref([])
const selectedAssignment = ref(null)
const selectedSectionFilter = ref('')
const selectedTypeFilter = ref('')

const filteredAssignments = computed(() => {
  let filtered = assignments.value

  if (selectedSectionFilter.value) {
    filtered = filtered.filter(a => a.section_id === selectedSectionFilter.value)
  }

  if (selectedTypeFilter.value) {
    filtered = filtered.filter(a => a.type === selectedTypeFilter.value)
  }

  return filtered
})

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

const formatDateTime = (date) => {
  return format(new Date(date), 'MMM dd, yyyy h:mm a')
}

const viewSubmissions = async (assignmentId) => {
  if (selectedAssignment.value === assignmentId) {
    selectedAssignment.value = null
    submissions.value = []
    return
  }

  selectedAssignment.value = assignmentId
  loadingSubmissions.value = true

  try {
    const response = await assessmentsService.getSubmissions({ assignment: assignmentId })
    submissions.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch submissions:', error)
  } finally {
    loadingSubmissions.value = false
  }
}

const gradeSubmission = (submission, totalPoints) => {
  const points = prompt(`Enter points earned (out of ${totalPoints}):`, '0')
  if (points === null) return

  const pointsEarned = parseFloat(points)
  if (isNaN(pointsEarned) || pointsEarned < 0 || pointsEarned > totalPoints) {
    alert('Invalid points value')
    return
  }

  const feedback = prompt('Enter feedback (optional):', '')

  // Call API to grade submission
  assessmentsService.gradeSubmission(submission.submission_id, {
    points_earned: pointsEarned,
    feedback: feedback || ''
  })
    .then(() => {
      alert('Submission graded successfully')
      // Refresh submissions
      viewSubmissions(selectedAssignment.value)
    })
    .catch(error => {
      console.error('Failed to grade submission:', error)
      alert('Failed to grade submission')
    })
}

const viewGrade = (submission) => {
  alert(`Grade: ${submission.points_earned}\nFeedback: ${submission.feedback || 'No feedback provided'}`)
}

const filterAssignments = () => {
  // Filters are reactive through computed property
}

onMounted(async () => {
  try {
    // Fetch sections
    const sectionsResponse = await academicsService.getMySections()
    sections.value = sectionsResponse.data.results || sectionsResponse.data

    // Fetch assignments
    const assignmentsResponse = await assessmentsService.getAssignments()
    assignments.value = assignmentsResponse.data.results || assignmentsResponse.data
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.assignments-page {
  max-width: 1400px;
}

.filters-card {
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 200px;
}

.filter-item label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.assignments-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.assignment-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.assignment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.assignment-header h3 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.assignment-meta {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.assignment-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.detail-row {
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

.assignment-description {
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.assignment-actions {
  display: flex;
  gap: 1rem;
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

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.submissions-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.submissions-section h4 {
  margin-bottom: 1rem;
  font-size: 1.125rem;
}

.text-muted {
  color: var(--text-secondary);
}
</style>
