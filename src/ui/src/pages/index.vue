<template>
  <div class="homepage">
    <Chat />
  </div>
</template>

<script setup>
import Chat from '../components/chat.vue'
</script>
<style scoped>
.homepage {display: flex; justify-content: center; align-items: center; flex-wrap: wrap; width: 100vw; height: 100vh; margin: auto; background-image: url("https://images.pexels.com/photos/19196730/pexels-photo-19196730.jpeg"); background-size: cover; }
</style>