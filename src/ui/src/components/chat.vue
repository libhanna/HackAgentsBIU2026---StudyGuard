<template>
    <div>
    <div class="chat-container">
        <input class="chat-input" type="text" v-model="message"  @keyup.enter="sendMessage" placeholder="Please enter your question here..." />
        <button class="chat-button-send" @click="sendMessage">Send</button>
    </div>
    <div class="messages-container">
        <TransitionGroup name="fold">
            <div class="message" v-for="(msg, index) in messages" :class="msg.sender == 'user' ? 'user-message' : 'bot-message'" :key="index">
                {{ msg.text }}
            </div>
        </TransitionGroup>
    </div>
    </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import {TransitionGroup} from 'vue';

const messages = ref([]);
const message =  ref('');

onMounted(() => {
    setTimeout(() => {
        messages.value.push({text: 'Hello! How can I assist you today?', sender: 'bot'});
    }, 500);
})

const sendMessage = () => {
    if (message.value.trim()) {
        messages.value.push({text: message.value, sender: 'user'});
        message.value = '';
    }
}
</script>

<style scoped>
.chat-container { max-height: 200px;}
.chat-input {height: 40px; width: 450px; border-radius: 6px;  border: none; outline: none; padding: 2px 10px; font-size: 12pt; }
.chat-button-send {background: #84c1ff; border-radius: 4px; color: white; border: none; outline: none; height: 40px; width: 80px; margin-left: 1rem; cursor: pointer;}
.messages-container { display: flex; padding-right: 10px; margin-top: 10px; flex-direction: column; perspective: 1000px; max-height: calc(100vh - 80px); overflow-y: auto; }
.user-message { background: #f0f0f0; color: #333; align-self: flex-end; }
.bot-message { background: #84c1ff; color: white; align-self: flex-start; }
.message { margin: 10px 0; padding: 10px; font-size: 12pt; width: 400px; border-radius: 6px; word-wrap: break-word; }

/* Fold Animation */
.fold-enter-active { animation: fold-in 0.5s ease-out; }
.fold-leave-active { animation: fold-out 0.3s ease-in; }
.fold-move { transition: transform 0.3s ease; }

@keyframes fold-in {
    from {
        opacity: 0;
        transform: rotateX(90deg) scaleY(0);
        transform-origin: top;
    }
    to {
        opacity: 1;
        transform: rotateX(0) scaleY(1);
    }
}

@keyframes fold-out {
    from {
        opacity: 1;
        transform: rotateX(0) scaleY(1);
    }
    to {
        opacity: 0;
        transform: rotateX(90deg) scaleY(0);
        transform-origin: top;
    }
}    
</style>