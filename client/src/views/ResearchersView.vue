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
const researcherToEdit = ref({});

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
  <div class="container-fluid">
      <div class="p-2">
        <div v-if="is_authenticated">
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="card-title mb-0">Фильтры</h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-4">
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control"
                      v-model="searchQuery"
                      placeholder="Поиск по имени..."
                    />
                  </div>
                </div>
                <div class="col-md-2">
                  <input
                    type="date"
                    class="form-control"
                    v-model="selectedBirthDate"
                    placeholder="Дата рождения"
                  />
                </div>
                <div class="col-md-4">
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-telephone"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control"
                      v-model="searchPhone"
                      placeholder="Поиск по телефону..."
                    />
                  </div>
                </div>
                <div class="col-md-2">
                  <button @click="resetFilters" class="btn btn-outline-secondary w-100">
                    Сбросить
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')">
            <form @submit.prevent.stop="onResearcherAdd">
              <div class="row">
                <div class="col">
                  <div class="form-floating mb-3">
                    <input
                      type="text"
                      class="form-control"
                      v-model="researcherToAdd.name"
                      required
                    />
                    <label for="floatingInput">ФИО исследователя</label>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="form-floating mb-3">
                    <input
                      type="date"
                      class="form-control"
                      v-model="researcherToAdd.birth_date"
                      required
                    />
                    <label for="floatingInput">Дата рождения</label>
                  </div>
                </div>
                <div class="col-auto">
                  <div class="form-floating mb-3">
                    <input
                      type="tel"
                      class="form-control"
                      v-model="researcherToAdd.phone"
                      required
                    />
                    <label for="floatingInput">Телефон</label>
                  </div>
                </div>
                <div class="col-auto">
                  <button class="btn btn-primary">Добавить</button>
                </div>
              </div>
            </form>
          </div>

          <div class="mb-3">
            <button @click="exportToExcel" class="btn btn-success" :disabled="loadingExport">
              <i class="bi bi-file-earmark-excel"></i>
              {{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}
            </button>
          </div>

          <div>
            <div v-for="item in filteredResearchers" :key="item.id" class="researcher-item">
              <div>{{ item.name }}</div>
              <div>{{ item.birth_date }}</div>
              <div>{{ item.phone }}</div>
              <button
                v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')"
                class="btn btn-sm btn-outline-secondary me-2"
                @click="OnResearcherEdit(item)"
                data-bs-toggle="modal"
                data-bs-target="#editResearcherModal"
              >
                Редактировать
              </button>
              <button 
                v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_patients')"
                class="btn btn-sm btn-danger" 
                @click="OnResearcherRemove(item)"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
        <div v-else>Вы не авторизованы</div>
    </div>

    <div
      class="modal fade"
      id="editResearcherModal"
      tabindex="-1"
      aria-labelledby="editResearcherModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="editResearcherModalLabel">
              Редактировать исследователя
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
                  <input
                    type="text"
                    class="form-control"
                    v-model="researcherToEdit.name"
                    placeholder="ФИО исследователя"
                  />
                  <label>ФИО исследователя</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="date"
                    class="form-control"
                    v-model="researcherToEdit.birth_date"
                    placeholder="Дата рождения"
                  />
                  <label>Дата рождения</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="tel"
                    class="form-control"
                    v-model="researcherToEdit.phone"
                    placeholder="Телефон"
                  />
                  <label>Телефон</label>
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
              @click="onResearcherUpdate"
            >
              Сохранить изменения
            </button>
          </div>
        </div>
      </div>
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