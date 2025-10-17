<template>
  <Layout>
    <div class="library-page">
      <h1 class="page-title">Library</h1>

      <div v-if="loading" class="loading">Loading library data...</div>

      <div v-else>
        <!-- Active Checkouts -->
        <div class="card">
          <h2>My Active Checkouts</h2>
          <div v-if="activeCheckouts.length === 0">
            No active checkouts
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Book</th>
                <th>Author</th>
                <th>Checkout Date</th>
                <th>Due Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="checkout in activeCheckouts" :key="checkout.checkout_id">
                <td><strong>{{ checkout.book_title }}</strong></td>
                <td>{{ checkout.book_author }}</td>
                <td>{{ formatDate(checkout.checkout_date) }}</td>
                <td>{{ formatDate(checkout.due_date) }}</td>
                <td>
                  <span
                    :class="{
                      'badge badge-success': !checkout.is_overdue,
                      'badge badge-danger': checkout.is_overdue
                    }"
                  >
                    {{ checkout.is_overdue ? `Overdue (${checkout.days_overdue} days)` : 'Active' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Checkout History -->
        <div class="card">
          <h2>Checkout History</h2>
          <div v-if="returnedCheckouts.length === 0">
            No checkout history
          </div>
          <table v-else class="table">
            <thead>
              <tr>
                <th>Book</th>
                <th>Author</th>
                <th>Checkout Date</th>
                <th>Return Date</th>
                <th>Fine</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="checkout in returnedCheckouts" :key="checkout.checkout_id">
                <td><strong>{{ checkout.book_title }}</strong></td>
                <td>{{ checkout.book_author }}</td>
                <td>{{ formatDate(checkout.checkout_date) }}</td>
                <td>{{ formatDate(checkout.return_date) }}</td>
                <td>
                  <span v-if="checkout.fine_amount > 0" class="badge badge-warning">
                    ${{ checkout.fine_amount }}
                  </span>
                  <span v-else>-</span>
                </td>
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

const activeCheckouts = computed(() => {
  return studentStore.libraryCheckouts.filter(c => c.status === 'Active' || c.status === 'Overdue')
})

const returnedCheckouts = computed(() => {
  return studentStore.libraryCheckouts.filter(c => c.status === 'Returned')
})

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

onMounted(async () => {
  await studentStore.fetchLibraryCheckouts()
  loading.value = false
})
</script>
