<script setup>
import { Toaster, toast } from 'vue-sonner'
import 'vue-sonner/style.css'
</script>

<template>
  <router-view />
  <Toaster />
</template>

<style>
::-webkit-scrollbar {
  width: 5px;
}

/* Track */
::-webkit-scrollbar-track {
  box-shadow: inset 0 0 5px grey;
  border-radius: 10px;
  padding: 2px;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: rgb(190, 190, 190);
  border-radius: 10px;
}
</style>
