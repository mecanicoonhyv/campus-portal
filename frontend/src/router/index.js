import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy load views
const Login = () => import('@/views/auth/Login.vue')
const StudentDashboard = () => import('@/views/student/Dashboard.vue')
const StudentCourses = () => import('@/views/student/Courses.vue')
const StudentGrades = () => import('@/views/student/Grades.vue')
const StudentAttendance = () => import('@/views/student/Attendance.vue')
const StudentLibrary = () => import('@/views/student/Library.vue')
const StudentFinancialAid = () => import('@/views/student/FinancialAid.vue')
const FacultyDashboard = () => import('@/views/faculty/Dashboard.vue')
const FacultySections = () => import('@/views/faculty/Sections.vue')
const FacultyAssignments = () => import('@/views/faculty/Assignments.vue')
const CourseCatalog = () => import('@/views/courses/Catalog.vue')
const Events = () => import('@/views/events/Events.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, hideNav: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/courses',
    name: 'Courses',
    component: StudentCourses,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/grades',
    name: 'Grades',
    component: StudentGrades,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: StudentAttendance,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/library',
    name: 'Library',
    component: StudentLibrary,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/financial-aid',
    name: 'FinancialAid',
    component: StudentFinancialAid,
    meta: { requiresAuth: true, roles: ['student'] }
  },
  {
    path: '/faculty/dashboard',
    name: 'FacultyDashboard',
    component: FacultyDashboard,
    meta: { requiresAuth: true, roles: ['faculty'] }
  },
  {
    path: '/faculty/sections',
    name: 'FacultySections',
    component: FacultySections,
    meta: { requiresAuth: true, roles: ['faculty'] }
  },
  {
    path: '/faculty/assignments',
    name: 'FacultyAssignments',
    component: FacultyAssignments,
    meta: { requiresAuth: true, roles: ['faculty'] }
  },
  {
    path: '/catalog',
    name: 'Catalog',
    component: CourseCatalog,
    meta: { requiresAuth: true }
  },
  {
    path: '/events',
    name: 'Events',
    component: Events,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    // Redirect to appropriate dashboard
    if (authStore.isStudent) {
      next('/dashboard')
    } else if (authStore.isFaculty) {
      next('/faculty/dashboard')
    } else {
      next('/dashboard')
    }
  } else if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    // User doesn't have required role
    next('/dashboard')
  } else {
    next()
  }
})

export default router
