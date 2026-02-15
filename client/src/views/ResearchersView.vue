<script setup>
import { computed, onBeforeMount, ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";  

const userInfoStore = useUserInfoStore();  
const { is_superuser, is_authenticated, user_type } = storeToRefs(userInfoStore);  

onBeforeMount(() => {
  axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
});

const loading = ref(false);
const loadingExport = ref(false);

const researchers = ref([]);
const researcherToAdd = ref({});
const researcherToEdit = ref(null);

const searchQuery = ref("");
const searchPhone = ref("");
const selectedBirthDate = ref("");

const filteredResearchers = computed(() => {
  if (!researchers.value.length) return [];

  return researchers.value.filter(researcher => {

    if (searchQuery.value) {
      const researcherName = researcher.name?.toLowerCase() || '';
      const query = searchQuery.value.toLowerCase();
      
      if (!researcherName.includes(query)) {
        return false;
      }
    }

    if (searchPhone.value) {
      const phone = researcher.phone?.toLowerCase() || '';
      const query = searchPhone.value.toLowerCase();
      
      if (!phone.includes(query)) {
        return false;
      }
    }

    if (selectedBirthDate.value && researcher.birth_date !== selectedBirthDate.value) {
      return false;
    }

    return true;
  });
});

const resetFilters = () => {
  searchQuery.value = "";
  searchPhone.value = "";
  selectedBirthDate.value = "";
};

async function fetchResearchers() {
  loading.value = true;
  const r = await axios.get("/api/researchers/");
  researchers.value = r.data;
  loading.value = false;
}

async function onResearcherAdd() {
  await axios.post("/api/researchers/", {
    ...researcherToAdd.value,
  });
  await fetchResearchers();
}

async function OnResearcherEdit(researcher) {
  researcherToEdit.value = { ...researcher };
}

async function onResearcherUpdate() {
  try {
    await axios.put(`/api/researchers/${researcherToEdit.value.id}/`, {
      ...researcherToEdit.value,
    });
    await fetchResearchers();
    researcherToEdit.value = null;
  } catch (error) {
    console.error("Ошибка при обновлении исследователя:", error);
    alert("Ошибка при обновлении исследователя");
  }
}

async function OnResearcherRemove(researcher) {
  await axios.delete(`/api/researchers/${researcher.id}/`);
  await fetchResearchers();
}

onBeforeMount(async () => {
  await fetchResearchers();
});

async function exportToExcel() {
  loadingExport.value = true;
  try {
    const response = await axios.get('/api/researchers/export-excel/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'researchers.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (e) {
    console.error('Ошибка при экспорте:', e);
    alert('Ошибка при экспорте данных');
  } finally {
    loadingExport.value = false;
  }
}
</script>

<template>
  <div>
    <div class="p-2">
      <div v-if="is_authenticated">
        <el-card class="mb-4">
          <template #header>Фильтры исследователей</template>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-input v-model="searchQuery" placeholder="Поиск по имени...">
                <template #prefix><i class="bi bi-search"></i></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-date-picker v-model="selectedBirthDate" type="date" placeholder="Дата рождения" style="width:100%" />
            </el-col>
            <el-col :span="6">
              <el-input v-model="searchPhone" placeholder="Поиск по телефону...">
                <template #prefix><i class="bi bi-telephone"></i></template>
              </el-input>
            </el-col>
            <el-col :span="4">
              <el-button @click="resetFilters" type="info" plain>Сбросить</el-button>
            </el-col>
          </el-row>
        </el-card>

        <div v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')">
          <el-card class="mb-4">
            <template #header><h5>Добавить исследователя</h5></template>
            <el-form @submit.prevent.stop="onResearcherAdd" label-position="top">
              <el-row :gutter="12" align="middle">
                <el-col :span="10"><el-input v-model="researcherToAdd.name" placeholder="ФИО исследователя" /></el-col>
                <el-col :span="6"><el-date-picker v-model="researcherToAdd.birth_date" type="date" placeholder="Дата рождения" style="width:100%" /></el-col>
                <el-col :span="6"><el-input v-model="researcherToAdd.phone" placeholder="Телефон" /></el-col>
                <el-col :span="2"><el-button type="primary" native-type="submit">Добавить</el-button></el-col>
              </el-row>
            </el-form>
          </el-card>
        </div>

        <div v-if="researcherToEdit" class="mb-3">
          <el-card>
            <template #header><h5>Редактировать исследователя</h5></template>
            <el-row :gutter="12" align="middle">
              <el-col :span="8"><el-input v-model="researcherToEdit.name" placeholder="ФИО исследователя" /></el-col>
              <el-col :span="6"><el-date-picker v-model="researcherToEdit.birth_date" type="date" style="width:100%" /></el-col>
              <el-col :span="6"><el-input v-model="researcherToEdit.phone" /></el-col>
              <el-col :span="4"><el-button type="primary" @click="onResearcherUpdate">Сохранить</el-button><el-button @click="researcherToEdit = null">Отмена</el-button></el-col>
            </el-row>
          </el-card>
        </div>

        <div v-if="loading">Загрузка данных...</div>

        <div class="mb-3">
          <el-button @click="exportToExcel" type="success" :disabled="loadingExport">{{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}</el-button>
        </div>

        <el-row :gutter="16">
          <el-col :span="8" v-for="item in filteredResearchers" :key="item.id">
            <el-card class="researcher-card">
              <div><strong>{{ item.name }}</strong></div>
              <div class="text-muted">{{ item.birth_date }}</div>
              <div>{{ item.phone }}</div>
              <div class="mt-2">
                <el-button v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')" size="mini" @click="OnResearcherEdit(item)">Редактировать</el-button>
                <el-button v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')" size="mini" type="danger" @click="OnResearcherRemove(item)">Удалить</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      <div v-else>Вы не авторизованы</div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.researcher-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto auto auto auto;
  gap: 16px;
  align-items: center;
  align-content: center;
}
</style>