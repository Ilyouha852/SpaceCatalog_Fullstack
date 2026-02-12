import { defineStore } from "pinia";
import { onBeforeMount, ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false,
        username: "",
        is_staff: false,
        is_superuser: false
    })
    
    async function checkLogin() {
        try {
            // Устанавливаем CSRF токен для всех запросов
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
            
            let response = await axios.get("/api/user/info/")
            userInfo.value = response.data;
        } catch (error) {
            console.error("Check login error:", error);
            userInfo.value = {
                is_authenticated: false,
                username: "",
                is_staff: false,
                is_superuser: false
            };
        }
    }

    async function login(username, password) {
        try {
            // Устанавливаем CSRF токен
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
            
            let response = await axios.post("/api/user/login/", {
                username: username,
                password: password,
            })
            
            if (response.status === 200) {
                await checkLogin();
                return { success: true };
            }
        } catch (error) {
            console.error("Login error:", error);
            return { 
                success: false, 
                error: error.response?.data?.message || "Ошибка авторизации" 
            };
        }
    }

    async function logout() {
        try {
            // Устанавливаем CSRF токен
            axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
            
            await axios.post("/api/user/logout/");
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            userInfo.value = {
                is_authenticated: false,
                username: "",
                is_staff: false,
                is_superuser: false
            };
        }
    }

    // Проверяем авторизацию при инициализации store
    onBeforeMount(async () => {
        await checkLogin();
    })

    return {
        userInfo,
        checkLogin,
        login,
        logout
    }
})