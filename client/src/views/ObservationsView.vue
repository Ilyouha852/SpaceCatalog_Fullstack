<script setup>
import { onBeforeMount, ref, computed } from "vue";
import axios from "axios";
import Cookies from "js-cookie";
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";

const userInfoStore = useUserInfoStore();
const { is_authenticated, is_superuser } = storeToRefs(userInfoStore);

onBeforeMount(() => {
  axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
});

const loading = ref(false);
const loadingExport = ref(false);
const observations = ref([]);
const astronomers = ref([]);
const researchers = ref([]);
const observationToAdd = ref({});
const observationToEdit = ref({});

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

const resetFilters = () => {
  searchQuery.value = "";
};

async function fetchObservations() {
  loading.value = true;
  let url = "/api/observations/";
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) {
    url = "/api/astronomers/my-observations/";
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
  try {
    await axios.put(`/api/observations/${observationToEdit.value.id}/`, {
      ...observationToEdit.value,
    });
    await fetchObservations();
  } catch (error) {
    console.error("Ошибка при обновлении наблюдения:", error);
    alert("Ошибка при обновлении наблюдения");
  }
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
  try {
    const response = await axios.get('/api/observations/export-excel/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'observations.xlsx');
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

const canCreateObservations = computed(() => {
  if (is_superuser.value || userInfoStore.isAdmin()) {
    return true;
  }
  
  if (userInfoStore.isAstronomer && userInfoStore.isAstronomer()) {
    return true;
  }
  
  return false;
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
  <div class="container-fluid">
    <div class="p-2">
      <div v-if="is_authenticated">
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="card-title mb-0">Поиск</h6>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    v-model="searchQuery"
                    placeholder="Поиск по ФИО астронома или исследователя..."
                  />
                  <button 
                    v-if="searchQuery" 
                    @click="resetFilters" 
                    class="btn btn-outline-secondary"
                  >
                    Сбросить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <form v-if="canCreateObservations && !userInfoStore.isResearcher()" @submit.prevent.stop="onObservationAdd">
          <div class="row">
            <div class="col">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="observationToAdd.astronomer"
                  required
                >
                  <option value="" disabled selected>Выберите астронома</option>
                  <option :key="d.id" :value="d.id" v-for="d in astronomers">
                    {{ d.name }}
                  </option>
                </select>
                <label for="floatingInput">Астроном</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="observationToAdd.researcher"
                  required
                >
                  <option value="" disabled selected>Выберите исследователя</option>
                  <option :key="p.id" :value="p.id" v-for="p in researchers">
                    {{ p.name }}
                  </option>
                </select>
                <label for="floatingInput">Исследователь</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating mb-3">
                <input
                  type="datetime-local"
                  class="form-control"
                  v-model="observationToAdd.date_time"
                  required
                />
                <label for="floatingInput">Дата и время</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="observationToAdd.status"
                  required
                >
                  <option value="" disabled selected>Выберите статус</option>
                  <option value="pending">Ожидание</option>
                  <option value="planned">Запланировано</option>
                  <option value="completed">Завершено</option>
                  <option value="cancelled">Отменено</option>
                </select>
                <label for="floatingInput">Статус</label>
              </div>
            </div>
            <div class="col-auto">
              <button class="btn btn-primary">Добавить</button>
            </div>
          </div>
        </form>

        <div class="mb-3">
          Всего записей: {{ observations.length }}
          <span v-if="searchQuery"> | Найдено: {{ filteredObservations.length }}</span>
        </div>

        <div class="mb-3">
          <button @click="exportToExcel" class="btn btn-success" :disabled="loadingExport">
            <i class="bi bi-file-earmark-excel"></i>
            {{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}
          </button>
        </div>

        <div>
          <div v-for="item in filteredObservations" :key="item.id" class="observation-item">
            <div><strong>Астроном:</strong> {{ getAstronomerName(item.astronomer) }}</div>
            <div><strong>Исследователь:</strong> {{ getResearcherName(item.researcher) }}</div>
            <div><strong>Дата:</strong> {{ new Date(item.date_time).toLocaleString('ru-RU') }}</div>
            <div><strong>Статус:</strong> {{ 
              item.status === 'pending' ? 'Ожидание' :
              item.status === 'planned' ? 'Запланировано' :
              item.status === 'completed' ? 'Завершено' :
              item.status === 'cancelled' ? 'Отменено' : item.status 
            }}</div>
            <button
              v-if="canCreateObservations"
              class="btn btn-sm btn-outline-secondary me-2"
              @click="OnObservationEdit(item)"
              data-bs-toggle="modal"
              data-bs-target="#editObservationModal"
            >
              Редактировать
            </button>
            <button 
              v-if="canCreateObservations"
              class="btn btn-sm btn-danger" 
              @click="OnObservationRemove(item)"
            >
              Удалить
            </button>
          </div>
          
          <div v-if="filteredObservations.length === 0 && searchQuery" class="alert alert-info mt-3">
            Записи не найдены
          </div>
        </div>
      </div>
      <div v-else>Вы не авторизованы</div>
    </div>

    <div
      class="modal fade"
      id="editObservationModal"
      tabindex="-1"
      aria-labelledby="editObservationModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="editObservationModalLabel">
              Редактировать наблюдение
            </h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-12">
                <div class="form-floating">
                  <select
                    class="form-select"
                    v-model="observationToEdit.astronomer"
                    required
                  >
                    <option value="" disabled selected>Выберите астронома</option>
                    <option :key="d.id" :value="d.id" v-for="d in astronomers">
                      {{ d.name }}
                    </option>
                  </select>
                  <label>Астроном</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <select
                    class="form-select"
                    v-model="observationToEdit.researcher"
                    required
                  >
                    <option value="" disabled selected>Выберите исследователя</option>
                    <option :key="p.id" :value="p.id" v-for="p in researchers">
                      {{ p.name }}
                    </option>
                  </select>
                  <label>Исследователь</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="datetime-local"
                    class="form-control"
                    v-model="observationToEdit.date_time"
                    required
                  />
                  <label>Дата и время</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <select
                    class="form-select"
                    v-model="observationToEdit.status"
                    required
                  >
                    <option value="" disabled selected>Выберите статус</option>
                    <option value="pending">Ожидание</option>
                    <option value="planned">Запланировано</option>
                    <option value="completed">Завершено</option>
                    <option value="cancelled">Отменено</option>
                  </select>
                  <label>Статус</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
            >
              Закрыть
            </button>
            <button
              type="button"
              class="btn btn-primary"
              data-bs-dismiss="modal"
              @click="onObservationUpdate"
            >
              Сохранить изменения
            </button>
          </div>
        </div>
      </div>
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