<script setup>
import { ref, onBeforeMount } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useUserInfoStore } from '@/stores/user_info_store'
import { storeToRefs } from 'pinia'

const userInfoStore = useUserInfoStore()
const { is_superuser } = storeToRefs(userInfoStore)

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
})

const loading = ref(false)
const loadingExport = ref(false)
const spaceObjects = ref([])
const astronomers = ref([])

const newObject = ref({ name: '', object_type: '', astronomer: '' })
const editObject = ref(null)

async function fetchSpaceObjects() {
  loading.value = true
  try {
    const r = await axios.get('/api/space-objects/')
    spaceObjects.value = r.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchAstronomers() {
  try {
    const r = await axios.get('/api/astronomers/')
    astronomers.value = r.data
  } catch (e) {
    console.error(e)
  }
}

async function onAddObject() {
  try {
    await axios.post('/api/space-objects/', newObject.value)
    newObject.value = { name: '', object_type: '', astronomer: '' }
    await fetchSpaceObjects()
  } catch (e) {
    console.error('Create failed', e)
    alert('Ошибка при создании объекта')
  }
}

function startEdit(obj) {
  editObject.value = { ...obj }
}

async function onUpdateObject() {
  try {
    await axios.put(`/api/space-objects/${editObject.value.id}/`, editObject.value)
    editObject.value = null
    await fetchSpaceObjects()
  } catch (e) {
    console.error('Update failed', e)
    alert('Ошибка при обновлении')
  }
}

async function onDeleteObject(obj) {
  if (!confirm('Удалить объект?')) return
  try {
    await axios.delete(`/api/space-objects/${obj.id}/`)
    await fetchSpaceObjects()
  } catch (e) {
    console.error('Delete failed', e)
    alert('Ошибка при удалении')
  }
}

onBeforeMount(async () => {
  await Promise.all([fetchSpaceObjects(), fetchAstronomers()])
})

async function exportToExcel() {
  loadingExport.value = true
  try {
    const response = await axios.get('/api/space-objects/export-excel/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'space_objects.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (e) {
    console.error('Ошибка при экспорте:', e)
    alert('Ошибка при экспорте данных')
  } finally {
    loadingExport.value = false
  }
}
</script>

<template>
  <div class="container-fluid">
    <div class="p-2">
      <h4>Космические объекты</h4>

      <div class="mb-3">
        <button @click="exportToExcel" class="btn btn-success" :disabled="loadingExport">
          <i class="bi bi-file-earmark-excel"></i>
          {{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}
        </button>
      </div>

      <div v-if="loading">Загрузка данных...</div>

      <div v-else>
        <div v-if="is_superuser || userInfoStore.isAdmin()" class="mb-3">
          <h5>Добавить объект</h5>
          <div class="row g-2 align-items-end">
            <div class="col-md-4">
              <input class="form-control" placeholder="Имя" v-model="newObject.name" />
            </div>
            <div class="col-md-3">
              <input class="form-control" placeholder="Тип" v-model="newObject.object_type" />
            </div>
            <div class="col-md-3">
              <select class="form-select" v-model="newObject.astronomer">
                <option value="">-- выбрать астронома --</option>
                <option v-for="a in astronomers" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary w-100" @click="onAddObject">Добавить</button>
            </div>
          </div>
        </div>

        <div v-if="editObject" class="card mb-3 p-3">
          <h5>Редактировать объект</h5>
          <div class="row g-2 align-items-end">
            <div class="col-md-4">
              <input class="form-control" v-model="editObject.name" />
            </div>
            <div class="col-md-3">
              <input class="form-control" v-model="editObject.object_type" />
            </div>
            <div class="col-md-3">
              <select class="form-select" v-model="editObject.astronomer">
                <option value="">-- выбрать астронома --</option>
                <option v-for="a in astronomers" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-success w-100" @click="onUpdateObject">Сохранить</button>
            </div>
          </div>
        </div>

        <div v-if="!spaceObjects.length">Нет объектов</div>
        <div v-else>
          <table class="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Тип</th>
                <th>Астроном</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="obj in spaceObjects" :key="obj.id">
                <td>{{ obj.id }}</td>
                <td>{{ obj.name }}</td>
                <td>{{ obj.object_type }}</td>
                <td>{{ obj.astronomer_name || obj.astronomer }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-secondary me-2" @click="startEdit(obj)">Редактировать</button>
                  <button class="btn btn-sm btn-danger" @click="onDeleteObject(obj)">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="editObject" class="card mt-3 p-3">
          <h5>Редактировать объект</h5>
          <div class="row g-2 align-items-end">
            <div class="col-md-4">
              <input class="form-control" v-model="editObject.name" />
            </div>
            <div class="col-md-3">
              <input class="form-control" v-model="editObject.object_type" />
            </div>
            <div class="col-md-3">
              <select class="form-select" v-model="editObject.astronomer">
                <option value="">-- выбрать астронома --</option>
                <option v-for="a in astronomers" :key="a.id" :value="a.id">{{ a.name }}</option>
              </select>
            </div>
            <div class="col-md-2">
              <button class="btn btn-success w-100" @click="onUpdateObject">Сохранить</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
