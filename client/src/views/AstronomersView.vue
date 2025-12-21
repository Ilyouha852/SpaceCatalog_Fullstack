<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { useDataStore } from '@/stores/data_store';
import { storeToRefs } from 'pinia';

const userStore = useUserStore();
const dataStore = useDataStore();

const { userInfo } = storeToRefs(userStore);
const { astronomers } = storeToRefs(dataStore);

onBeforeMount(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');
  await dataStore.fetchAllData();
});

const astronomerToAdd = ref({});
const astronomerPictureRef = ref();
const astronomerImageUrl = ref();

const astronomerToEdit = ref({});
const astronomerEditPictureRef = ref();
const astronomerEditImageUrl = ref();

async function astronomerAddPictureChange() {
  astronomerImageUrl.value = URL.createObjectURL(astronomerPictureRef.value.files[0]);
}

async function onAstronomerAdd() {
  const formData = new FormData();
  formData.append('picture', astronomerPictureRef.value.files[0]);
  formData.set('name', astronomerToAdd.value.name);
  formData.set('bio', astronomerToAdd.value.bio);

  await axios.post('/api/astronomers/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  await dataStore.fetchAstronomers();
}

async function onAstronomerEditClick(astronomer) {
  astronomerToEdit.value = { ...astronomer };
  astronomerEditImageUrl.value = null;
}

async function astronomerEditPictureChange() {
  if (astronomerEditPictureRef.value.files[0]) {
    astronomerEditImageUrl.value = URL.createObjectURL(astronomerEditPictureRef.value.files[0]);
  }
}

async function onUpdateAstronomer() {
  const formData = new FormData();

  if (astronomerEditPictureRef.value.files[0]) {
    formData.append('picture', astronomerEditPictureRef.value.files[0]);
  }

  formData.set('name', astronomerToEdit.value.name);
  formData.set('bio', astronomerToEdit.value.bio);

  await axios.put(`/api/astronomers/${astronomerToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });

  await dataStore.fetchAstronomers();
}

async function onRemoveClickAstronomer(astronomer) {
  await axios.delete(`/api/astronomers/${astronomer.id}/`);
  await dataStore.fetchAstronomers();
}
</script>

<template>
  
    <div v-if="userInfo && userInfo.is_authenticated">
        <div class="border p-5">
          <div class="mb-5" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
            <h3>Добавить астронома</h3>
          <form @submit="onAstronomerAdd">
              
              <div class="row">
                  <div class="col">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="astronomerToAdd.name"
                      required
                      />
                      <label for="floatingInput">Имя астронома</label>
                  </div>
                  </div>
                  <div class="col">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="astronomerToAdd.bio"
                      required
                      />
                      <label for="floatingInput">Биография</label>
                  </div>
                  </div>
                  <div class="col">
                  <div class="form-floating">
                      <input
                      type="file"
                      class="form-control"
                      ref="astronomerPictureRef"
                      @change="astronomerAddPictureChange"
                      required
                      />
                      <label for="floatingInput">Фотография</label>
                  </div>
                  </div>
                  
                  <div class="col-auto">
                  <button class="btn btn-primary" style="width: 100%;height: 100%;">
                      Добавить 
                  </button>
                  </div>
              </div>
              
              <img :src="astronomerImageUrl" style="max-width: 300px; margin-top:20px;border-radius:20px;"/>
          </form>
          </div>
          <div v-if="userInfo && userInfo.is_authenticated">
            <h4>Список астрономов</h4>
        <div class="row">
            <template v-for="item in astronomers">
            <div class="col-3 p-3 border d-flex justify-content-between align-items-center flex-wrap">
              <div v-show="item.picture"><img :src="item.picture" style="max-width: 100%; border-radius: 20px; height: 300px; object-fit: cover; width:300px; margin-bottom:20px"></div>
              {{ item.name }} 

                 <button v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff" class="btn btn-danger" @click="onRemoveClickAstronomer(item)">
                    <i class="bi bi-x">x</i>
                </button>
                
                <button style="flex:0 0 100%;" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff"
                    class="btn btn-success mt-2"
                    @click="onAstronomerEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editAstronomerModal">
                    <span>Редактировать</span>
                </button>
            </div>
            </template>
        </div>
          </div>
        </div>
    </div>
    <div v-else>
      <h2 class="mt-2">Пожалуйста, <a href="/">авторизуйтесь</a></h2>
    </div>
    <div class="modal fade" id="editAstronomerModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
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
          <div class="row">
            <div class="col-6">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="astronomerToEdit.name"
                />
                <label for="floatingInput">Имя</label>
              </div>
            </div>
            <div class="col-6">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="astronomerToEdit.bio"
                />
                <label for="floatingInput">Биография</label>
              </div>
            </div>
            <div class="col-6 mt-3" v-if="astronomerToEdit.picture">
                <p>Текущее изображение:</p>
                <img :src="astronomerToEdit.picture" style="max-width: 300px; border-radius: 10px; height: 200px; object-fit: cover; margin-bottom: 10px">
            </div>
            <div class="col-12 mt-3">
              <div class="form-floating">
                <input
                  type="file"
                  class="form-control"
                  ref="astronomerEditPictureRef"
                  @change="astronomerEditPictureChange"
                />
                <label for="floatingInput">Новое изображение (оставьте пустым, чтобы не менять)</label>
              </div>
            </div>
          </div>
         
        <img v-if="astronomerEditImageUrl" :src="astronomerEditImageUrl" style="max-width: 200px; border-radius: 10px; height: 200px; object-fit: cover; margin-top: 10px">
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
          >
            Close
          </button>
          <button
            data-bs-dismiss="modal"
            type="button"
            class="btn btn-primary"
            @click="onUpdateAstronomer"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
</div> 
</template>