<template>
    <div class="chat-container">
        <input class="chat-input" type="text" placeholder="Please enter your question here..." />
        <button class="chat-button-send">Send</button>
    </div>
</template>

<style scoped>
.chat-container { max-height: 200px;}
.chat-input {height: 40px; width: 450px; border-radius: 6px;  border: none; outline: none; padding: 2px 10px; font-size: 12pt; }
.chat-button-send {background: #84c1ff; border-radius: 4px; color: white; border: none; outline: none; height: 40px; width: 80px; margin-left: 1rem; cursor: pointer;}
</style>