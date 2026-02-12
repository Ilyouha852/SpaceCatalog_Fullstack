<script setup>
import { ref, watch, onMounted, onUnmounted, onBeforeMount } from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie'
import { useUserInfoStore } from '@/stores/user_info_store';
import QRCode from 'qrcode'

const key = ref();
const userInfoStore = useUserInfoStore();
const totpUrl = ref();
const qrcodeUrl = ref();
const timeLeft = ref(0); 
const timerInterval = ref(null);

function startTimer() {
    if (timerInterval.value) {
        clearInterval(timerInterval.value);
    }
    
    timerInterval.value = setInterval(() => {
        if (userInfoStore.second && timeLeft.value > 0) {
            timeLeft.value--;

            if (timeLeft.value <= 0) {
                userInfoStore.fetchUserInfo();
            }
        }
    }, 1000);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

async function onActivate() {
    try {
        const response = await axios.post("/api/users/second-login/", {
            key: key.value
        });

        await userInfoStore.fetchUserInfo();

        if (response.data.expires_in) {
            timeLeft.value = response.data.expires_in;
            startTimer();
        }
    } catch (err) {
        const msg = err?.response?.data?.message || err.message || 'Ошибка при активации';
        alert(msg);
        console.error('Second factor activation failed:', err);
    }
}

async function getTotpKey() {
    let r = await axios.get('/api/users/get-totp/')
    totpUrl.value = r.data.url;
}


onMounted(() => {
    startTimer();
});

onBeforeMount(() => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
})

onUnmounted(() => {
    if (timerInterval.value) {
        clearInterval(timerInterval.value);
    }
});

watch(totpUrl, async () => {
    qrcodeUrl.value = await QRCode.toDataURL(totpUrl.value);
})
</script>

<template> 
    <div class="second-auth-container">
        <h2 class="title">Двухфакторная аутентификация</h2>
        <div v-if="userInfoStore.second" class="status-section">
            <div v-if="timeLeft > 0" class="time-indicator">
                <div class="time-badge">
                    <span class="time-icon">⏰</span>
                    Действует еще: {{ formatTime(timeLeft) }}
                </div>
                <div class="progress-bar">
                    <div 
                        class="progress-fill" 
                        :style="{ width: ((timeLeft / 60) * 100) + '%' }"
                    ></div>
                </div>
            </div>
        </div>

        <div v-else class="input-group">
            <input 
                type="text" 
                v-model="key"
                placeholder="Введите 6-значный код"
                class="code-input"
                maxlength="6"
            >
            <button 
                @click="onActivate" 
                class="activate-btn"
                :disabled="!key || key.length !== 6"
            >
                Активировать второй фактор
            </button>
        </div>

        <div class="button-group">
            <button @click="getTotpKey" class="key-btn">
                Запросить ключ
            </button>
        </div>
   
        <div class="url-display" v-if="totpUrl">
            <h3>Ссылка для настройки:</h3>
            <div class="url-content">{{ totpUrl }}</div>
        </div>
        
        <div class="qr-container" v-if="qrcodeUrl">
            <h3>QR-код:</h3>
            <img :src="qrcodeUrl" alt="QR Code" class="qr-image">
        </div>
        
        
    </div>
</template>

<style scoped>
    
.second-auth-container {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.title {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 2rem;
    font-size: 1.8rem;
}

.input-group {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.code-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.code-input:focus {
    outline: none;
    border-color: #3498db;
}

.activate-btn {
    padding: 0.75rem 1.5rem;
    background: #3498db;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.3s ease;
}

.activate-btn:hover:not(:disabled) {
    background: #2980b9;
}

.activate-btn:disabled {
    background: #bdc3c7;
    cursor: not-allowed;
}

.button-group {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
}

.key-btn, .group-btn {
    flex: 1;
    padding: 0.75rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.key-btn {
    background: #2ecc71;
    color: white;
}

.key-btn:hover {
    background: #27ae60;
}

.group-btn {
    background: #e74c3c;
    color: white;
}

.group-btn:hover {
    background: #c0392b;
}

.url-display {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border: 1px solid #dee2e6;
}

.url-display h3 {
    margin-top: 0;
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.url-content {
    word-break: break-all;
    font-family: monospace;
    color: #495057;
    font-size: 0.9rem;
}

.qr-container {
    text-align: center;
    margin-bottom: 1.5rem;
}

.qr-container h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.qr-image {
    width: 200px;
    height: 200px;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
    background: white;
}

.time-indicator {
    background: linear-gradient(135deg, #3498db, #2980b9);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    text-align: center;
}

.time-badge {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.time-icon {
    margin-right: 0.5rem;
    font-size: 1.4rem;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #2ecc71;
    border-radius: 4px;
    transition: width 1s linear;
}

.info-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1.5rem;
    color: #856404;
}

.info-box h4 {
    margin-top: 0;
    color: #856404;
}

.info-box p {
    margin: 0.5rem 0;
}
</style>