<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useUserInfoStore } from '@/stores/user_info_store';
import QRCode from 'qrcode';
import { ElMessage } from 'element-plus';

import axios from 'axios';
import Cookies from 'js-cookie'

axios.defaults.withCredentials = true;
axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");

const key = ref(null);
const userInfoStore = useUserInfoStore();
const totpUrl = ref();
const qrcodeUrl = ref(null);
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
    const response = await axios.post("/api/users/second-login/", {
        key: key.value
    });

    await userInfoStore.fetchUserInfo();

    if (response.data.expires_in) {
        timeLeft.value = response.data.expires_in;
        startTimer();
    }

    ElMessage({ message: 'Двухфакторная аутентификация выполнена', type: 'success' });
}

async function getTotpKey() {
    let r = await axios.get('/api/users/get-totp/')
    totpUrl.value = r.data.url;
}


onMounted(() => {
    startTimer();
});

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
    <el-card class="second-auth-container">
        <template #header><h2 class="title">Двухфакторная аутентификация</h2></template>

        <div v-if="userInfoStore.second" class="status-section">
            <div v-if="timeLeft > 0" class="time-indicator">
                <div class="time-badge">⏰ Действует еще: {{ formatTime(timeLeft) }}</div>
                <el-progress :percentage="(timeLeft / 60) * 100" :stroke-width="8" />
            </div>
        </div>

        <div v-else class="input-group">
            <el-input v-model="key" maxlength="6" placeholder="Введите 6-значный код" style="flex:1" />
            <el-button @click="onActivate" :disabled="!key || key.length !== 6" type="primary">Активировать второй фактор</el-button>
        </div>

        <div style="display:flex; gap:1rem; margin-bottom:2rem;">
            <el-button @click="getTotpKey" type="success">Запросить ключ</el-button>
        </div>

        <div v-if="totpUrl" style="background:#f8f9fa; padding:1rem; border-radius:8px; margin-bottom:1.5rem; border:1px solid #dee2e6;">
            <h3 style="margin-top:0; color:#2c3e50; margin-bottom:0.5rem;">Ссылка для настройки:</h3>
            <div style="word-break:break-all; font-family:monospace; color:#495057; font-size:0.9rem;">{{ totpUrl }}</div>
        </div>

        <div v-if="qrcodeUrl" style="text-align:center; margin-bottom:1.5rem;">
            <h3 style="color:#2c3e50; margin-bottom:1rem;">QR-код:</h3>
            <img :src="qrcodeUrl" alt="QR Code" style="width:200px; height:200px; border:1px solid #dee2e6; border-radius:8px; padding:10px; background:white;" />
        </div>
    </el-card>
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

</style>
