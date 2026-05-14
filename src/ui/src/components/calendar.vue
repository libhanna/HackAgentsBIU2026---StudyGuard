<template>
  <div class="calendar-panel" :class="{ 'full-screen': isFullScreen }">
    <div class="header">
      <h2>📅 Today's Schedule</h2>
      <button class="toggle-btn" @click="isFullScreen = !isFullScreen">
        {{ isFullScreen ? '⛙' : '⛶' }}
      </button>
    </div>
    
    <div v-if="loading" class="state-msg">Loading events...</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    
    <div v-else class="events-list">
      <div v-if="todayEvents.length === 0" class="state-msg">
        No events planned for today. Enjoy your free time!
      </div>
      <div v-else class="event-card" v-for="(event, index) in todayEvents" :key="index">
        <div class="time-block">
          <span class="start">{{ event.start }}</span>
          <span class="separator">-</span>
          <span class="end">{{ event.end }}</span>
        </div>
        <div class="topic">{{ event.topic }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

const isFullScreen = ref(false);
const allEvents = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchEvents = async () => {
  try {
    const res = await fetch("http://localhost:5000/calendar", {
      credentials: "include"
    });
    if (!res.ok) throw new Error(`Server error: ${res.status}`);
    const data = await res.json();
    allEvents.value = data.events || [];
  } catch (err) {
    error.value = "Failed to load calendar. Please check if the server is running.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const todayEvents = computed(() => {
  // Assuming events in allEvents are for today according to app.py flattening 
  // Let's filter just in case if app.py actually sends future events too.
  // Although app.py code seems to sync today events.
  return allEvents.value;
});

onMounted(() => {
  fetchEvents();
});
</script>

<style scoped>
.calendar-panel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.calendar-panel.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
  border-radius: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 1.4rem;
}

.toggle-btn {
  background: transparent;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.toggle-btn:hover {
  color: #000;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.event-card {
  background: white;
  border-left: 4px solid #84c1ff;
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-block {
  font-weight: bold;
  color: #555;
  font-size: 0.9rem;
}

.topic {
  font-size: 1.1rem;
  color: #222;
}

.state-msg {
  text-align: center;
  color: #777;
  padding: 2rem 0;
  font-style: italic;
}

.state-msg.error {
  color: #d9534f;
}
</style>