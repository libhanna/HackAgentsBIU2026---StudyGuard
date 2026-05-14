<template>
  <div class="homepage">
    <div class="side-panel">
      <Calendar />
    </div>
    <div class="main-panel">
      <Chat />
    </div>
  </div>
</template>

<script setup>
import Chat from '../components/chat.vue'
import Calendar from '../components/calendar.vue'
</script>
<style>
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
</style>
<style scoped>
.homepage {
  display: flex;
  justify-content: center;
  font-family: 'Assistant';
  align-items: stretch;
  width: 100%;
  height: 100%;
  background-image: url("https://images.pexels.com/photos/314726/pexels-photo-314726.jpeg");
  background-size: cover;
  background-attachment: fixed;
  padding: 2rem;
  box-sizing: border-box;
  gap: 2rem;
}

.side-panel {
  flex: 0 0 calc(33.333% - 1rem); /* About 1/3 of the screen */
  max-width: 400px;
  min-width: 300px;
  height: calc(100vh - 150px);
  position: relative;
  top: 80px;
  box-sizing: border-box;
}

.main-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 150px);
  top: 100px;
  position: relative;
  box-sizing: border-box;
}
</style>