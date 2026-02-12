
<script setup>
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";
import { onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const userInfoStore = useUserInfoStore();
const { 
  is_authenticated, 
  is_superuser, 
  username, 
  user_type
} = storeToRefs(userInfoStore);

const router = useRouter();

onMounted(() => {
  userInfoStore.fetchUserInfo();
});

async function onLogout() {
  const r = await axios.post("/api/users/logout/");
  userInfoStore.fetchUserInfo();
  router.push("/login");
}
</script>

<template>
  <div>
    <nav class="navbar navbar-expand-sm navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand" href="#">Космический справочник</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown">
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse justify-content-between" id="navbarNavDropdown">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Обсерватории</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/astronomers">Астрономы</router-link>
            </li>
            <li class="nav-item" v-if="is_superuser || user_type === 'admin' || user_type === 'astronomer' || userInfoStore.hasPermission('can_manage_researchers')">
              <router-link class="nav-link" to="/researchers">Исследователи</router-link>
            </li>
            <li class="nav-item" v-if="is_authenticated">
              <router-link class="nav-link" to="/observations">Наблюдения</router-link>
            </li>
            <li class="nav-item" v-if="is_authenticated">
              <router-link class="nav-link" to="/space-objects">Космические объекты</router-link>
            </li>
            <li class="nav-item" v-if="userInfoStore.hasPermission('can_see_statistics_page') || userInfoStore.isAdmin()">
              <router-link class="nav-link" to="/statistics">Статистика</router-link>
            </li>
            <li class="nav-item" v-if="is_authenticated">
              <router-link class="nav-link" to="/second-auth">
                <i class="bi bi-shield-check me-1"></i>
                2FA
              </router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item" v-if="is_authenticated">
              <div class="d-flex align-items-center" style="gap: 10px;">
                <span class="navbar-text text-light">{{ username }}</span>
                
                <span v-if="userInfoStore.second" class="badge bg-success">
    <i class="bi bi-shield-check me-1"></i>
    
</span>

                
                <button class="btn btn-outline-light btn-sm" @click="onLogout">
                  <i class="bi bi-box-arrow-right me-1"></i>
                  Выйти
                </button>
              </div>
            </li>
            
            <li class="nav-item" v-if="!is_authenticated">
              <router-link class="nav-link" to="/login">
                <button class="btn btn-outline-light" type="button">
                  <i class="bi bi-box-arrow-in-right me-1"></i>
                  Войти
                </button>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0,0,0,.1);
}

.nav-link {
  color: rgba(255, 255, 255, 0.85) !important;
  transition: color 0.2s;
}

.nav-link:hover {
  color: white !important;
}

.btn-outline-light {
  border-color: rgba(255, 255, 255, 0.5);
  color: white;
}

.btn-outline-light:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: white;
}

.container {
  margin-top: 20px;
}

.badge {
  font-size: 0.75em;
  padding: 0.25em 0.5em;
}

@media (max-width: 992px) {
  .navbar-collapse {
    text-align: center;
  }
  
  .nav-item {
    margin: 5px 0;
  }
  
  .d-flex.align-items-center {
    flex-direction: column;
    gap: 10px;
  }
}
</style>