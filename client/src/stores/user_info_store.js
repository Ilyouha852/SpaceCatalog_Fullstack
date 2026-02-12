import { ref } from "vue";
import axios from "axios";
import { defineStore } from "pinia";

export const useUserInfoStore = defineStore("userInfoStore", () => {
    const is_authenticated = ref(false);
    const username = ref("");
    const user_type = ref("");
    const can_see_statistics = ref(false);
    const user_id = ref(null);
    const is_superuser = ref(false);
  
    const permissions = ref([]);

    async function fetchUserInfo() {
        const r = await axios.get("/api/users/my/");
        is_authenticated.value = r.data.is_authenticated;
        username.value = r.data.username;
        user_type.value = r.data.user_type;
        can_see_statistics.value = r.data.can_see_statistics;
        user_id.value = r.data.user_id;
        is_superuser.value = r.data.is_superuser;
       
        permissions.value = r.data.permissions;
    }

    function hasPermission(permission) {
        return permissions.value.includes(permission);
    }
    function isAstronomer() {
        return user_type.value === 'astronomer';
    }
    
    function getAstronomerId() {
        return user_id.value;
    }
    
    function isResearcher() {
        return user_type.value === 'researcher';
    }
    
    function getResearcherId() {
        if (user_type.value === 'researcher') {
            return user_id.value;
        }
        return null;
    }
    
    function isAdmin() {
        return user_type.value === 'admin' || is_superuser.value;
    }

    return {
        is_authenticated,
        username,
        user_type,
        can_see_statistics,
        user_id,
        is_superuser,
        
        permissions,
        fetchUserInfo,
        hasPermission,
        isAstronomer,
        getAstronomerId,
        isResearcher,
        getResearcherId,
        isAdmin
    };
});