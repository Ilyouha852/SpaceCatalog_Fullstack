<script setup>
import { ref } from 'vue';
import { useUserInfoStore } from '@/stores/user_info_store';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

const username = ref('');
const password = ref('');

const userInfoStore = useUserInfoStore();
const {
    is_authenticated
} = storeToRefs(userInfoStore)
const router = useRouter();

async function onLoginFormSubmit() {
  const r = await axios.post("/api/users/login/", {
    username: username.value,
    password: password.value,
  })

  password.value = '';
  username.value = '';

  await userInfoStore.fetchUserInfo();

  if (is_authenticated.value) {
    router.push("/")
  }
}
</script>

<template>
  <div class="login-form">
    <el-form label-position="top" @submit.prevent="onLoginFormSubmit">
      <el-form-item>
        <el-input v-model="username" placeholder="логин" />
      </el-form-item>

      <el-form-item>
        <el-input v-model="password" placeholder="пароль" show-password type="password" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" native-type="submit">Войти</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<style scoped>
.login-form {
  max-width: 420px;
  margin: 24px auto;
  padding: 12px;
}
</style>