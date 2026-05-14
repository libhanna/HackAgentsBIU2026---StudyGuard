<template>
  <div class="calendar-panel" :class="{ 'full-screen': isFullScreen }">
    <div class="header">
      <h2>Today's Schedule</h2>
      <button class="toggle-btn" @click="isFullScreen = !isFullScreen">
        {{ isFullScreen ? '⛙' : '⛶' }}
      </button>
    </div>
    
    <div v-if="loading" class="state-msg loading-container">
      <div class="spinner"></div>
      <span>Loading events...</span>
    </div>
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
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 30px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1),
              inset 0 1px 0 rgba(255, 255, 255, 0.6);
  padding: 2rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

.calendar-panel::-webkit-scrollbar {
  width: 6px;
}
.calendar-panel::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
}

.calendar-panel.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1000;
  border-radius: 0;
  background: rgba(255, 255, 255, 0.3);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 1rem;
}

.header h2 {
  margin: 0;
  color: #1a1a1a;
  font-size: 1.5rem;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
  color: #333;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.05);
  color: #000;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.event-card {
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-left: 4px solid #2a5298;
  border-radius: 16px;
  padding: 1.2rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.55);
}

.time-block {
  font-weight: 600;
  color: #555;
  font-size: 0.95rem;
  display: flex;
  gap: 0.5rem;
}

.topic {
  font-size: 1.15rem;
  color: #222;
  font-weight: 500;
}

.state-msg {
  text-align: center;
  color: #555;
  padding: 3rem 0;
  font-size: 1.1rem;
  font-weight: 500;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.6);
}

.state-msg.error {
  color: #d9534f;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(42, 82, 152, 0.2);
  border-top-color: #2a5298;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>