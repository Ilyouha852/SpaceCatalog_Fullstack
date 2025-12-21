<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { computed, onBeforeMount, ref } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { useDataStore } from '@/stores/data_store';
import { storeToRefs } from 'pinia';

const userStore = useUserStore();
const dataStore = useDataStore();

const { userInfo } = storeToRefs(userStore);
const {
  researchers,
  spaceObjects,
  observations
} = storeToRefs(dataStore);

onBeforeMount(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');
  await dataStore.fetchAllData();
});

const selectedResearcher = ref(null);

const filteredObservations = computed(() => {
  if (!selectedResearcher.value) {
    return observations.value;
  }
  return observations.value.filter(item => item.researcher === parseInt(selectedResearcher.value));
});

const observationsToAdd = ref({});

const observationToEdit = ref({});

async function onObservationAdd() {
  await axios.post('/api/observations/', {
    ...observationsToAdd.value,
  });
  await dataStore.fetchObservations();
}

async function onObservationEditClick(observation) {
  observationToEdit.value = { ...observation };
}

async function onUpdateObservation() {
  await axios.put(`/api/observations/${observationToEdit.value.id}/`, {
    ...observationToEdit.value,
  });
  await dataStore.fetchObservations();
}

async function onRemoveClickObservation(observation) {
  await axios.delete(`/api/observations/${observation.id}/`);
  await dataStore.fetchObservations();
}
</script>

<template>
        <div class="border p-5" v-if="userInfo && userInfo.is_authenticated">
          <div>
            <h3 v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">Запланировать наблюдение</h3>
            <h3 v-else-if="userInfo && userInfo.is_authenticated">Запланировать наблюдение</h3>
            <form @submit.prevent.stop="onObservationAdd">
                <div class="row">
            <div class="col-3">
                <div class="form-floating">
                  <select class="form-select" v-model="observationsToAdd.space_object" required>
                    <option :value="b.id" v-for="b in spaceObjects" :key="b.id">
                      {{ b.name }}
                    </option>
                  </select>
                  <label for="floatingInput">Космический объект</label>
                </div>
            </div>
            <div class="col-2">
                      <div class="form-floating">
                        <select class="form-select" v-model="observationsToAdd.status"> 
                        
                          <option value="planned">Запланировано</option>
                          <option value="in_progress">В процессе</option>
                        </select>
                        <label for="floatingInput">Статус</label>
                      </div>
            </div>
            <div class="col-2">
                  <div class="form-floating">
                      <input
                      type="date"
                      class="form-control"
                      v-model="observationsToAdd.observation_date"
                      required
                      />
                      <label for="floatingInput">Дата наблюдения</label>
                  </div>
            </div>
            <div class="col-3">
                <div class="form-floating">
                  <select class="form-select" v-model="observationsToAdd.researcher" required>
                    <option :value="b.id" v-for="b in researchers">
                      {{ b.first_name }}  {{ b.last_name }}
                    </option>
                  </select>
                  <label for="floatingInput">Исследователь</label>
                </div>
            </div>
          
                 <div class="col-2" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
                  <button class="btn btn-primary"  style="width: 100%;height: 100%;">
                      Запланировать 
                  </button>
                  </div>
                     <div class="col-2" v-else-if="userInfo && userInfo.is_authenticated">
                  <button class="btn btn-primary"  style="width: 100%;height: 100%;">
                      Запланировать 
                  </button>
                  </div>
          </div>
           
          </form>
          </div>

         
          <div class="mt-4" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
            <h4>Фильтр по исследователю</h4>
            <div class="row">
              <div class="col-6">
                <div class="form-floating">
                  <select class="form-select" v-model="selectedResearcher">
                    <option value="">Все исследователи</option>
                    <option :value="researcher.id" v-for="researcher in researchers" :key="researcher.id">
                      {{ researcher.first_name }} {{ researcher.last_name }}
                    </option>
                  </select>
                  <label for="floatingInput">Выберите исследователя</label>
                </div>
              </div>
            
            </div>
          </div>

          <h4 class="mt-5" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">Наблюдения</h4>
          <h4 class="mt-5" v-else-if="userInfo && userInfo.is_authenticated">Мои наблюдения</h4>
          
          
          <div v-if="selectedResearcher && userInfo && userInfo.is_authenticated && userInfo.is_staff" class="alert alert-info">
            Показаны наблюдения исследователя: 
            <strong>
              {{ researchers.find(r => r.id === parseInt(selectedResearcher))?.first_name }} 
              {{ researchers.find(r => r.id === parseInt(selectedResearcher))?.last_name }}
            </strong>
          </div>

            <div class="row">
                <template v-for="item in filteredObservations">
                <div class="col-3 p-3 border d-flex justify-content-between align-items-center flex-wrap">{{ spaceObjects.find(b => b.id === item.space_object)?.name || 'Объект' }}  <br> <hr>
                
                    
                    <button v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff"class="btn btn-danger" @click="onRemoveClickObservation(item)">
                        <i class="bi bi-x">x</i>
                    </button>
                    <div style="width:100%;">
                          <span v-if="item.status === 'planned'">Запланировано</span>
                    <span v-else-if="item.status === 'in_progress'">В процессе</span>
                    <span v-else-if="item.status === 'completed'">Завершено</span>
                    <span v-else>{{ item.status }}</span>
                    </div>
                    <div class="mt-2 mb-2" style="width:100%;">
                      Исследователь - {{ researchers.find(r => r.id === item.researcher)?.first_name }} {{ researchers.find(r => r.id === item.researcher)?.last_name }}
                    </div>
                    <button style="flex:0 0 100%;" v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff"
                        class="btn btn-success mt-2"
                        @click="onObservationEditClick(item)"
                        data-bs-toggle="modal"
                        data-bs-target="#editObservationModal">
                        <span>Редактировать</span>
                    </button>
                     
                </div>
                
                </template>
            </div>

         
         
        </div>
        <div v-else>
          <h2 class="mt-2">Пожалуйста, <a href="/">авторизуйтесь</a></h2>
        </div>  
         <div class="modal fade" id="editObservationModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="exampleModalLabel">
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
          <div class="row">
            <div class="col-6 mb-2">
                <div class="form-floating">
                  <select class="form-select" v-model="observationToEdit.space_object" required>
                    <option :value="b.id" v-for="b in spaceObjects" :key="b.id">
                      {{ b.name }}
                    </option>
                  </select>
                  <label for="floatingInput">Космический объект</label>
                </div>
            </div>
            <div class="col-6 mb-2">
                      <div class="form-floating">
                        <select class="form-select" v-model="observationToEdit.status"> 
                          <option value="planned">Запланировано</option>
                          <option value="in_progress">В процессе</option>
                          <option value="completed">Завершено</option>
                        </select>
                        <label for="floatingInput">Статус</label>
                      </div>
            </div>
            <div class="col-6 mb-2">
                  <div class="form-floating">
                      <input
                      type="date"
                      class="form-control"
                      v-model="observationToEdit.observation_date"
                      required
                      />
                      <label for="floatingInput">Дата наблюдения</label>
                  </div>
            </div>
             <div class="col-6 mb-2">
                <div class="form-floating">
                  <select class="form-select" v-model="observationToEdit.researcher" required>
                    <option :value="b.id" v-for="b in researchers" :key="b.id">
                      {{ b.first_name }}  {{ b.last_name }}
                    </option>
                  </select>
                  <label for="floatingInput">Исследователь</label>
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
            @click="onUpdateObservation"
          >
            Сохранить
          </button>
        </div>
      </div>
    </div>
</div>
</template>