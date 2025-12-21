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
const astronomerToAdd = ref({});
const spaceObjectsToAdd = ref({});
const observationsToAdd = ref({});

async function onSpaceObjectAdd() {
  await axios.post("/api/spaceobjects/", {
    ...spaceObjectsToAdd.value,
  });
  await dataStore.fetchSpaceObjects();
}

async function onRemoveClickSpaceObject(spaceObject) {
  await axios.delete(`/api/spaceobjects/${spaceObject.id}/`);
  await dataStore.fetchSpaceObjects();
}


const spaceObjectToEdit = ref({});
async function onSpaceObjectEditClick(spaceObject) {
  spaceObjectToEdit.value = { ...spaceObject };
}
async function onUpdateSpaceObject() {
  await axios.put(`/api/spaceobjects/${spaceObjectToEdit.value.id}/`, {
    ...spaceObjectToEdit.value,
  });
  await dataStore.fetchSpaceObjects();
}

const uniqueObjectTypes = computed(() => {
  const seen = new Set();
  return objectTypes.value.filter(item => {
    if (seen.has(item.name)) {
      return false;
    }
    seen.add(item.name);
    return true;
  });
});
</script>
<template>
    <div class="border p-5" v-if="userInfo && userInfo.is_authenticated">
          <div class="mb-5" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
            <h3>Добавить космический объект</h3>
          <form @submit.prevent.stop="onSpaceObjectAdd">
              
              <div class="row" style="row-gap: 20px;">
                  <div class="col-4">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="spaceObjectsToAdd.name"
                      required
                      />
                      <label for="floatingInput">Название объекта</label>
                  </div>
                  </div>
                  <div class="col-4">
                      <div class="form-floating">
                        <select class="form-select" v-model="spaceObjectsToAdd.astronomer">
                          <option :value="a.id" v-for="a in astronomers">
                            {{ a.name }}
                          </option>
                        </select>
                        <label for="floatingInput">Открыватель</label>
                      </div>
                  </div>
                 <div class="col-4">
                    <div class="form-floating">
                      <select class="form-select" v-model="spaceObjectsToAdd.object_type"> 
                        <option :value="g.id" v-for="g in uniqueObjectTypes" :key="g.id">
                          {{ g.name }}
                        </option>
                      </select>
                      <label for="floatingInput">Тип объекта</label>
                    </div>
                  </div>
                  <div class="col-4">
                  <div class="form-floating">
                      <input
                      type="number"
                      class="form-control"
                      v-model="spaceObjectsToAdd.discovery_year"
                      required
                      />
                      <label for="floatingInput">Год открытия</label>
                  </div>
                  </div>
                  <div class="col-4">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="spaceObjectsToAdd.description"
                      required
                      />
                      <label for="floatingInput">Описание</label>
                  </div>
                  </div>
                  <div class="col-4">
                  <div class="form-floating">
                      <input
                      type="number"
                      step="0.01"
                      class="form-control"
                      v-model="spaceObjectsToAdd.distance"
                      />
                      <label for="floatingInput">Расстояние (св. годы)</label>
                  </div>
                  </div>
                  <div class="col-4">
                  <div class="form-floating">
                      <input
                      type="number"
                      step="0.01"
                      class="form-control"
                      v-model="spaceObjectsToAdd.mass"
                      />
                      <label for="floatingInput">Масса (солн. массы)</label>
                  </div>
                  </div>
                  <div class="col-4">
                  <button class="btn btn-primary" style="width: 100%;height: 100%;">
                      Добавить 
                  </button>
                  </div>
              </div>
          </form>
          </div>
          <div>
            <h4>Список космических объектов</h4>
            <div class="row">
            <template v-for="item in spaceObjects">
            <div class="col-3 p-3 border d-flex justify-content-between align-items-center flex-wrap"><div>
              <h5>Название: </h5>{{ item.name }}
            </div> 
             
                 <button v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff" class="btn btn-danger" @click="onRemoveClickSpaceObject(item)">
                    <i class="bi bi-x">x</i>
                </button>
                <div>
               <h5>Описание: </h5>
              <ul>
                <li>{{ item.description }} </li>
              </ul>
             </div>
                
                <button style="flex:0 0 100%;"v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff"
                    class="btn btn-success mt-2"
                    @click="onSpaceObjectEditClick(item)"
                    data-bs-toggle="modal"
                    data-bs-target="#editSpaceObjectModal">
                    <span>Редактировать</span>
                </button>
            </div>
            </template>
        </div>
          </div>
         </div>
         <div v-else>
      <h2 class="mt-2">Пожалуйста, <a href="/">авторизуйтесь</a></h2>
    </div>
         <div class="modal fade" id="editSpaceObjectModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
           Редактировать космический объект
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
            <div class="col-6 mb-2">
                    <div class="form-floating">
                      <input
                        type="text"
                        class="form-control"
                        v-model="spaceObjectToEdit.name"
                      />
                      <label for="floatingInput">Название</label>
                    </div>
            </div>
            <div class="col-6 mb-2">
                      <div class="form-floating">
                        <select class="form-select" v-model="spaceObjectToEdit.astronomer">
                          <option :value="a.id" v-for="a in astronomers">
                            {{ a.name }}
                          </option>
                        </select>
                        <label for="floatingInput">Открыватель</label>
                      </div>
            </div>
            <div class="col-6 mb-2">
                      <div class="form-floating">
                        <select class="form-select" v-model="spaceObjectToEdit.object_type"> 
                        <option :value="g.id" v-for="g in uniqueObjectTypes" :key="g.id">
                          {{ g.name }}
                        </option>
                      </select>
                        <label for="floatingInput">Тип объекта</label>
                      </div>
            </div>
            <div class="col-6 mb-2">
                  <div class="form-floating">
                      <input
                      type="number"
                      class="form-control"
                      v-model="spaceObjectToEdit.discovery_year"
                      required
                      />
                      <label for="floatingInput">Год открытия</label>
                  </div>
            </div>
            <div class="col-6 mb-2">
                  <div class="form-floating">
                      <input
                      type="text"
                      class="form-control"
                      v-model="spaceObjectToEdit.description"
                      required
                      />
                      <label for="floatingInput">Описание</label>
                  </div>
            </div>
            <div class="col-6 mb-2">
                  <div class="form-floating">
                      <input
                      type="number"
                      step="0.01"
                      class="form-control"
                      v-model="spaceObjectToEdit.distance"
                      />
                      <label for="floatingInput">Расстояние (св. годы)</label>
                  </div>
            </div>
            <div class="col-6 mb-2">
                  <div class="form-floating">
                      <input
                      type="number"
                      step="0.01"
                      class="form-control"
                      v-model="spaceObjectToEdit.mass"
                      />
                      <label for="floatingInput">Масса (солн. массы)</label>
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
            @click="onUpdateSpaceObject"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
</div>   
</template>