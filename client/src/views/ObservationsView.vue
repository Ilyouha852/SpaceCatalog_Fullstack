<script setup>
import { onBeforeMount, ref, computed } from "vue";
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";

import axios from 'axios';
import Cookies from 'js-cookie'

axios.defaults.withCredentials = true;
axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");

const userInfoStore = useUserInfoStore();
const { is_authenticated, is_superuser } = storeToRefs(userInfoStore);

const loading = ref(false);
const loadingExport = ref(false);
const observations = ref([]);
const astronomers = ref([]);
const researchers = ref([]);
const observationToAdd = ref({});
const observationToEdit = ref(null);

const searchQuery = ref("");

const filteredObservations = computed(() => {
  if (!searchQuery.value.trim()) {
    return observations.value;
  }
  
  const query = searchQuery.value.toLowerCase().trim();
  
  return observations.value.filter(observation => {
    const astronomer = astronomers.value.find(d => d.id === (observation.astronomer || observation.astronomer));
    const researcher = researchers.value.find(p => p.id === (observation.researcher || observation.researcher));
    
    const astronomerName = astronomer?.name?.toLowerCase() || "";
    const researcherName = researcher?.name?.toLowerCase() || "";
    
    return astronomerName.includes(query) || researcherName.includes(query);
  });
});

const astronomerOptions = computed(() => {
  if ((userInfoStore.isAdmin && userInfoStore.isAdmin()) || is_superuser.value) return astronomers.value || [];
  if (userInfoStore.isResearcher && userInfoStore.isResearcher()) return astronomers.value || [];
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) return (astronomers.value || []).filter(a => a.user_id && a.user_id === userInfoStore.user_id);
  return [];
});

const researcherOptions = computed(() => {
  if ((userInfoStore.isAdmin && userInfoStore.isAdmin()) || is_superuser.value) return researchers.value || [];
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) return researchers.value || [];
  if (userInfoStore.isResearcher && userInfoStore.isResearcher()) return (researchers.value || []).filter(r => r.user_id && r.user_id === userInfoStore.user_id);
  return [];
});

const resetFilters = () => {
  searchQuery.value = "";
};

async function fetchObservations() {
  loading.value = true;
  let url = "/api/observations/";
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) {
    url = "/api/astronomers/my-appointments/";
  } else if (userInfoStore.isResearcher && userInfoStore.isResearcher()) {
    url = "/api/observations/";
  }
  
  const r = await axios.get(url);
  observations.value = r.data;
  loading.value = false;
}

async function fetchAstronomers() {
  const r = await axios.get("/api/astronomers/");
  astronomers.value = r.data;
}

async function fetchResearchers() {
  const r = await axios.get("/api/researchers/");
  researchers.value = r.data;
}

async function onObservationAdd() {
  await axios.post("/api/observations/", {
    ...observationToAdd.value,
  });
  await fetchObservations();
  observationToAdd.value = {};
}

async function OnObservationEdit(observation) {
  observationToEdit.value = { ...observation };
}

async function onObservationUpdate() {
  await axios.put(`/api/observations/${observationToEdit.value.id}/`, {
    ...observationToEdit.value,
  });
  await fetchObservations();
  observationToEdit.value = null;
}

async function OnObservationRemove(observation) {
  await axios.delete(`/api/observations/${observation.id}/`);
  await fetchObservations();
}

onBeforeMount(async () => {
  await fetchAstronomers();
  await fetchResearchers();
  await fetchObservations();
});

async function exportToExcel() {
  loadingExport.value = true;

  const response = await axios.get('/api/observations/export-excel/', { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'observations.xlsx');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  loadingExport.value = false;
}

const canCreateObservations = computed(() => {
  if (is_superuser.value || userInfoStore.isAdmin()) {
    return true;
  }
  
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) {
    return true;
  }
  
  return false;
});

const isAdmin = computed(() => {
  return is_superuser.value || (userInfoStore.isAdmin && userInfoStore.isAdmin());
});

const getAstronomerName = (astronomerId) => {
  const astronomer = astronomers.value.find(d => d.id === astronomerId) || astronomers.value.find(d => d.id === (astronomerId?.astronomer || astronomerId));
  return astronomer?.name || `Астроном ID: ${astronomerId}`;
};

const getResearcherName = (researcherId) => {
  const researcher = researchers.value.find(p => p.id === researcherId) || researchers.value.find(p => p.id === (researcherId?.researcher || researcherId));
  return researcher?.name || `Исследователь ID: ${researcherId}`;
};
</script>

<template>
  <div>
    <div class="p-2">
      <div v-if="is_authenticated">
        <el-card class="mb-4">
          <template #header><span>Поиск наблюдений</span></template>
          <el-row>
            <el-col :span="24">
              <el-input v-model="searchQuery" placeholder="Поиск по ФИО астронома или исследователя..." style="width:100%">
                <template #prefix><i class="bi bi-search"></i></template>
                <template #suffix>
                  <el-button v-if="searchQuery" @click="resetFilters" type="text">Сбросить</el-button>
                </template>
              </el-input>
            </el-col>
          </el-row>
          <div class="mt-2 text-muted">Найдено наблюдений: {{ filteredObservations.length }}</div>
        </el-card>

        <div v-if="canCreateObservations || (userInfoStore.isResearcher && userInfoStore.isResearcher())" class="mb-4">
          <el-card>
            <template #header><h5>Добавить наблюдение</h5></template>
            <el-form @submit.prevent.stop="onObservationAdd" label-position="top">
              <el-row :gutter="12">
                <el-col :span="6">
                  <el-select v-model="observationToAdd.astronomer" placeholder="Выберите астронома">
                    <el-option v-for="d in astronomerOptions" :key="d.id" :label="d.name" :value="d.id" />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-select v-model="observationToAdd.researcher" placeholder="Выберите исследователя">
                    <el-option v-for="p in researcherOptions" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-col>
                <el-col :span="6"><el-date-picker v-model="observationToAdd.date_time" type="datetime" placeholder="Дата и время" style="width:100%" /></el-col>
                <el-col :span="4">
                  <el-select v-model="observationToAdd.status" placeholder="Выберите статус">
                    <el-option label="Ожидание" value="pending" />
                    <el-option label="Запланировано" value="planned" />
                    <el-option label="Завершено" value="completed" />
                    <el-option label="Отменено" value="cancelled" />
                  </el-select>
                </el-col>
                <el-col :span="2"><el-button type="primary" native-type="submit">Добавить</el-button></el-col>
              </el-row>
            </el-form>
          </el-card>
        </div>

        <div v-if="observationToEdit" class="mb-3">
          <el-card>
            <template #header><h5>Редактировать наблюдение</h5></template>
            <el-row :gutter="12" align="middle">
              <el-col :span="4">
                <el-select v-model="observationToEdit.astronomer" placeholder="Астроном">
                  <el-option v-for="d in astronomers" :key="d.id" v-if="userInfoStore.isAdmin() || d.user_id === userInfoStore.user_id" :label="d.name" :value="d.id" />
                </el-select>
              </el-col>
              <el-col :span="4">
                <el-select v-model="observationToEdit.researcher" placeholder="Исследователь">
                  <el-option v-for="p in researchers" :key="p.id" v-if="userInfoStore.isAdmin() || p.user_id === userInfoStore.user_id" :label="p.name" :value="p.id" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-date-picker v-model="observationToEdit.date_time" type="datetime" style="width:100%" />
              </el-col>
              <el-col :span="4">
                <el-select v-model="observationToEdit.status">
                  <el-option label="Ожидание" value="pending" />
                  <el-option label="Запланировано" value="planned" />
                  <el-option label="Завершено" value="completed" />
                  <el-option label="Отменено" value="cancelled" />
                </el-select>
              </el-col>
              <el-col :span="24" class="mt-2">
                <el-button type="success" @click="onObservationUpdate">Сохранить</el-button>
                <el-button @click="observationToEdit = null">Отмена</el-button>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div v-if="loading">Загрузка данных...</div>
        <div class="mb-3" v-if="!loading"><el-button @click="exportToExcel" type="success" :disabled="loadingExport">{{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}</el-button></div>

        <el-row :gutter="16">
          <el-col :span="8" v-for="item in filteredObservations" :key="item.id">
            <el-card class="mb-2">
              <div class="card-grid">
                <div><strong>{{ getAstronomerName(item.astronomer) }}</strong></div>
                <div class="text-muted">{{ getResearcherName(item.researcher) }}</div>
                <div>{{ new Date(item.date_time).toLocaleString('ru-RU') }}</div>
                <div class="status">{{ item.status === 'pending' ? 'Ожидание' : item.status === 'planned' ? 'Запланировано' : item.status === 'completed' ? 'Завершено' : item.status === 'cancelled' ? 'Отменено' : item.status }}</div>
                <div class="mt-2 actions">
                  <el-button v-if="isAdmin" size="mini" @click="OnObservationEdit(item)">Редактировать</el-button>
                  <el-button v-if="isAdmin" size="mini" type="danger" @click="OnObservationRemove(item)">Удалить</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-empty v-if="filteredObservations.length === 0 && searchQuery" description="Записи не найдены" />
      </div>
      <div v-else>Вы не авторизованы</div>
    </div>
  </div>
</template>

<style scoped>
.observation-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr 1fr auto auto auto auto;
  gap: 16px;
  align-items: center;
  align-content: center;
}
</style>