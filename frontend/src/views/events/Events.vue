<template>
  <Layout>
    <div class="events-page">
      <h1 class="page-title">Campus Events</h1>

      <!-- Filters -->
      <div class="card filters-card">
        <div class="filters">
          <div class="filter-item">
            <label>Event Type:</label>
            <select v-model="selectedType" @change="filterEvents" class="select">
              <option value="">All Types</option>
              <option value="Academic">Academic</option>
              <option value="Social">Social</option>
              <option value="Sports">Sports</option>
              <option value="Cultural">Cultural</option>
              <option value="Career">Career</option>
            </select>
          </div>

          <div class="filter-item">
            <label>Status:</label>
            <select v-model="selectedStatus" @change="filterEvents" class="select">
              <option value="">All Status</option>
              <option value="Scheduled">Scheduled</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <div class="filter-item">
            <label>Time:</label>
            <select v-model="selectedTime" @change="filterEvents" class="select">
              <option value="">All Events</option>
              <option value="upcoming">Upcoming Only</option>
              <option value="past">Past Only</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">Loading events...</div>

      <!-- Events Grid -->
      <div v-else class="events-grid">
        <div v-if="filteredEvents.length === 0" class="card">
          <p>No events found</p>
        </div>

        <div
          v-for="event in filteredEvents"
          :key="event.event_id"
          class="event-card card"
        >
          <div class="event-header">
            <div>
              <h3>{{ event.name }}</h3>
              <p class="event-organizer">Organized by {{ event.organizer }}</p>
            </div>
            <span
              :class="{
                'badge badge-success': event.status === 'Scheduled',
                'badge': event.status === 'Completed',
                'badge badge-danger': event.status === 'Cancelled'
              }"
            >
              {{ event.status }}
            </span>
          </div>

          <div class="event-details">
            <div class="detail-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <div>
                <span class="detail-label">Date:</span>
                <span>{{ formatDate(event.date) }}</span>
              </div>
            </div>

            <div class="detail-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <span class="detail-label">Time:</span>
                <span>{{ event.start_time }} - {{ event.end_time }}</span>
              </div>
            </div>

            <div class="detail-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div>
                <span class="detail-label">Location:</span>
                <span>{{ event.location }}</span>
              </div>
            </div>

            <div class="detail-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <div>
                <span class="detail-label">Type:</span>
                <span class="badge">{{ event.type }}</span>
              </div>
            </div>

            <div v-if="event.max_participants" class="detail-item">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <div>
                <span class="detail-label">Participants:</span>
                <span>{{ event.registered_count || 0 }} / {{ event.max_participants }}</span>
              </div>
            </div>
          </div>

          <p class="event-description">{{ event.description }}</p>

          <div v-if="event.contact_email" class="event-contact">
            <strong>Contact:</strong> {{ event.contact_email }}
          </div>

          <div v-if="isUpcoming(event.date) && event.status === 'Scheduled'" class="event-actions">
            <button @click="registerForEvent(event)" class="btn btn-primary">
              Register
            </button>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import Layout from '@/components/layout/Layout.vue'
import servicesService from '@/services/services'
import { format, isPast, parseISO } from 'date-fns'

const loading = ref(true)
const events = ref([])
const selectedType = ref('')
const selectedStatus = ref('')
const selectedTime = ref('upcoming')

const filteredEvents = computed(() => {
  let filtered = events.value

  if (selectedType.value) {
    filtered = filtered.filter(e => e.type === selectedType.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(e => e.status === selectedStatus.value)
  }

  if (selectedTime.value === 'upcoming') {
    filtered = filtered.filter(e => !isPast(parseISO(e.date)))
  } else if (selectedTime.value === 'past') {
    filtered = filtered.filter(e => isPast(parseISO(e.date)))
  }

  return filtered.sort((a, b) => new Date(a.date) - new Date(b.date))
})

const formatDate = (date) => {
  return format(new Date(date), 'EEEE, MMMM dd, yyyy')
}

const isUpcoming = (date) => {
  return !isPast(parseISO(date))
}

const filterEvents = () => {
  // Filters are reactive through computed property
}

const registerForEvent = (event) => {
  alert(`Registration for "${event.name}" - Feature coming soon!`)
}

onMounted(async () => {
  try {
    const response = await servicesService.getEvents()
    events.value = response.data.results || response.data
  } catch (error) {
    console.error('Failed to fetch events:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.events-page {
  max-width: 1200px;
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

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.event-card {
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.event-header h3 {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  color: var(--text-primary);
}

.event-organizer {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.event-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--primary-color);
  flex-shrink: 0;
}

.detail-item > div {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detail-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 600;
}

.event-description {
  color: var(--text-primary);
  margin-bottom: 1rem;
  line-height: 1.5;
  flex-grow: 1;
}

.event-contact {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.event-actions {
  display: flex;
  gap: 1rem;
  margin-top: auto;
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

@media (max-width: 768px) {
  .events-grid {
    grid-template-columns: 1fr;
  }
}
</style>
