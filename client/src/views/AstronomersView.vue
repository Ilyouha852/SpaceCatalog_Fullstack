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
const astronomerToEdit = ref(null);

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
    astronomerToEdit.value = null;
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

const currentImageUrl = ref('');
const imageDialogVisible = ref(false);

function openImagePreviewModal(url) {
  currentImageUrl.value = url;
  imageDialogVisible.value = true;
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
  <div>
    <div class="p-2">
      <div v-if="is_authenticated">
        <el-card class="mb-4">
          <template #header>
            <span>Фильтры астрономов</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-input v-model="searchQuery" placeholder="Поиск по имени астронома...">
                <template #prefix><i class="bi bi-search"></i></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select v-model="selectedObservatory" placeholder="Все обсерватории" clearable>
                <el-option v-for="p in observatories" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="selectedSpecialization" placeholder="Все специализации" clearable>
                <el-option v-for="spec in specializationsList" :key="spec" :label="spec" :value="spec" />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button @click="resetFilters" type="info" plain>Сбросить</el-button>
            </el-col>
          </el-row>
          <div class="mt-2 text-muted">Найдено астрономов: {{ filteredAstronomers.length }}</div>
        </el-card>

        <div v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')">
          <el-card class="mb-4">
            <template #header><h5>Добавить астронома</h5></template>
            <el-form @submit.prevent.stop="onAstronomerAdd" label-position="top">
              <el-row :gutter="12" align="middle">
                <el-col :span="6"><el-input v-model="astronomerToAdd.name" placeholder="ФИО астронома" /></el-col>
                <el-col :span="6"><el-input v-model="astronomerToAdd.specialization" placeholder="Специализация" /></el-col>
                <el-col :span="6">
                  <el-select v-model="astronomerToAdd.observatory" placeholder="Выберите обсерваторию">
                    <el-option v-for="p in observatories" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-col>
                <el-col :span="4"><input type="file" ref="astronomerAddPictureRef" @change="astronomerAddPictureChange" /></el-col>
                <el-col :span="2"><el-button type="primary" native-type="submit">Добавить</el-button></el-col>
              </el-row>
              <div v-if="astronomerAddImageUrl" class="mt-2">
                <img :src="astronomerAddImageUrl" style="max-height:60px; cursor:pointer;" @click="openImagePreviewModal(astronomerAddImageUrl)" />
              </div>
            </el-form>
          </el-card>
        </div>

        <div v-if="astronomerToEdit" class="mb-3">
          <el-card>
            <template #header>
              <h5>Редактировать астронома</h5>
            </template>
            <el-row :gutter="12" align="middle">
              <el-col :span="6"><el-input v-model="astronomerToEdit.name" placeholder="ФИО астронома" /></el-col>
              <el-col :span="6"><el-input v-model="astronomerToEdit.specialization" placeholder="Специализация" /></el-col>
              <el-col :span="6">
                <el-select v-model="astronomerToEdit.observatory" placeholder="Выберите обсерваторию">
                  <el-option v-for="p in observatories" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <input type="file" ref="astronomerEditPictureRef" @change="astronomerEditPictureChange" accept="image/*" />
                <div v-if="getImageUrl(astronomerToEdit)" class="mt-2">
                  <img :src="getImageUrl(astronomerToEdit)" style="max-height:80px" />
                </div>
                <div v-if="astronomerEditImageUrl" class="mt-2">
                  <img :src="astronomerEditImageUrl" style="max-height:80px" />
                </div>
              </el-col>
              <el-col :span="24" class="mt-2">
                <el-button type="primary" @click="onAstronomerUpdate">Сохранить</el-button>
                <el-button @click="astronomerToEdit = null">Отмена</el-button>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div v-if="loading">Загрузка данных...</div>

        <div class="mb-3">
          <el-button @click="exportToExcel" type="success" :disabled="loadingExport">{{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}</el-button>
        </div>

        <el-row :gutter="16">
          <el-col :span="8" v-for="item in filteredAstronomers" :key="item.id">
            <el-card class="astronomer-card">
              <div><strong>{{ item.name }}</strong></div>
              <div class="text-muted">{{ item.specialization }}</div>
              <div>{{ observatoriesById[item.observatory] }}</div>
                <div v-if="item.picture" class="mt-2">
                <img :src="getImageUrl(item)" style="max-height:60px; cursor:pointer;" @click="openImagePreviewModal(getImageUrl(item))" />
              </div>
              <div class="mt-2">
                <el-button v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')" size="mini" @click="OnAstronomerEdit(item)">Редактировать</el-button>
                <el-button v-if="is_superuser || user_type === 'admin' || userInfoStore.hasPermission('can_manage_astronomers') || userInfoStore.hasPermission('can_manage_doctors')" size="mini" type="danger" @click="OnAstronomerRemove(item)">Удалить</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-dialog v-model="imageDialogVisible" width="60%">
          <template #title>Просмотр изображения</template>
          <div class="text-center"><img v-if="currentImageUrl" :src="currentImageUrl" style="max-height:80vh; width:100%" /></div>
          <template #footer>
            <el-button @click="imageDialogVisible = false">Закрыть</el-button>
          </template>
        </el-dialog>
      </div>
      <div v-else>Вы не авторизованы</div>
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