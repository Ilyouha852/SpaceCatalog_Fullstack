<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import {computed, onBeforeMount, ref} from 'vue';
import {useUserStore} from '@/stores/user_store';
import {useDataStore} from '@/stores/data_store';
import {storeToRefs} from "pinia";
const userStore = useUserStore()
const dataStore = useDataStore()

const {
    userInfo,
} = storeToRefs(userStore)

const {
    researchers,
    spaceObjects,
    objectTypes,
    astronomers,
    observations
} = storeToRefs(dataStore)

onBeforeMount(async () => {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
    await dataStore.fetchAllData()
})

const researcherToAdd = ref({});


const researcherPictureRef = ref();
const researcherImageUrl = ref();
async function researcherAddPictureChange() {
  researcherImageUrl.value = URL.createObjectURL(researcherPictureRef.value.files[0])
}
async function onResearcherAdd() {
  const formData = new FormData();
  
  formData.set('first_name', researcherToAdd.value.first_name);
  formData.set('last_name', researcherToAdd.value.last_name);
  formData.set('email', researcherToAdd.value.email);
  formData.set('card_number', researcherToAdd.value.card_number);
 
  if (researcherPictureRef.value.files[0]) {
     formData.append('picture', researcherPictureRef.value.files[0]);
  }
  await axios.post("/api/researchers/",formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await dataStore.fetchResearchers();
}
async function onRemoveClick(researcher) {
  await axios.delete(`/api/researchers/${researcher.id}/`);
  await dataStore.fetchResearchers();
}
const researcherToEdit = ref({});


const researcherEditPictureRef = ref();
const researcherEditImageUrl = ref();
async function researcherEditPictureChange() {
  if (researcherEditPictureRef.value.files[0]) {
    researcherEditImageUrl.value = URL.createObjectURL(researcherEditPictureRef.value.files[0])
  }
}
async function onResearcherEditClick(researcher) {
  researcherToEdit.value = { ...researcher };
  researcherEditImageUrl.value = null; 
 
}
async function onUpdateResearcher() {
  const formData = new FormData();
  
  
  if (researcherEditPictureRef.value.files[0]) {
    formData.append('picture', researcherEditPictureRef.value.files[0]);
  }
  formData.set('first_name', researcherToEdit.value.first_name);
  formData.set('last_name', researcherToEdit.value.last_name);
  formData.set('email', researcherToEdit.value.email);
  formData.set('card_number', researcherToEdit.value.card_number);

  
  await axios.put(`/api/researchers/${researcherToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  
  await dataStore.fetchResearchers();

}


</script>
<template>
  <div class="border p-5" v-if="userInfo && userInfo.is_authenticated">
        <div class="mb-5" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
          <h3>Добавить исследователя</h3>
        <form @submit.prevent.stop="onResearcherAdd">
            
            <div class="row">
                <div class="col">
                <div class="form-floating">
                    <!-- ТУТ ПОДКЛЮЧИЛ studentToAdd.name -->
                    <input
                    type="text"
                    class="form-control"
                      v-model="researcherToAdd.first_name"
                    required
                    />
                    <label for="floatingInput">Имя</label>
                </div>
                </div>
                <div class="col">
                <div class="form-floating">
                    <!-- ТУТ ПОДКЛЮЧИЛ studentToAdd.name -->
                    <input
                    type="text"
                    class="form-control"
                      v-model="researcherToAdd.last_name"
                    required
                    />
                    <label for="floatingInput">Фамилия</label>
                </div>
                </div>
                <div class="col">
                <div class="form-floating">
                    <!-- ТУТ ПОДКЛЮЧИЛ studentToAdd.name -->
                    <input
                    type="email"
                    class="form-control"
                      v-model="researcherToAdd.email"
                    required
                    />
                    <label for="floatingInput">Почта</label>
                </div>
                </div>
                <div class="col">
                <div class="form-floating">
                    <!-- ТУТ ПОДКЛЮЧИЛ studentToAdd.name -->
                    <input
                    type="number"
                    class="form-control"
                      v-model="researcherToAdd.card_number"
                    required
                    />
                      <label for="floatingInput">Номер исследователя</label>
                </div>
                </div>
                <div class="col">
                  <div class="form-floating">
                      <input
                      type="file"
                      class="form-control"
                      ref="researcherPictureRef"
                      @change="researcherAddPictureChange"
                      
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
            <img :src="researcherImageUrl" style="max-width: 300px; margin-top:20px;border-radius:20px;"/>
        </form>
        </div>
        <h4 v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff" >Список исследователей</h4>
        <h4 v-else-if="userInfo && userInfo.is_authenticated">Моя информация</h4>
        <div class="row">
            <template v-for="item in researchers">
            <div class="col-3 p-3 border d-flex justify-content-between align-items-center flex-wrap">
                    <div v-show="item.picture"><img :src="item.picture" style="max-width: 100%; border-radius: 20px; height: 300px; object-fit: cover; width:300px; margin-bottom:20px"></div>  {{ item.first_name }} 
                
                 <button class="btn btn-danger" @click="onRemoveClick(item)" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
                    <i class="bi bi-x">x</i>
                </button>
                
                <button style="flex:0 0 100%;"
                    class="btn btn-success mt-2"
                    @click="onResearcherEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editReaderModal">
                    <span>Редактировать</span>
                </button>
            </div>
            </template>
        </div>
        </div>
        <div v-else>
      <h2 class="mt-2">Пожалуйста, <a href="/">авторизуйтесь</a></h2>
    </div>
        <div class="modal fade" id="editReaderModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
           Редактировать
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
            <div class="col">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="researcherToEdit.first_name"
                />
                <label for="floatingInput">Имя</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="researcherToEdit.last_name"
                />
                <label for="floatingInput">Фамилия</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  type="email"
                  class="form-control"
                  v-model="researcherToEdit.email"
                />
                <label for="floatingInput">Почта</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  type="number"
                  class="form-control"
                  v-model="researcherToEdit.card_number"
                />
                      <label for="floatingInput">Номер исследователя</label>
              </div>
            </div>
            <div class="col-12 mt-3" v-if="researcherToEdit.picture">
                <p>Текущее фото:</p>
                <img :src="researcherToEdit.picture" style="max-width: 300px; border-radius: 10px; height: 200px; object-fit: cover; margin-bottom: 10px">
            </div>
            <div class="col-12 mt-3">
              <div class="form-floating">
                <input
                  type="file"
                  class="form-control"
                  ref="researcherEditPictureRef"
                  @change="researcherEditPictureChange"
                />
                <label for="floatingInput">Новое фото (оставьте пустым, чтобы не менять)</label>
              </div>
            </div>
          </div>
          <img v-if="researcherEditImageUrl" :src="researcherEditImageUrl" style="max-width: 200px; border-radius: 10px; height: 200px; object-fit: cover; margin-top: 10px">
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
            @click="onUpdateResearcher"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
</div>
</template>
<style scoped>
</style>