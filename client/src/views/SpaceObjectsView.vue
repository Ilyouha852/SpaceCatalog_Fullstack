<script setup>
import { ref, onBeforeMount, computed } from 'vue'
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
const searchQuery = ref('')

const filteredSpaceObjects = computed(() => {
  if (!searchQuery.value || !spaceObjects.value.length) return spaceObjects.value
  const q = searchQuery.value.toLowerCase().trim()
  return spaceObjects.value.filter(o => {
    const name = (o.name || '').toLowerCase()
    const type = (o.object_type || '').toLowerCase()
    const astronomer = (o.astronomer_name || '').toLowerCase()
    return name.includes(q) || type.includes(q) || astronomer.includes(q)
  })
})

const resetFilters = () => {
  searchQuery.value = ''
}

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
  <div>
    <div class="p-2">
      <!-- page title removed to match other pages -->

      <el-card class="mb-4">
        <template #header><span>Фильтры объектов</span></template>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-input v-model="searchQuery" placeholder="Поиск по названию, типу или астроному...">
              <template #prefix><i class="bi bi-search"></i></template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button @click="resetFilters" type="info" plain>Сбросить</el-button>
          </el-col>
        </el-row>
        <div class="mt-2 text-muted">Найдено объектов: {{ filteredSpaceObjects.length }}</div>
      </el-card>

      <div v-if="loading">Загрузка данных...</div>

      <div v-else>
        <div v-if="is_superuser || userInfoStore.isAdmin()" class="mb-3">
          <el-card>
            <template #header><h5>Добавить объект</h5></template>
            <el-row :gutter="12" align="end">
              <el-col :span="4"><el-input v-model="newObject.name" placeholder="Имя" /></el-col>
              <el-col :span="4"><el-input v-model="newObject.object_type" placeholder="Тип" /></el-col>
              <el-col :span="4">
                <el-select v-model="newObject.astronomer" placeholder="Выберите астронома">
                  <el-option v-for="a in astronomers" :key="a.id" :label="a.name" :value="a.id" />
                </el-select>
              </el-col>
              <el-col :span="4"><el-button type="primary" @click="onAddObject">Добавить</el-button></el-col>
            </el-row>
          </el-card>
        </div>

        <div v-if="editObject" class="mb-3">
          <el-card>
            <template #header><h5>Редактировать объект</h5></template>
            <el-row :gutter="12" align="end">
              <el-col :span="4"><el-input v-model="editObject.name" /></el-col>
              <el-col :span="4"><el-input v-model="editObject.object_type" /></el-col>
              <el-col :span="4"><el-select v-model="editObject.astronomer" placeholder="Астроном"><el-option v-for="a in astronomers" :key="a.id" :label="a.name" :value="a.id" /></el-select></el-col>
              <el-col :span="4">
                <el-button type="success" @click="onUpdateObject">Сохранить</el-button>
                <el-button @click="editObject = null" style="margin-left:8px">Отмена</el-button>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div class="mb-3">
          <el-button @click="exportToExcel" type="success" :disabled="loadingExport">{{ loadingExport ? 'Экспорт...' : 'Экспорт в Excel' }}</el-button>
        </div>

        <div v-if="!filteredSpaceObjects.length">Нет объектов</div>
        <div v-else>
          <el-row :gutter="16">
            <el-col :span="8" v-for="obj in filteredSpaceObjects" :key="obj.id">
              <el-card class="space-object-card">
                <div><strong>{{ obj.name }}</strong></div>
                <div class="text-muted">{{ obj.object_type }}</div>
                <div>{{ obj.astronomer_name || obj.astronomer }}</div>
                <div class="mt-2">
                  <el-button size="mini" @click="startEdit(obj)">Редактировать</el-button>
                  <el-button size="mini" type="danger" @click="onDeleteObject(obj)">Удалить</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>
  </div>
</template>
