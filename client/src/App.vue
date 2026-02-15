
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
  <el-container>
    <el-header height="64px">
      <div class="header-row">
        <div class="brand">Космический справочник</div>

        <el-menu class="nav-menu" mode="horizontal" router>
          <el-menu-item index="/">
            <router-link to="/">Обсерватории</router-link>
          </el-menu-item>
          <el-menu-item index="/astronomers">
            <router-link to="/astronomers">Астрономы</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_superuser || user_type === 'admin' || user_type === 'astronomer' || userInfoStore.hasPermission('can_manage_researchers')" index="/researchers">
            <router-link to="/researchers">Исследователи</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/observations">
            <router-link to="/observations">Наблюдения</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/space-objects">
            <router-link to="/space-objects">Космические объекты</router-link>
          </el-menu-item>
          <el-menu-item v-if="userInfoStore.hasPermission('can_see_statistics_page') || userInfoStore.isAdmin()" index="/statistics">
            <router-link to="/statistics">Статистика</router-link>
          </el-menu-item>
          <el-menu-item v-if="is_authenticated" index="/second-auth">
            <router-link to="/second-auth">2FA</router-link>
          </el-menu-item>
        </el-menu>

        <div class="user-area">
          <div v-if="is_authenticated" class="user-info">
            <el-badge v-if="userInfoStore.second" type="success">
              <span class="badge-placeholder" />
            </el-badge>
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
      <div class="main-container">
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

.brand {
  font-weight: 600;
  font-size: 1.1rem;
}

.nav-menu {
  flex: 1 1 auto;
  margin-left: 20px;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main-container {
  padding: 16px;
}
</style>