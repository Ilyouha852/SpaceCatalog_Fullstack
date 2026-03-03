
<script setup>
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import axios from "axios";
import Cookies from 'js-cookie'

axios.defaults.withCredentials = true;
axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");

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
  <el-container>
    <el-header height="64px">
      <div class="header-row">
        <div style="font-weight:600; font-size:1.1rem;">Космический справочник</div>

        <el-menu style="flex:1 1 auto; margin-left:20px;" mode="horizontal" router>
          <el-menu-item v-if="is_authenticated" index="/">
            <router-link to="/">Обсерватории</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/astronomers">
            <router-link to="/astronomers">Астрономы</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/researchers">
            <router-link to="/researchers">Исследователи</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/observations">
            <router-link to="/observations">Наблюдения</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_superuser || user_type === 'astronomer'" index="/space-objects">
            <router-link to="/space-objects">Космические объекты</router-link>
          </el-menu-item>
          <el-menu-item v-if="userInfoStore.hasPermission('can_see_statistics_page') || userInfoStore.is_superuser" index="/statistics">
            <router-link to="/statistics">Статистика</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/second-auth">
            <router-link to="/second-auth">2FA</router-link>
          </el-menu-item>
        </el-menu>

        <div class="user-area">
          <div v-if="is_authenticated" class="user-info">
            <span class="username">{{ username }}</span>
            <el-button size="small" type="warning" plain @click="onLogout">Выйти</el-button>
          </div>
          <div v-else>
            <router-link to="/login">
              <el-button type="primary" plain>Войти</el-button>
            </router-link>
          </div>
        </div>
      </div>
    </el-header>

    <el-main>
      <div style="padding:16px;">
        <router-view />
      </div>
    </el-main>
  </el-container>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: space-between;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
