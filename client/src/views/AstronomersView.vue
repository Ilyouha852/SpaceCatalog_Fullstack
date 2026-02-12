<script setup>
import { onBeforeMount, ref, computed } from "vue";
import axios from "axios";
import Cookies from "js-cookie";
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";  

const userInfoStore = useUserInfoStore();  
const { is_authenticated, is_superuser, user_type } = storeToRefs(userInfoStore);  

onBeforeMount(() => {
  axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");
});

const loading = ref(false);
const loadingExport = ref(false);

const astronomers = ref([]);
const observatories = ref([]);
const astronomerToAdd = ref({});
const astronomerToEdit = ref({});

const astronomerAddPictureRef = ref();
const astronomerEditPictureRef = ref();
const astronomerAddImageUrl = ref();
const astronomerEditImageUrl = ref();
const hasAstronomerEditPicture = ref(false);

const searchQuery = ref("");
const selectedObservatory = ref("");
const selectedSpecialization = ref("");

const observatoriesById = computed(() => {
  const result = {};
  observatories.value.forEach(observatory => {
    result[observatory.id] = observatory.name;
  });
  return result;
});

const specializationsList = computed(() => {
  const specializations = new Set();
  astronomers.value.forEach(astronomer => {
    if (astronomer.specialization) {
      specializations.add(astronomer.specialization);
    }
  });
  return Array.from(specializations).sort();
});

const filteredAstronomers = computed(() => {
  if (!astronomers.value.length) return [];

  return astronomers.value.filter(astronomer => {
    if (searchQuery.value) {
      const astronomerName = astronomer.name?.toLowerCase() || '';
      const query = searchQuery.value.toLowerCase();
      
      if (!astronomerName.includes(query)) {
        return false;
      }
    }

    if (selectedObservatory.value && astronomer.polyclinic != selectedObservatory.value) {
      return false;
    }

    if (selectedSpecialization.value && astronomer.specialization !== selectedSpecialization.value) {
      return false;
    }

    return true;
  });
});

const resetFilters = () => {
  searchQuery.value = "";
  selectedObservatory.value = "";
  selectedSpecialization.value = "";
};

async function fetchObservatories() {
  const r = await axios.get("/api/observatories/");
  observatories.value = r.data;
}

async function fetchAstronomers() {
  loading.value = true;
  const r = await axios.get("/api/astronomers/");
  astronomers.value = r.data;
  loading.value = false;
}

async function onAstronomerAdd() {
  const formData = new FormData();

  if (astronomerAddPictureRef.value && astronomerAddPictureRef.value.files[0]) {
    formData.set("picture", astronomerAddPictureRef.value.files[0]);
  }
  formData.set("name", astronomerToAdd.value.name);
  formData.set("specialization", astronomerToAdd.value.specialization);
  formData.set("observatory", astronomerToAdd.value.observatory);

  try {
    await axios.post("/api/astronomers/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    await fetchAstronomers();

    astronomerToAdd.value = {};
    astronomerAddPictureRef.value = "";
    astronomerAddImageUrl.value = "";
  } catch (error) {
    console.error("Ошибка при создании астронома:", error);
  }
}

async function astronomerAddPictureChange() {
  if (astronomerAddPictureRef.value && astronomerAddPictureRef.value.files[0]) {
    astronomerAddImageUrl.value = URL.createObjectURL(
      astronomerAddPictureRef.value.files[0]
    );
  }
}

async function OnAstronomerEdit(astronomer) {
  astronomerToEdit.value = { ...astronomer };
  astronomerEditImageUrl.value = '';
  if (astronomerEditPictureRef.value) {
    astronomerEditPictureRef.value.value = '';
  }
}

async function onAstronomerUpdate() {
  try {
    const formData = new FormData();
    formData.set('name', astronomerToEdit.value.name);
    formData.set('specialization', astronomerToEdit.value.specialization);
    formData.set('observatory', astronomerToEdit.value.observatory);

    if (astronomerEditPictureRef.value && astronomerEditPictureRef.value.files[0]) {
      formData.append('picture', astronomerEditPictureRef.value.files[0]);
    }

    await axios.put(`/api/astronomers/${astronomerToEdit.value.id}/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    await fetchAstronomers();
  } catch (error) {
    console.error("Ошибка при обновлении астронома:", error);
    alert("Ошибка при обновлении астронома");
  }
}

async function astronomerEditPictureChange() {
  if (astronomerEditPictureRef.value && astronomerEditPictureRef.value.files[0]) {
    astronomerEditImageUrl.value = URL.createObjectURL(
      astronomerEditPictureRef.value.files[0]
    );
    hasAstronomerEditPicture.value = true;
  }
}

async function OnAstronomerRemove(astronomer) {
  await axios.delete(`/api/astronomers/${astronomer.id}/`);
  await fetchAstronomers();
}

onBeforeMount(async () => {
  await fetchObservatories();
  await fetchAstronomers();
});

async function exportToExcel() {
  loadingExport.value = true;
  try {
    const response = await axios.get('/api/astronomers/export-excel/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'astronomers.xlsx');
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

const showZoomImageContainer = ref(false);
const zoomImageUrl = ref("");

function showZoomImage(imageUrl) {
  zoomImageUrl.value = imageUrl;
  showZoomImageContainer.value = true;
}

function hideZoomImage() {
  showZoomImageContainer.value = false;
}

function getImageUrl(astronomer) {
  if (!astronomer.picture) return null;
  
  if (astronomer.picture.startsWith('http')) {
    return astronomer.picture;
  }
  
  return `http://localhost:8000${astronomer.picture}`;
}
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <div v-if="is_authenticated">
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="card-title mb-0">Фильтры астрономов</h6>
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
                    placeholder="Поиск по имени астронома..."
                  />
                </div>
              </div>
              <div class="col-md-3">
                <select class="form-select" v-model="selectedObservatory">
                  <option value="">Все обсерватории</option>
                  <option :value="p.id" v-for="p in observatories" :key="p.id">
                    {{ p.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-3">
                <select class="form-select" v-model="selectedSpecialization">
                  <option value="">Все специализации</option>
                  <option :value="spec" v-for="spec in specializationsList" :key="spec">
                    {{ spec }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <button @click="resetFilters" class="btn btn-outline-secondary w-100">
                  Сбросить
                </button>
              </div>
            </div>
            <div class="mt-2 text-muted">
              Найдено астрономов: {{ filteredAstronomers.length }}
            </div>
          </div>
        </div>

        <form v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')" @submit.prevent.stop="onAstronomerAdd">
          <div class="row">
            <div class="col">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="astronomerToAdd.name"
                  required
                />
                <label for="floatingInput">ФИО астронома</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating mb-3">
                <input
                  type="text"
                  class="form-control"
                  v-model="astronomerToAdd.specialization"
                  required
                />
                <label for="floatingInput">Специализация</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating mb-3">
                <select
                  class="form-select"
                  v-model="astronomerToAdd.observatory"
                  required
                >
                  <option value="" disabled selected>Выберите обсерваторию</option>
                  <option :key="p.id" :value="p.id" v-for="p in observatories">
                    {{ p.name }}
                  </option>
                </select>
                <label for="floatingInput">Обсерватория</label>
              </div>
            </div>
            <div class="col-auto">
              <input
                class="form-control"
                type="file"
                ref="astronomerAddPictureRef"
                @change="astronomerAddPictureChange"
              />
            </div>
            <div class="col-auto">
              <img
                :src="astronomerAddImageUrl"
                style="max-height: 60px"
                alt="Изображение"
                v-if="astronomerAddImageUrl"
                @click="showZoomImage(astronomerAddImageUrl)"
              />
            </div>
            <div class="col-auto">
              <button class="btn btn-primary">Добавить</button>
            </div>
          </div>
        </form>

        <div v-if="loading">Гружу...</div>

        <div class="mb-3">
          <button @click="exportToExcel" class="btn btn-success" :disabled="loadingExport">
            <i class="bi bi-file-earmark-excel"></i>
            {{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}
          </button>
        </div>

        <div>
          <div v-for="item in filteredAstronomers" :key="item.id" class="astronomer-item">
            <div>{{ item.name }}</div>
            <div>{{ item.specialization }}</div>
            <div>{{ observatoriesById[item.observatory] }}</div>
            <div v-show="item.picture">
              <img
                :src="getImageUrl(item)"
                style="max-height: 60px"
                @click="showZoomImage(getImageUrl(item))"
              />
            </div>
            <button
              v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')"
              class="btn btn-sm btn-outline-secondary me-2"
              @click="OnAstronomerEdit(item)"
              data-bs-toggle="modal"
              data-bs-target="#editAstronomerModal"
            >
              Редактировать
            </button>
            <button 
              v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')"
              class="btn btn-sm btn-danger" 
              @click="OnAstronomerRemove(item)"
            >
              Удалить
            </button>
          </div>
        </div>

        <div
          class="zoom-image-container"
          :class="{ active: showZoomImageContainer }"
          @click="hideZoomImage"
        >
          <img :src="zoomImageUrl" alt="Увеличенное изображение" />
        </div>
      </div>
      <div v-else>Вы не авторизованы</div>
    </div>

    <div
      class="modal fade"
      id="editAstronomerModal"
      tabindex="-1"
      aria-labelledby="editAstronomerModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="editAstronomerModalLabel">
              Редактировать астронома
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
                    v-model="astronomerToEdit.name"
                    placeholder="ФИО астронома"
                  />
                  <label>ФИО астронома</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="astronomerToEdit.specialization"
                    placeholder="Специализация"
                  />
                  <label>Специализация</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <select
                    class="form-select"
                    v-model="astronomerToEdit.observatory"
                    required
                  >
                    <option value="" disabled selected>Выберите обсерваторию</option>
                    <option :key="p.id" :value="p.id" v-for="p in observatories">
                      {{ p.name }}
                    </option>
                  </select>
                  <label>Обсерватория</label>
                </div>
              </div>
              <div class="col-12">
                <div class="mb-3">
                  <label class="form-label">Изменить изображение</label>
                  <input 
                    class="form-control" 
                    type="file" 
                    ref="astronomerEditPictureRef" 
                    @change="astronomerEditPictureChange"
                    accept="image/*"
                  >
                  <div v-if="getImageUrl(astronomerToEdit)" class="mt-2">
                    <p class="small text-muted mb-1">Текущее изображение:</p>
                    <img 
                      :src="getImageUrl(astronomerToEdit)" 
                      :alt="astronomerToEdit.name"
                      style="max-height: 100px;"
                      class="img-thumbnail"
                    >
                  </div>
                  <div v-if="astronomerEditImageUrl" class="mt-2">
                    <p class="small text-muted mb-1">Новое изображение:</p>
                    <img 
                      :src="astronomerEditImageUrl" 
                      alt="Новое изображение"
                      style="max-height: 100px;"
                      class="img-thumbnail"
                    >
                  </div>
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
              data-bs-dismiss="modal"
              type="button"
              class="btn btn-primary"
              @click="onAstronomerUpdate"
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
.astronomer-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto auto auto auto auto;
  gap: 16px;
  align-items: center;
  align-content: center;
}

img {
  cursor: pointer;
}

.zoom-image-container {
  position: fixed;
  left: 0;
  top: 40px;
  right: 0;
  bottom: 0;
  display: block;
  padding: 1rem;
  backdrop-filter: blur(4px);
  z-index: 100;
  transform: scale(0.2, 0.2);
  transition: all 0.2s ease-out;
  opacity: 0;
  height: 0;
  overflow: hidden;
}

.zoom-image-container.active {
  opacity: 1;
  transform: scale(1, 1);
  height: auto;
}

.zoom-image-container img {
  height: 100%;
  width: 100%;
  object-fit: contain;
}
</style>