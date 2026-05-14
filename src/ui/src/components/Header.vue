<script setup lang="ts">

</script>

<template>
    <header class="header">
        <div>Home</div>
        <div><button @click="$emit('calendars')">Calendars</button></div>
        <div><a href="/tasks">Tasks</a></div>
    </header>
</template>

<style scoped>
.header {display: flex; justify-content: space-around; font-family: 'Assistant'; align-items: center; padding: 10px 10px 20px; background-color: transparent; border-bottom: solid 2px #333; width: 100%; position: fixed; height: 50px; top: 0; left: 0; z-index: 100;}
.header a {text-decoration: none; color: #333; font-size: 18pt; font-weight: 500;}
.header a:hover {color: #84c1ff; transition: all 0.3s ease; font-size: 20pt;}   
</style>