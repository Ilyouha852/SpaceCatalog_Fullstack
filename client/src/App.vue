<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { storeToRefs } from 'pinia';

const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

const isLoading = ref(true);
const isLoginLoading = ref(false);

const username = ref('');
const password = ref('');
const loginError = ref('');

onMounted(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');

  try {
    await userStore.checkLogin();
  } finally {
    isLoading.value = false;
  }
});

async function onFormSend() {
  loginError.value = '';
  isLoginLoading.value = true;
  try {
    const result = await userStore.login(username.value, password.value);
    if (!result.success) {
      loginError.value = result.error || 'Failed to login';
    }
  } catch (error) {
    loginError.value = 'An error occurred during login';
    console.error('Login error:', error);
  } finally {
    isLoginLoading.value = false;
  }
}

async function handleLogout() {
  await userStore.logout();
}
</script>

<template>
  <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="height: 100vh;">
    <div class="spinner-border" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>

  <div v-else>
    <nav class="navbar navbar-expand-lg">
      <div class="container">
        <a class="navbar-brand" href="/" style="color: #fff;">
          <i class="fas fa-rocket" style="margin-right: 8px;"></i>
          Космический каталог
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="fas fa-home"></i> Главная
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/astronomers">
                <i class="fas fa-user-astronaut"></i> Астрономы
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/spaceobjects">
                <i class="fas fa-galaxy"></i> Космические объекты
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/objecttypes">
                <i class="fas fa-star-half-alt"></i> Типы объектов
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/researchers">
                <i class="fas fa-users"></i> Исследователи
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/observations">
                <i class="fas fa-telescope"></i> Наблюдения
              </router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-user-circle"></i> Пользователь
              </a>
              <ul class="dropdown-menu">
                <li v-if="userInfo && userInfo.is_staff">
                  <a class="dropdown-item" href="/admin">
                    <i class="fas fa-cog"></i> Админка
                  </a>
                </li>
                <li>
                  <a class="dropdown-item" href="#" @click="handleLogout">
                    <i class="fas fa-sign-out-alt"></i> Выйти
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container">
      <router-view/>
    </div>
  </div>

  <div v-if="userInfo && !userInfo.is_authenticated" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.7)">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-user-astronaut me-2"></i>
            Добро пожаловать в Космический каталог
          </h5>
        </div>
        <div class="modal-body">
          <div class="container">
            <div class="text-center mb-4">
              <i class="fas fa-rocket fa-3x mb-3" style="color: #a8b2ff;"></i>
              <p class="text-muted">Пожалуйста, авторизуйтесь для доступа к каталогу</p>
            </div>
            <form @submit.stop.prevent="onFormSend" class="mb-3">
              <div class="mb-3">
                <div class="input-group">
                  <span class="input-group-text bg-transparent border-end-0">
                    <i class="fas fa-user" style="color: #a8b2ff;"></i>
                  </span>
                  <input 
                    v-model="username" 
                    type="text" 
                    placeholder="Имя пользователя" 
                    required 
                    class="form-control border-start-0"
                    :disabled="isLoginLoading"
                  >
                </div>
              </div>
              <div class="mb-4">
                <div class="input-group">
                  <span class="input-group-text bg-transparent border-end-0">
                    <i class="fas fa-lock" style="color: #a8b2ff;"></i>
                  </span>
                  <input 
                    v-model="password" 
                    type="password" 
                    placeholder="Пароль" 
                    required 
                    class="form-control border-start-0"
                    :disabled="isLoginLoading"
                  >
                </div>
              </div>
              
              <div v-if="loginError" class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                {{ loginError }}
              </div>

              <button 
                type="submit" 
                class="btn btn-primary w-100 py-2"
                :disabled="isLoginLoading"
              >
                <span v-if="isLoginLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-sign-in-alt me-2"></i>
                {{ isLoginLoading ? 'Подключение...' : 'Войти в систему' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>