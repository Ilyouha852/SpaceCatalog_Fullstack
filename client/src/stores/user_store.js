import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false,
        isLoading: true
    })

    async function checkLogin() {
        try {
            let r = await axios.get("/api/user/info/")
            userInfo.value = r.data;
        } catch (error) {
            userInfo.value = {
                is_authenticated: false
            };
        }
    }

    async function login(username, password) {
        try {
            console.log('Attempting login with:', { username });
            const r = await axios.post("/api/user/login/", {
                username: username,
                password: password,
            });
            console.log('Login response:', r.data);
            if (r.data.success) {
                await checkLogin();
                return { success: true };
            } else {
                userInfo.value = {
                    is_authenticated: false,
                    error: 'Invalid credentials'
                };
                return { success: false, error: 'Invalid credentials' };
            }
        } catch (error) {
            console.error('Login error:', error.response?.data || error.message);
            userInfo.value = {
                is_authenticated: false,
                error: error.response?.data?.detail || 'Failed to login'
            };
            return {
                success: false,
                error: error.response?.data?.detail || 'Failed to login'
            };
        }
    }

    async function logout() {
        try {
            await axios.post("/api/user/logout/");
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            userInfo.value = {
                is_authenticated: false,
                username: "",
                password: "",
                is_staff: false
            };
        }
    }

    return {
        userInfo,
        checkLogin,
        login,
        logout
    }
})