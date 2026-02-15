<script setup>
import { computed, onBeforeMount, ref } from "vue";
import axios from "axios";
import Cookies from "js-cookie";
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";  
import { Modal } from 'bootstrap';

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
  
  const modalElement = document.getElementById('imagePreviewModal');
  
  if (modalElement) {
    const modal = Modal.getOrCreateInstance(modalElement); 
    modal.show();
  } else {
    console.error("Ошибка: Модальное окно с ID 'imagePreviewModal' не найдено в DOM.");
  }
}
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <div v-if="is_authenticated">
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="card-title mb-0">Фильтры обсерваторий</h6>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3">
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    v-model="searchQuery"
                    placeholder="Поиск по названию..."
                  />
                </div>
              </div>
              <div class="col-md-3">
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-geo-alt"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    v-model="searchAddress"
                    placeholder="Поиск по адресу..."
                  />
                </div>
              </div>
              <div class="col-md-3">
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
              <div class="col-md-3">
                <button @click="resetFilters" class="btn btn-outline-secondary w-100">
                  Сбросить
                </button>
              </div>
            </div>
            <div class="mt-2 text-muted">
              Найдено обсерваторий: {{ filteredObservatories.length }}
            </div>
          </div>
        </div>

          <div v-if="is_superuser || userInfoStore.isAdmin()">
          <form @submit.prevent.stop="onObservatoryAdd">
            <div class="row">
              <div class="col">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="observatoryToAdd.name"
                    required
                  />
                  <label for="floatingInput">Название</label>
                </div>
              </div>
              <div class="col">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="observatoryToAdd.address"
                    required
                  />
                  <label for="floatingInput">Адрес</label>
                </div>
              </div>
              <div class="col">
                <div class="form-floating mb-3">
                  <input
                    type="text"
                    class="form-control"
                    v-model="observatoryToAdd.phone"
                    required
                  />
                  <label for="floatingInput">Телефон</label>
                </div>
              </div>
              <div class="col-auto">
                <input
                  class="form-control"
                  type="file"
                  ref="observatoryAddPictureRef"
                  @change="observatoryAddPictureChange"
                />
              </div>
              <div class="col-auto">
                <img
                  :src="observatoryAddImageUrl"
                  style="max-height: 60px"
                  alt="Изображение"
                  v-if="observatoryAddImageUrl"
                  @click="showZoomImage(observatoryAddImageUrl)"
                />
              </div>
              <div class="col-auto">
                <button class="btn btn-primary">Добавить</button>
              </div>
            </div>
          </form>
        </div>

        <div v-if="observatoryToEdit" class="card mb-3 p-3">
          <h5>Редактировать обсерваторию</h5>
          <div class="row g-2 align-items-start">
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.name" placeholder="Название обсерватории" />
            </div>
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.address" placeholder="Адрес" />
            </div>
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.phone" placeholder="Телефон" />
            </div>
            <div class="col-md-3">
              <input class="form-control" type="file" ref="observatoryEditPictureRef" @change="observatoryEditPictureChange" accept="image/*" />
              <div v-if="getImageUrl(observatoryToEdit)" class="mt-2">
                <img :src="getImageUrl(observatoryToEdit)" style="max-height:80px" class="img-thumbnail" />
              </div>
              <div v-if="observatoryEditImageUrl" class="mt-2">
                <img :src="observatoryEditImageUrl" style="max-height:80px" class="img-thumbnail" />
              </div>
            </div>
            <div class="col-12 mt-2 d-flex gap-2">
              <button class="btn btn-primary" @click="onObservatoryUpdate">Сохранить</button>
              <button class="btn btn-secondary" @click="observatoryToEdit = null">Отмена</button>
            </div>
          </div>
        </div>

        <div v-if="loading">Загрузка данных...</div>

        <div class="mb-3">
          <button 
            @click="exportToExcel" 
            class="btn btn-success"
            :disabled="loadingExport"
          >
            <i class="bi bi-file-earmark-excel"></i> 
            {{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}
          </button>
        </div>

        <div>
          <div v-for="item in filteredObservatories" :key="item.id" class="observatory-item">
            <div>{{ item.name }}</div>
            <div>{{ item.address }}</div>
            <div>{{ item.phone }}</div>
            <div v-show="item.picture">
              <img
                :src="getImageUrl(item)"
                style="max-height: 60px"
                @click="openImagePreviewModal(getImageUrl(item))"
              />
            </div>
            <button
              v-if="is_superuser || userInfoStore.isAdmin()"
              class="btn btn-sm btn-outline-secondary me-2"
              @click="OnObservatoryEdit(item)"
            >
              Редактировать
            </button>
            <button 
              v-if="is_superuser || userInfoStore.isAdmin()"
              class="btn btn-sm btn-danger" 
              @click="OnObservatoryRemove(item)"
            >
              Удалить
            </button>
          </div>
        </div>

        <div v-if="observatoryToEdit" class="card mb-3 p-3">
          <h5>Редактировать обсерваторию</h5>
          <div class="row g-2 align-items-start">
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.name" placeholder="Название обсерватории" />
            </div>
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.address" placeholder="Адрес" />
            </div>
            <div class="col-md-3">
              <input type="text" class="form-control" v-model="observatoryToEdit.phone" placeholder="Телефон" />
            </div>
            <div class="col-md-3">
              <input class="form-control" type="file" ref="observatoryEditPictureRef" @change="observatoryEditPictureChange" accept="image/*" />
              <div v-if="getImageUrl(observatoryToEdit)" class="mt-2">
                <img :src="getImageUrl(observatoryToEdit)" style="max-height:80px" class="img-thumbnail" />
              </div>
              <div v-if="observatoryEditImageUrl" class="mt-2">
                <img :src="observatoryEditImageUrl" style="max-height:80px" class="img-thumbnail" />
              </div>
            </div>
            <div class="col-12 mt-2 d-flex gap-2">
              <button class="btn btn-primary" @click="onObservatoryUpdate">Сохранить</button>
              <button class="btn btn-secondary" @click="observatoryToEdit = null">Отмена</button>
            </div>
          </div>
        </div>
        
        <div class="zoom-image-container" :class="{ active: showZoomImageContainer }" @click="hideZoomImage">
          <img :src="zoomImageUrl" alt="Увеличенное изображение" />
        </div>
      </div>
      <div v-else>Вы не авторизованы</div>
    </div>
    
    <div class="modal fade" id="imagePreviewModal" tabindex="-1" aria-labelledby="imagePreviewModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="imagePreviewModalLabel">Просмотр изображения</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
          </div>
          <div class="modal-body text-center">
            <img v-if="currentImageUrl" :src="currentImageUrl" :alt="''" class="img-fluid rounded" style="max-height: 80vh; object-fit: contain;">
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
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