<script setup>
import { computed, onBeforeMount, ref } from "vue";
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
const observatories = ref([]);
const observatoryToAdd = ref({});
const observatoryToEdit = ref(null);

const observatoryAddPictureRef = ref();
const observatoryEditPictureRef = ref();
const observatoryAddImageUrl = ref();
const observatoryEditImageUrl = ref();
const hasObservatoryEditPicture = ref(false);

const searchQuery = ref("");
const searchAddress = ref("");
const searchPhone = ref("");
const currentImageUrl = ref('');
const imageDialogVisible = ref(false);

const filteredObservatories = computed(() => {
  if (!observatories.value.length) return [];

  return observatories.value.filter(observatory => {
    if (searchQuery.value) {
      const name = observatory.name?.toLowerCase() || '';
      const query = searchQuery.value.toLowerCase();
      
      if (!name.includes(query)) {
        return false;
      }
    }

    if (searchAddress.value) {
      const address = observatory.address?.toLowerCase() || '';
      const query = searchAddress.value.toLowerCase();
      
      if (!address.includes(query)) {
        return false;
      }
    }

    if (searchPhone.value) {
      const phone = observatory.phone?.toLowerCase() || '';
      const query = searchPhone.value.toLowerCase();
      
      if (!phone.includes(query)) {
        return false;
      }
    }

    return true;
  });
});

const resetFilters = () => {
  searchQuery.value = "";
  searchAddress.value = "";
  searchPhone.value = "";
};

async function fetchObservatories() {
  loading.value = true;
  const r = await axios.get("/api/observatories/");
  observatories.value = r.data;
  loading.value = false;
}

async function onObservatoryAdd() {
  const formData = new FormData();

  if (observatoryAddPictureRef.value && observatoryAddPictureRef.value.files[0]) {
    formData.set("picture", observatoryAddPictureRef.value.files[0]);
  }

  formData.set("name", observatoryToAdd.value.name);
  formData.set("address", observatoryToAdd.value.address);
  formData.set("phone", observatoryToAdd.value.phone);

  try {
    await axios.post("/api/observatories/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    await fetchObservatories();
  } catch (error) {
    console.error("Ошибка при создании обсерватории:", error);
  }
}

async function observatoryAddPictureChange() {
  observatoryAddImageUrl.value = URL.createObjectURL(
    observatoryAddPictureRef.value.files[0]
  );
}

async function exportToExcel() {
  loadingExport.value = true;
  try {
    const response = await axios.get("/api/observatories/export-excel/", {
      responseType: 'blob'
    });
 
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'observatories.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
  } catch (error) {
    console.error("Ошибка при экспорте:", error);
    alert("Ошибка при экспорте данных");
  } finally {
    loadingExport.value = false;
  }
}

async function OnObservatoryEdit(observatory) {
  observatoryToEdit.value = { ...observatory };
  observatoryEditImageUrl.value = '';
  if (observatoryEditPictureRef.value) {
    observatoryEditPictureRef.value.value = '';
  }
}

async function onObservatoryUpdate() {
  try {
    const formData = new FormData();

    formData.set('name', observatoryToEdit.value.name);
    formData.set('address', observatoryToEdit.value.address);
    formData.set('phone', observatoryToEdit.value.phone);

    if (observatoryEditPictureRef.value && observatoryEditPictureRef.value.files[0]) {
      formData.append('picture', observatoryEditPictureRef.value.files[0]);
    }

    await axios.put(`/api/observatories/${observatoryToEdit.value.id}/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    await fetchObservatories();
    observatoryToEdit.value = null;
  } catch (error) {
    console.error("Ошибка при обновлении обсерватории:", error);
    alert("Ошибка при обновлении обсерватории");
  }
}

async function observatoryEditPictureChange() {
  observatoryEditImageUrl.value = URL.createObjectURL(
    observatoryEditPictureRef.value.files[0]
  );
}

async function OnObservatoryRemove(observatory) {
  await axios.delete(`/api/observatories/${observatory.id}/`);
  await fetchObservatories();
}

onBeforeMount(async () => {
  await fetchObservatories();
});

const showZoomImageContainer = ref(false);
const zoomImageUrl = ref("");

function showZoomImage(imageUrl) {
  zoomImageUrl.value = imageUrl;
  showZoomImageContainer.value = true;
}

function hideZoomImage() {
  showZoomImageContainer.value = false;
}

function getImageUrl(observatory) {
  if (!observatory.picture) return null;
  
  if (observatory.picture.startsWith('http')) {
    return observatory.picture;
  }
  
  return `http://localhost:8000${observatory.picture}`;
}

function openImagePreviewModal(url) {
  currentImageUrl.value = url;
  imageDialogVisible.value = true;
}
</script>
<template>
  <div>
    <div class="p-2">
      <div v-if="is_authenticated">
        <el-card class="mb-4">
          <template #header>
            <span>Фильтры обсерваторий</span>
          </template>

          <el-row :gutter="16" class="filters-row">
            <el-col :span="6">
              <el-input v-model="searchQuery" placeholder="Поиск по названию...">
                <template #prefix><i class="bi bi-search"></i></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-input v-model="searchAddress" placeholder="Поиск по адресу...">
                <template #prefix><i class="bi bi-geo-alt"></i></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-input v-model="searchPhone" placeholder="Поиск по телефону...">
                <template #prefix><i class="bi bi-telephone"></i></template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-button @click="resetFilters" type="info" plain>Сбросить</el-button>
            </el-col>
          </el-row>

          <div class="mt-2 text-muted">Найдено обсерваторий: {{ filteredObservatories.length }}</div>
        </el-card>

        <div v-if="is_superuser || userInfoStore.isAdmin()">
          <el-card class="mb-4">
            <template #header><h5>Добавить обсерваторию</h5></template>
            <el-form @submit.prevent.stop="onObservatoryAdd" label-position="top">
              <el-row :gutter="12" align="middle">
                <el-col :span="6"><el-input v-model="observatoryToAdd.name" placeholder="Название" /></el-col>
                <el-col :span="6"><el-input v-model="observatoryToAdd.address" placeholder="Адрес" /></el-col>
                <el-col :span="4"><el-input v-model="observatoryToAdd.phone" placeholder="Телефон" /></el-col>
                <el-col :span="4">
                  <input type="file" ref="observatoryAddPictureRef" @change="observatoryAddPictureChange" />
                </el-col>
                <el-col :span="2">
                  <el-button type="primary" native-type="submit">Добавить</el-button>
                </el-col>
              </el-row>
              <div v-if="observatoryAddImageUrl" class="mt-2">
                <img :src="observatoryAddImageUrl" style="max-height:60px; cursor:pointer;" @click="showZoomImage(observatoryAddImageUrl)" />
              </div>
            </el-form>
          </el-card>
        </div>

        <div v-if="observatoryToEdit" class="mb-3">
          <el-card>
            <template #header>
              <h5>Редактировать обсерваторию</h5>
            </template>
            <el-row :gutter="12" align="middle">
              <el-col :span="6"><el-input v-model="observatoryToEdit.name" placeholder="Название обсерватории" /></el-col>
              <el-col :span="6"><el-input v-model="observatoryToEdit.address" placeholder="Адрес" /></el-col>
              <el-col :span="6"><el-input v-model="observatoryToEdit.phone" placeholder="Телефон" /></el-col>
              <el-col :span="6">
                <input type="file" ref="observatoryEditPictureRef" @change="observatoryEditPictureChange" accept="image/*" />
                <div v-if="getImageUrl(observatoryToEdit)" class="mt-2">
                  <img :src="getImageUrl(observatoryToEdit)" style="max-height:80px" />
                </div>
                <div v-if="observatoryEditImageUrl" class="mt-2">
                  <img :src="observatoryEditImageUrl" style="max-height:80px" />
                </div>
              </el-col>
              <el-col :span="24" class="mt-2">
                <el-button type="primary" @click="onObservatoryUpdate">Сохранить</el-button>
                <el-button @click="observatoryToEdit = null">Отмена</el-button>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div v-if="loading">Загрузка данных...</div>

        <div class="mb-3">
          <el-button @click="exportToExcel" type="success" :disabled="loadingExport">{{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}</el-button>
        </div>

        <el-row :gutter="16">
          <el-col :span="8" v-for="item in filteredObservatories" :key="item.id">
            <el-card class="observatory-item-card">
              <div class="observatory-card-content">
                <div><strong>{{ item.name }}</strong></div>
                <div class="text-muted">{{ item.address }}</div>
                <div>{{ item.phone }}</div>
                <div v-if="item.picture" class="mt-2">
                  <img :src="getImageUrl(item)" style="max-height:60px; cursor:pointer;" @click="openImagePreviewModal(getImageUrl(item))" />
                </div>
                <div class="actions mt-2">
                  <el-button v-if="is_superuser || userInfoStore.isAdmin()" size="mini" @click="OnObservatoryEdit(item)">Редактировать</el-button>
                  <el-button v-if="is_superuser || userInfoStore.isAdmin()" size="mini" type="danger" @click="OnObservatoryRemove(item)">Удалить</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <el-dialog v-model="imageDialogVisible" width="60%" :show-close="true">
          <template #title>Просмотр изображения</template>
          <div class="text-center">
            <img v-if="currentImageUrl" :src="currentImageUrl" style="max-height:80vh; width:100%" />
          </div>
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
.observatory-item {
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid silver;
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr auto auto auto auto auto auto;
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