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
const objectTypeToAdd = ref({});


async function onObjectTypeAdd() {
  await axios.post("/api/objecttypes/", {
    ...objectTypeToAdd.value,
  });
  await dataStore.fetchObjectTypes();
}


async function onRemoveClickObjectType(objectType) {
  await axios.delete(`/api/objecttypes/${objectType.id}/`);
  await dataStore.fetchObjectTypes();
}


const objectTypeToEdit = ref({});
async function onObjectTypeEditClick(objectType) {
  objectTypeToEdit.value = { ...objectType };
}
async function onUpdateObjectType() {
  await axios.put(`/api/objecttypes/${objectTypeToEdit.value.id}/`, {
    ...objectTypeToEdit.value,
  });
  await dataStore.fetchObjectTypes();
}

</script>
<template>
  <div class="border p-5" v-if="userInfo && userInfo.is_authenticated">
         <div class="mb-5" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
           <h3>Добавить тип объекта</h3>
          <form @submit.prevent.stop="onObjectTypeAdd">
              
              <div class="row">
                  <div class="col-5">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="objectTypeToAdd.name"
                      required
                      />
                      <label for="floatingInput">Название типа</label>
                  </div>
                  </div>
                  <div class="col-5">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="objectTypeToAdd.description"
                      required
                      />
                      <label for="floatingInput">Описание</label>
                  </div>
                  </div>
                
                  <div class="col-2">
                  <button class="btn btn-primary" style="width: 100%;height: 100%;">
                      Добавить 
                  </button>
                  </div>
              </div>
          </form>
         </div>
          <h4>Список типов объектов</h4>
        <div class="row">
            <template v-for="item in objectTypes">
            <div class="col-3 p-3 border d-flex justify-content-between align-items-center flex-wrap">{{ item.name }} 
                
                 <button v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff" class="btn btn-danger" @click="onRemoveClickObjectType(item)">
                    <i class="bi bi-x">x</i>
                </button>
                <div style="width: 100%;">
                  Описание:
                  {{ item.description }}
                </div>
                <button style="flex:0 0 100%;"v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff"
                    class="btn btn-success mt-2"
                    @click="onObjectTypeEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editObjectTypeModal">
                    <span>Редактировать</span>
                </button>
            </div>
            </template>
        </div>
         </div>
         <div v-else>
      <h2 class="mt-2">Пожалуйста, <a href="/">авторизуйтесь</a></h2>
    </div>
         <div class="modal fade" id="editObjectTypeModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
           Редактировать тип объекта
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
                  v-model="objectTypeToEdit.name"
                />
                <label for="floatingInput">Название типа</label>
              </div>
            </div>
            <div class="col">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="objectTypeToEdit.description"
                />
                <label for="floatingInput">Описание типа</label>
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
            Close
          </button>
          <button
            data-bs-dismiss="modal"
            type="button"
            class="btn btn-primary"
            @click="onUpdateObjectType"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
</div>
</template>