<template>
  <div class="homepage">
    <Chat />
  </div>
</template>

<script setup>
import Chat from '../components/chat.vue'
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
.homepage {display: flex; justify-content: center; font-family: 'Assistant'; align-items: center; flex-wrap: wrap; width: 100%; height: 100%; background-image: url("https://images.pexels.com/photos/19196730/pexels-photo-19196730.jpeg"); background-size: cover; background-attachment: fixed; }
</style>