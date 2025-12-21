<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import QRCode from 'qrcode'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'verified'])

const loading = ref(false)
const verified = ref(false)
const pinInput = ref('')
const totpUrl = ref('')
const qrcodeUrl = ref('')
const error = ref('')

watch(totpUrl, async (newUrl) => {
  if (newUrl) {
    try {
      qrcodeUrl.value = await QRCode.toDataURL(newUrl)
    } catch (err) {
      console.error('Ошибка генерации QR-кода:', err)
    }
  }
})

async function requestTotpKey() {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.get('/api/user/get_totp/')
    if (response.data.success) {
      totpUrl.value = response.data.url
    } else {
      error.value = response.data.error || 'Ошибка при запросе ключа TOTP'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Не удалось запросить TOTP ключ'
    console.error('Ошибка запроса TOTP ключа:', err)
  } finally {
    loading.value = false
  }
}

async function verifyCode() {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.post('/api/user/verify_2fa/', {
      pin: pinInput.value
    })

    if (response.data.success) {
      verified.value = true
      setTimeout(() => {
        emit('verified')
        closeModal()
      }, 1500)
    } else {
      error.value = response.data.error || 'Неверный код'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка при проверке кода'
    console.error('Ошибка верификации TOTP:', err)
  } finally {
    loading.value = false
  }
}

function closeModal() {
  verified.value = false
  pinInput.value = ''
  totpUrl.value = ''
  qrcodeUrl.value = ''
  error.value = ''

  emit('close')
}
</script>

<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">Двухфакторная аутентификация (TOTP)</h5>
          <button
            type="button"
            class="btn-close btn-close-white"
            @click="closeModal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <div v-if="!totpUrl && !verified" class="text-center">
            <p class="mb-3" style="color: white;">Для выполнения этой операции требуется подтверждение через 2FA.<br>Нажмите кнопку ниже, чтобы получить QR-код для приложения аутентификатора 
              (Google Authenticator, Microsoft Authenticator и т.д.)
            </p>
            <button 
              @click="requestTotpKey" 
              class="btn btn-primary btn-lg"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Получить QR-код
            </button>
          </div>

          <div v-else-if="totpUrl && !verified" class="text-center">
            <p class="mb-3">
              Отсканируйте QR-код приложением аутентификатора:
            </p>
            
            <div v-if="qrcodeUrl" class="mb-3">
              <img :src="qrcodeUrl" alt="QR-код для TOTP" class="img-fluid" style="max-width: 200px;" />
            </div>
            
            <div class="alert alert-info small">
              <strong>URL:</strong> {{ totpUrl }}
            </div>

            <form @submit.prevent="verifyCode">
              <div class="mb-3">
                <label for="pinInput" class="form-label">Введите 6-значный код из приложения:</label>
                <input
                  id="pinInput"
                  v-model="pinInput"
                  type="text"
                  class="form-control form-control-lg text-center"
                  placeholder="000000"
                  maxlength="6"
                  pattern="[0-9]{6}"
                  required
                  autofocus
                  :disabled="loading"
                />
              </div>
              
              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>

              <button 
                type="submit" 
                class="btn btn-success btn-lg w-100"
                :disabled="loading || pinInput.length !== 6"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                Подтвердить
              </button>
            </form>
          </div>

          <div v-else class="text-center">
            <div class="text-success mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" viewBox="0 0 16 16">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/>
              </svg>
            </div>
            <h5 class="text-success">Аутентификация успешна!</h5>
            <p class="text-muted">Теперь вы можете редактировать данные.</p>
            <button @click="closeModal" class="btn btn-primary mt-3">
              Продолжить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal.show {
  display: block;
}
</style>
