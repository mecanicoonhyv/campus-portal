<template>
  <Layout>
    <div class="catalog-page">
      <h1 class="page-title">Course Catalog</h1>

      <!-- Search and Filters -->
      <div class="card filters-card">
        <div class="search-bar">
          <input
            v-model="searchQuery"
            @input="searchCourses"
            type="text"
            placeholder="Search by course name or code..."
            class="search-input"
          />
        </div>

        <div class="filters">
          <div class="filter-item">
            <label>Department:</label>
            <select v-model="selectedDepartment" @change="filterCourses" class="select">
              <option value="">All Departments</option>
              <option
                v-for="dept in departments"
                :key="dept.department_id"
                :value="dept.department_id"
              >
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="filter-item">
            <label>Level:</label>
            <select v-model="selectedLevel" @change="filterCourses" class="select">
              <option value="">All Levels</option>
              <option value="Undergraduate">Undergraduate</option>
              <option value="Graduate">Graduate</option>
            </select>
          </div>

          <div class="filter-item">
            <label>Status:</label>
            <select v-model="selectedStatus" @change="filterCourses" class="select">
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">Loading courses...</div>

      <!-- Courses Grid -->
      <div v-else class="courses-grid">
        <div v-if="filteredCourses.length === 0" class="card">
          <p>No courses found</p>
        </div>

        <div
          v-for="course in paginatedCourses"
          :key="course.course_id"
          class="course-card card"
        >
          <div class="course-header">
            <div>
              <h3>{{ course.course_name }}</h3>
              <p class="course-code">{{ course.course_id }}</p>
            </div>
            <div class="course-badges">
              <span class="badge">{{ course.credits }} Credits</span>
              <span
                :class="{
                  'badge badge-success': course.status === 'Active',
                  'badge': course.status === 'Inactive'
                }"
              >
                {{ course.status }}
              </span>
            </div>
          </div>

          <div class="course-details">
            <div class="detail-item">
              <span class="detail-label">Department:</span>
              <span>{{ getDepartmentName(course.department_id) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Level:</span>
              <span>{{ course.level }}</span>
            </div>
            <div v-if="course.prerequisites" class="detail-item">
              <span class="detail-label">Prerequisites:</span>
              <span>{{ course.prerequisites }}</span>
            </div>
          </div>

          <p class="course-description">{{ course.description }}</p>

          <div class="course-actions">
            <button @click="viewSections(course.course_id)" class="btn btn-primary">
              View Sections
            </button>
          </div>

          <!-- Sections (shown when expanded) -->
          <div
            v-if="expandedCourse === course.course_id"
            class="sections-section"
          >
            <h4>Available Sections</h4>
            <div v-if="loadingSections" class="loading">Loading sections...</div>
            <table v-else-if="courseSections.length > 0" class="table">
              <thead>
                <tr>
                  <th>Section</th>
                  <th>Instructor</th>
                  <th>Schedule</th>
                  <th>Room</th>
                  <th>Seats</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="section in courseSections" :key="section.section_id">
                  <td>{{ section.section_number }}</td>
                  <td>{{ section.instructor_name }}</td>
                  <td>{{ section.meeting_days }} {{ section.meeting_time }}</td>
                  <td>{{ section.room_number || 'TBA' }}</td>
                  <td>{{ section.enrolled }}/{{ section.capacity }}</td>
                  <td>
                    <span
                      :class="{
                        'badge badge-success': section.status === 'Open',
                        'badge badge-danger': section.status === 'Closed'
                      }"
                    >
                      {{ section.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else>No sections available</div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          @click="currentPage--"
          :disabled="currentPage === 1"
          class="btn btn-secondary"
        >
          Previous
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          @click="currentPage++"
          :disabled="currentPage === totalPages"
          class="btn btn-secondary"
        >
          Next
        </button>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import Layout from '@/components/layout/Layout.vue'
import academicsService from '@/services/academics'

const loading = ref(true)
const loadingSections = ref(false)
const courses = ref([])
const departments = ref([])
const courseSections = ref([])
const expandedCourse = ref(null)

const searchQuery = ref('')
const selectedDepartment = ref('')
const selectedLevel = ref('')
const selectedStatus = ref('')

const currentPage = ref(1)
const pageSize = 10

const filteredCourses = computed(() => {
  let filtered = courses.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      c =>
        c.course_name.toLowerCase().includes(query) ||
        c.course_id.toLowerCase().includes(query)
    )
  }

  if (selectedDepartment.value) {
    filtered = filtered.filter(c => c.department_id === selectedDepartment.value)
  }

  if (selectedLevel.value) {
    filtered = filtered.filter(c => c.level === selectedLevel.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(c => c.status === selectedStatus.value)
  }

  return filtered
})

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredCourses.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredCourses.value.length / pageSize)
})

const getDepartmentName = (deptId) => {
  const dept = departments.value.find(d => d.department_id === deptId)
  return dept ? dept.name : 'Unknown'
}

const searchCourses = () => {
  currentPage.value = 1
}

const filterCourses = () => {
  currentPage.value = 1
}

const viewSections = async (courseId) => {
  if (expandedCourse.value === courseId) {
    expandedCourse.value = null
    courseSections.value = []
    return
  }

  expandedCourse.value = courseId
  loadingSections.value = true

  try {
    const response = await academicsService.getSections({ course: courseId })
    courseSections.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch sections:', error)
  } finally {
    loadingSections.value = false
  }
}

onMounted(async () => {
  try {
    const [coursesResponse, departmentsResponse] = await Promise.all([
      academicsService.getCourses(),
      academicsService.getDepartments(),
    ])

    courses.value = coursesResponse.data.results || coursesResponse.data
    departments.value = departmentsResponse.data.results || departmentsResponse.data
  } catch (error) {
    console.error('Failed to fetch catalog data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.catalog-page {
  max-width: 1400px;
}

.filters-card {
  margin-bottom: 2rem;
}

.search-bar {
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.375rem;
  font-size: 1rem;
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

.courses-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
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
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.course-header h3 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.course-code {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 600;
}

.course-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.course-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
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

.course-description {
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.course-actions {
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sections-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.sections-section h4 {
  margin-bottom: 1rem;
  font-size: 1.125rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>
