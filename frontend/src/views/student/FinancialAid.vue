<template>
  <Layout>
    <div class="financial-aid-page">
      <h1 class="page-title">Financial Aid</h1>

      <div v-if="loading" class="loading">Loading financial aid...</div>

      <div v-else>
        <!-- Summary Card -->
        <div class="card summary-card">
          <div class="summary-grid">
            <div class="summary-item">
              <h3>Total Aid Amount</h3>
              <p class="amount">${{ totalAmount.toFixed(2) }}</p>
            </div>
            <div class="summary-item">
              <h3>Disbursed Amount</h3>
              <p class="amount disbursed">${{ disbursedAmount.toFixed(2) }}</p>
            </div>
          </div>
        </div>

        <!-- Aid Records -->
        <div class="card">
          <h2>Financial Aid Awards</h2>
          <div v-if="!financialAid || financialAid.aid_records.length === 0">
            No financial aid records
          </div>
          <div v-else class="aid-list">
            <div
              v-for="aid in financialAid.aid_records"
              :key="aid.aid_id"
              class="aid-item"
            >
              <div class="aid-header">
                <div>
                  <h3>{{ aid.name }}</h3>
                  <p class="aid-type">{{ aid.type }}</p>
                </div>
                <div class="aid-amount">
                  <span class="amount">${{ aid.amount }}</span>
                  <span
                    :class="{
                      'badge badge-success': aid.status === 'Disbursed',
                      'badge badge-warning': aid.status === 'Approved',
                      'badge': aid.status === 'Pending',
                      'badge badge-danger': aid.status === 'Rejected'
                    }"
                  >
                    {{ aid.status }}
                  </span>
                </div>
              </div>
              <div class="aid-details">
                <div><strong>Academic Year:</strong> {{ aid.academic_year }}</div>
                <div><strong>Semester:</strong> {{ aid.semester }}</div>
                <div v-if="aid.disbursement_date">
                  <strong>Disbursement Date:</strong> {{ formatDate(aid.disbursement_date) }}
                </div>
              </div>
              <p v-if="aid.description" class="aid-description">{{ aid.description }}</p>
            </div>
          </div>
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
const financialAid = ref(null)

const totalAmount = computed(() => {
  return financialAid.value?.total_amount || 0
})

const disbursedAmount = computed(() => {
  return financialAid.value?.disbursed_amount || 0
})

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

onMounted(async () => {
  await studentStore.fetchFinancialAid()
  financialAid.value = studentStore.financialAid
  loading.value = false
})
</script>

<style scoped>
.summary-card {
  margin-bottom: 2rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.summary-item h3 {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

.amount.disbursed {
  color: var(--secondary-color);
}

.aid-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.aid-item {
  padding: 1.5rem;
  background: var(--background-secondary);
  border-radius: 0.5rem;
  border-left: 4px solid var(--primary-color);
}

.aid-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.aid-header h3 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.aid-type {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
}

.aid-amount {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.aid-details {
  display: flex;
  gap: 2rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.aid-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}
</style>
