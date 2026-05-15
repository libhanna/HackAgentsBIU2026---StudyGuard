<template>
    <div class="main-container">
        <div class="messages-container" ref="messagesContainer">
            <TransitionGroup name="fade-slide">
                <div class="message-wrapper" v-for="(msg, index) in messages" :class="msg.sender == 'user' ? 'user-wrapper' : 'bot-wrapper'" :key="index">
                    <div class="message" :class="msg.sender == 'user' ? 'user-message' : 'bot-message'">
                        {{ msg.text }}
                    </div>
                </div>
            </TransitionGroup>
        </div>
        <div class="chat-container">
            <input class="chat-input" type="text" v-model="message" @keyup.enter="sendMessage" placeholder="Ask StudyGuard anything..." />
            <button class="chat-button-send" @click="sendMessage">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
        </div>
    </div>
</template>

<script setup>
import {onMounted, ref, nextTick} from 'vue';
import {TransitionGroup} from 'vue';
import { toast } from 'vue-sonner'

const messages = ref([]);
const message =  ref('');
const messagesContainer = ref(null);

// Notification sound for new bot messages from /newMessage
const notificationSound = new Audio('/notification.wav');
notificationSound.preload = 'auto';

const playNotificationSound = () => {
    try {
        notificationSound.currentTime = 0;
        const playPromise = notificationSound.play();
        if (playPromise && typeof playPromise.catch === 'function') {
            playPromise.catch((err) => {
                // Most likely autoplay was blocked until the user interacts with the page.
                console.warn('Notification sound blocked:', err);
            });
        }
    } catch (err) {
        console.warn('Notification sound error:', err);
    }
};

const scrollToBottom = async () => {
    await nextTick();
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
};

onMounted(() => {
    setTimeout(() => {
        messages.value.push({text: 'Hello! How can I assist you today?', sender: 'bot'});
        scrollToBottom();
    }, 500);
})

const sendMessage = async () => {
    const messageText = message.value.trim();
    if (messageText) {
        messages.value.push({text: messageText, sender: 'user'});
        message.value = '';
        scrollToBottom();

        try {
            const res = await fetch("http://localhost:5000/sendMessage", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "include",
                body: JSON.stringify({ message: messageText })
            });
            
            if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
            }
            
            scrollToBottom();
        } catch (error) {
            toast.error(`Error: ${error.message}`);
            console.error('Error sending message:', error);
        }
    }
}

const getMessages = async () => {
    try {
        const res = await fetch("http://localhost:5000/newMessage", {
            method: "GET",
            credentials: "include"
        });
        
        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }
        
        const data = await res.json();
        const newMessages = Array.isArray(data.messages) ? data.messages : [];

        if (newMessages.length > 0) {
            messages.value.push(...newMessages);
            playNotificationSound();
            scrollToBottom();
        }
    } catch (error) {
        toast.error(`Error fetching messages: ${error.message}`);
        console.error('Error fetching messages:', error);
    }
}

setInterval(getMessages, 9000);
</script>

<style scoped>
.main-container {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
    width: 100%;
    max-width: 700px;
    margin: 0 auto;
    position: relative;
    padding-bottom: 2rem;
}

.messages-container {
    display: flex;
    flex-direction: column;
    padding: 20px;
    gap: 18px;
    overflow-y: auto;
    flex: 1;
    scroll-behavior: smooth;
    mask-image: linear-gradient(to bottom, transparent, black 5%, black 95%, transparent);
    -webkit-mask-image: linear-gradient(to bottom, transparent, black 5%, black 95%, transparent);
}

.messages-container::-webkit-scrollbar {
    width: 6px;
}
.messages-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.4);
    border-radius: 10px;
}

.message-wrapper {
    display: flex;
    width: 100%;
}

.user-wrapper { justify-content: flex-end; }
.bot-wrapper { justify-content: flex-start; }

.message {
    max-width: 75%;
    padding: 14px 20px;
    font-size: 13pt;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.user-message {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.5);
    color: #1a1a1a;
    border-radius: 20px 20px 4px 20px;
}

.bot-message {
    background: linear-gradient(135deg, rgba(30, 60, 114, 0.85) 0%, rgba(42, 82, 152, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    border-radius: 20px 20px 20px 4px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Liquid Glass Input Container */
.chat-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 20px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 30px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.6);
    transition: all 0.3s ease;
}

.chat-container:focus-within {
    box-shadow: 0 12px 40px rgba(42, 82, 152, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.3);
}

.chat-input {
    flex: 1;
    height: 44px;
    background: transparent;
    border: none;
    padding: 0 15px;
    font-size: 11.5pt;
    color: #222;
    outline: none;
    font-family: inherit;
}

.chat-input::placeholder {
    color: rgba(0, 0, 0, 0.4);
}

.chat-button-send {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 15px rgba(42, 82, 152, 0.3);
}

.chat-button-send:hover {
    transform: scale(1.05) translateY(-2px);
    box-shadow: 0 6px 20px rgba(42, 82, 152, 0.4);
}
        
.chat-button-send:active {
    transform: scale(0.95);
}

/* Slide Fade Animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.fade-slide-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
}
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(-20px);
}
</style>