<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useUserStore } from '@/stores/user_store'
import { useDataStore } from '@/stores/data_store'
import { storeToRefs } from 'pinia'
import TwoFactorModal from '@/components/TwoFactorModal.vue'
import { Download } from '@element-plus/icons-vue'

import {
  ElCollapse,
  ElCollapseItem,
  ElCard,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElTable,
  ElTableColumn,
  ElStatistic,
  ElAlert,
  ElTag,
  ElRow,
  ElCol,
  ElDivider,
  ElBadge
} from 'element-plus'

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

const dataStore = useDataStore()
const { 
  researchers, 
  spaceObjects, 
  objectTypes, 
  astronomers, 
  observations,
  astronomersStats,
  objectTypesStats,
  spaceObjectsStats,
  researchersStats,
  observationsStats
} = storeToRefs(dataStore)

const twoFAStatus = ref({
  is_verified: false,
  authenticated: false,
  remaining_seconds: 0,
  remaining_minutes: 0
})
const show2FAModal = ref(false)
let twoFATimer = null

onMounted(async () => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')

  await dataStore.fetchAllData()
  await dataStore.fetchAllStats()

  check2FAStatus()
  twoFATimer = setInterval(check2FAStatus, 1000)
})

onBeforeUnmount(() => {
  if (twoFATimer) clearInterval(twoFATimer)
})

const check2FAStatus = async () => {
  try {
    const { data } = await axios.get('/api/user/check_2fa_status/')
    twoFAStatus.value = data
  } catch (e) {  }
}

const filters = ref({
  astronomers: '',
  objectTypes: '',
  spaceObjects: { name: '', type: '', yearFrom: '', yearTo: '' },
  researchers: '',
  observations: { object: '', status: '', researcher: '' }
})

const filteredAstronomers = computed(() => {
  if (!filters.value.astronomers) return astronomers.value
  const term = filters.value.astronomers.toLowerCase()
  return astronomers.value.filter(a =>
    (a.name || '').toLowerCase().includes(term) || (a.bio || '').toLowerCase().includes(term)
  )
})

const uniqueObjectTypes = computed(() => {
  const seen = new Set()
  return objectTypes.value.filter(t => {
    if (seen.has(t.name)) return false
    seen.add(t.name)
    return true
  })
})

const filteredObjectTypes = computed(() => {
  if (!filters.value.objectTypes) return uniqueObjectTypes.value
  const term = filters.value.objectTypes.toLowerCase()
  return uniqueObjectTypes.value.filter(t =>
    (t.name || '').toLowerCase().includes(term) || (t.description || '').toLowerCase().includes(term)
  )
})

const filteredSpaceObjects = computed(() => {
  let res = spaceObjects.value

  if (filters.value.spaceObjects.name) {
    const term = filters.value.spaceObjects.name.toLowerCase()
    res = res.filter(o => (o.name || '').toLowerCase().includes(term) || (o.description || '').toLowerCase().includes(term))
  }
  if (filters.value.spaceObjects.type) {
    res = res.filter(o => o.object_type == filters.value.spaceObjects.type)
  }
  if (filters.value.spaceObjects.yearFrom) {
    const y = parseInt(filters.value.spaceObjects.yearFrom)
    res = res.filter(o => o.discovery_year >= y)
  }
  if (filters.value.spaceObjects.yearTo) {
    const y = parseInt(filters.value.spaceObjects.yearTo)
    res = res.filter(o => o.discovery_year <= y)
  }
  return res
})

const filteredResearchers = computed(() => {
  if (!filters.value.researchers) return researchers.value
  const term = filters.value.researchers.toLowerCase()
  return researchers.value.filter(r =>
    `${r.first_name || ''} ${r.last_name || ''}`.toLowerCase().includes(term) ||
    (r.email || '').toLowerCase().includes(term) ||
    (r.card_number || '').toLowerCase().includes(term)
  )
})

const filteredObservations = computed(() => {
  let res = observations.value

  if (filters.value.observations.object) {
    const term = filters.value.observations.object.toLowerCase()
    res = res.filter(o => {
      const obj = spaceObjects.value.find(s => s.id === o.space_object)
      return (obj?.name || '').toLowerCase().includes(term)
    })
  }
  if (filters.value.observations.status) {
    res = res.filter(o => o.status === filters.value.observations.status)
  }
  if (filters.value.observations.researcher) {
    res = res.filter(o => o.researcher == filters.value.observations.researcher)
  }
  return res
})

const statusTagType = status => {
  return status === 'completed' ? 'success' :
         status === 'in_progress' ? 'warning' :
         status === 'planned' ? 'info' : 'primary'
}

const statusText = status => {
  return status === 'planned' ? 'Запланировано' :
         status === 'in_progress' ? 'В процессе' :
         status === 'completed' ? 'Завершено' : status
}

const expandedIds = ref(new Set())
const isExpanded = (id) => expandedIds.value.has(id)
const toggleExpand = (id) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

const exportToExcel = (endpoint, filename) => {
    dataStore.exportToExcel(endpoint, filename)
}
</script>

<template>
  <div class="container py-5">
    <div v-if="userInfo?.is_authenticated" class="mb-4">
      <h3 class="mb-3">Здравствуй, {{ userInfo.username }}!</h3>

      <ElAlert
        :type="twoFAStatus.is_verified ? 'success' : 'warning'"
        :closable="false"
        show-icon
        class="mb-4"
      >
        <template #title>
          <strong>Статус 2FA:</strong>
          <ElBadge v-if="twoFAStatus.is_verified" type="success" class="ms-2">
            Подтверждено (осталось {{ twoFAStatus.remaining_minutes }} мин {{ twoFAStatus.remaining_seconds % 60 }} сек)
          </ElBadge>
          <ElBadge v-else type="warning" class="ms-2">Не подтверждено</ElBadge>
        </template>
        <template #default>
          <small class="d-block mt-2">
            Двухфакторная аутентификация (TOTP) требуется для редактирования данных.
          </small>
          <ElButton
            v-if="!twoFAStatus.is_verified"
            type="primary"
            size="small"
            class="mt-2"
            @click="show2FAModal = true"
          >
            Пройти 2FA
          </ElButton>
        </template>
      </ElAlert>
    </div>

    <h1 class="text-center mb-5">Справочник космических объектов</h1>

    <ElCollapse accordion>
      <ElCollapseItem title="Астрономы" name="astronomers">
        <template #title>
          <div class="w-100 d-flex justify-content-between align-items-center pe-4">
            <strong>Астрономы ({{ filteredAstronomers.length }})</strong>
          </div>
        </template>

        <div class="d-flex justify-content-end mb-4">
        <ElButton
            type="success"
            size="large"
            :icon="Download"
            @click="exportToExcel('/api/astronomers/export_excel/', 'Астрономы.xlsx')"
            class="export-excel-btn"
        >
            Экспорт в Excel
        </ElButton>
        </div>

        <ElInput
          v-model="filters.astronomers"
          placeholder="Поиск по имени или биографии..."
          clearable
          class="mb-4"
          prefix-icon="Search"
        />

        <ElCard v-if="astronomersStats" shadow="never" class="mb-4">
          <ElStatistic title="Всего астрономов" :value="astronomersStats.total_count" />
          <ElDivider />
          <div v-if="astronomersStats.top_astronomers?.length">
            <strong>Топ-5 по открытиям:</strong>
            <ul class="mt-2 mb-0">
              <li v-for="a in astronomersStats.top_astronomers" :key="a.name">
                {{ a.name }} — {{ a.discoveries_count }} открытий
              </li>
            </ul>
          </div>
        </ElCard>

        <ElRow :gutter="20">
          <ElCol v-for="a in filteredAstronomers" :key="a.id" :md="12" :lg="8" class="mb-4">
            <ElCard shadow="hover">
              <template #header>
                <div class="d-flex align-items-center justify-content-between">
                  <h5 class="mb-0">{{ a.name }}</h5>
                  <ElImage
                    :src="a.picture"
                    style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; cursor: pointer;"
                    fit="cover"
                    :preview-src-list="[a.picture]"
                  />
                </div>
              </template>
              <div class="astronomer-bio">
                <p :class="{'expanded': isExpanded(a.id), 'collapsed': !isExpanded(a.id)}">
                  {{ a.bio }}
                </p>
                <ElButton 
                  v-if="a.bio && a.bio.length > 150" 
                  type="primary" 
                  link 
                  @click="toggleExpand(a.id)"
                >
                  {{ isExpanded(a.id) ? 'Свернуть' : 'Показать полностью' }}
                </ElButton>
              </div>
            </ElCard>
          </ElCol>
        </ElRow>
      </ElCollapseItem>

      <ElCollapseItem v-if="userInfo?.is_staff" title="Типы объектов" name="types">
        <template #title>
          <div class="w-100 d-flex justify-content-between align-items-center pe-4">
            <strong>Типы объектов ({{ filteredObjectTypes.length }})</strong>
          </div>
        </template>

        <div class="d-flex justify-content-end mb-4">
        <ElButton
            type="success"
            size="large"
            :icon="Download"
            @click="exportToExcel('/api/objecttypes/export_excel/', 'Типы_объектов.xlsx')"
            class="export-excel-btn"
        >
            Экспорт в Excel
        </ElButton>
        </div>
        
        <ElInput
          v-model="filters.objectTypes"
          placeholder="Поиск по названию типа..."
          clearable
          class="mb-4"
          prefix-icon="Search"
        />

        <ElCard v-if="objectTypesStats" shadow="never" class="mb-4">
          <ElStatistic title="Всего типов" :value="objectTypesStats.total_count" />
          <ElDivider />
          <strong>Топ-10 по количеству объектов:</strong>
          <ul class="mt-2">
            <li v-for="t in objectTypesStats.distribution?.slice(0,10)" :key="t.name">
              {{ t.name }} — {{ t.objects_count }}
            </li>
          </ul>
        </ElCard>

        <ElRow :gutter="20">
          <ElCol v-for="t in filteredObjectTypes" :key="t.id" :md="8" :lg="6" class="mb-4">
            <ElCard shadow="hover">
              <h5>{{ t.name }}</h5>
              <p class="text-muted small">{{ t.description }}</p>
            </ElCard>
          </ElCol>
        </ElRow>
      </ElCollapseItem>

      <ElCollapseItem title="Космические объекты" name="objects">
        <template #title>
          <div class="w-100 d-flex justify-content-between align-items-center pe-4">
            <strong>Космические объекты ({{ filteredSpaceObjects.length }})</strong>
          </div>
        </template>

        <div class="d-flex justify-content-end mb-4">
        <ElButton
            type="success"
            size="large"
            :icon="Download"
            @click="exportToExcel('/api/spaceobjects/export_excel/', 'Космические_объекты.xlsx')"
            class="export-excel-btn"
        >
            Экспорт в Excel
        </ElButton>
        </div>

        <div class="mb-4">
          <ElRow :gutter="12">
            <ElCol :span="8">
              <ElInput
                v-model="filters.spaceObjects.name"
                placeholder="Поиск по названию..."
                clearable
                prefix-icon="Search"
              />
            </ElCol>
            <ElCol :span="8">
              <ElSelect v-model="filters.spaceObjects.type" placeholder="Тип объекта" clearable class="w-100">
                <ElOption
                  v-for="t in uniqueObjectTypes"
                  :key="t.id"
                  :label="t.name"
                  :value="t.id"
                />
              </ElSelect>
            </ElCol>
            <ElCol :span="4">
              <ElInputNumber
                v-model="filters.spaceObjects.yearFrom"
                placeholder="Год от"
                :min="0"
                controls-position="right"
                class="w-100"
              />
            </ElCol>
            <ElCol :span="4">
              <ElInputNumber
                v-model="filters.spaceObjects.yearTo"
                placeholder="Год до"
                :min="0"
                controls-position="right"
                class="w-100"
              />
            </ElCol>
          </ElRow>
        </div>

        <ElCard v-if="spaceObjectsStats" shadow="never" class="mb-4">
          <ElRow :gutter="20">
            <ElCol :span="8">
              <ElStatistic title="Всего объектов" :value="spaceObjectsStats.total_count" />
            </ElCol>
            <ElCol :span="8">
              <ElStatistic title="Среднее расстояние" :value="spaceObjectsStats.avg_distance" suffix=" св. лет" />
            </ElCol>
            <ElCol :span="8">
              <ElStatistic title="Средняя масса" :value="spaceObjectsStats.avg_mass" suffix=" M⊙" />
            </ElCol>
          </ElRow>
        </ElCard>

        <ElRow :gutter="20">
          <ElCol v-for="obj in filteredSpaceObjects" :key="obj.id" :md="12" :lg="8" class="mb-4">
            <ElCard shadow="hover">
              <template #header>
                <h5 class="mb-0">{{ obj.name }}</h5>
              </template>
              <p>
                <strong>Открыватель:</strong> {{ dataStore.getAstronomerName(obj.astronomer) }}<br>
                <strong>Год:</strong> {{ obj.discovery_year }}<br>
                <strong>Тип:</strong> {{ dataStore.getObjectTypeName(obj.object_type) }}<br>
                <template v-if="obj.distance">
                  <strong>Расстояние:</strong> {{ obj.distance }} св. лет<br>
                </template>
                <template v-if="obj.mass">
                  <strong>Масса:</strong> {{ obj.mass }} M⊙<br>
                </template>
                <strong>Описание:</strong> {{ obj.description }}
              </p>
            </ElCard>
          </ElCol>
        </ElRow>
      </ElCollapseItem>

      <ElCollapseItem title="Исследователи" name="researchers">
        <template #title>
          <div class="w-100 d-flex justify-content-between align-items-center pe-4">
            <strong>Исследователи ({{ filteredResearchers.length }})</strong>
          </div>
        </template>

        <div class="d-flex justify-content-end mb-4">
        <ElButton
            type="success"
            size="large"
            :icon="Download"
            @click="exportToExcel('/api/researchers/export_excel/', 'Исследователи.xlsx')"
            class="export-excel-btn"
        >
            Экспорт в Excel
        </ElButton>
        </div>

        <ElInput
          v-model="filters.researchers"
          placeholder="Поиск по имени, email, номеру..."
          clearable
          class="mb-4"
          prefix-icon="Search"
        />

        <ElCard v-if="researchersStats" shadow="never" class="mb-4">
          <ElStatistic title="Всего" :value="researchersStats.total_count" />
          <ElStatistic title="Активных" :value="researchersStats.active_count" class="ms-4" />
        </ElCard>

        <ElRow :gutter="20">
          <ElCol v-for="r in filteredResearchers" :key="r.id" :md="12" :lg="8" class="mb-4">
            <ElCard shadow="hover">
              <template #header>
                <div class="d-flex align-items-center">
                  <ElImage
                    :src="r.picture"
                    style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover;"
                    fit="cover"
                    :preview-src-list="[r.picture]"
                  />
                  <div class="ms-3">
                    <h5 class="mb-0">{{ r.first_name }} {{ r.last_name }}</h5>
                    <small>{{ r.email }}</small>
                  </div>
                </div>
              </template>
              <p class="mb-0"><strong>№:</strong> {{ r.card_number }}</p>
            </ElCard>
          </ElCol>
        </ElRow>
      </ElCollapseItem>

      <ElCollapseItem v-if="userInfo?.is_authenticated" title="Наблюдения" name="observations">
        <template #title>
          <div class="w-100 d-flex justify-content-between align-items-center pe-4">
            <strong>Наблюдения ({{ filteredObservations.length }})</strong>
          </div>
        </template>

        <div class="d-flex justify-content-end mb-4">
        <ElButton
            type="success"
            size="large"
            :icon="Download"
            @click="exportToExcel('/api/observations/export_excel/', 'Наблюдения.xlsx')"
            class="export-excel-btn"
        >
            Экспорт в Excel
        </ElButton>
        </div>

        <ElRow :gutter="12" class="mb-4">
          <ElCol :span="8">
            <ElInput
              v-model="filters.observations.object"
              placeholder="Объект..."
              clearable
              prefix-icon="Search"
            />
          </ElCol>
          <ElCol :span="8">
            <ElSelect v-model="filters.observations.status" placeholder="Статус" clearable class="w-100">
              <ElOption label="Запланировано" value="planned" />
              <ElOption label="В процессе" value="in_progress" />
              <ElOption label="Завершено" value="completed" />
            </ElSelect>
          </ElCol>
          <ElCol :span="8">
            <ElSelect v-model="filters.observations.researcher" placeholder="Исследователь" clearable class="w-100">
              <ElOption
                v-for="r in researchers"
                :key="r.id"
                :label="`${r.first_name} ${r.last_name}`"
                :value="r.id"
              />
            </ElSelect>
          </ElCol>
        </ElRow>

        <ElCard v-if="observationsStats" shadow="never" class="mb-4">
          <ElStatistic title="Всего наблюдений" :value="observationsStats.total_count" />
          <ElDivider />
          <ElRow>
            <ElCol :span="8">Запланировано: {{ observationsStats.by_status?.planned || 0 }}</ElCol>
            <ElCol :span="8">В процессе: {{ observationsStats.by_status?.in_progress || 0 }}</ElCol>
            <ElCol :span="8">Завершено: {{ observationsStats.by_status?.completed || 0 }}</ElCol>
          </ElRow>
        </ElCard>

        <ElTable :data="filteredObservations" stripe style="width: 100%">
          <ElTableColumn prop="space_object" label="Объект">
            <template #default="{ row }">
              {{ spaceObjects.find(o => o.id === row.space_object)?.name || '—' }}
            </template>
          </ElTableColumn>
          <ElTableColumn label="Статус" width="140">
            <template #default="{ row }">
              <ElTag :type="statusTagType(row.status)">
                {{ statusText(row.status) }}
              </ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="observation_date" label="Дата" width="120" />
          <ElTableColumn label="Исследователь" width="200">
            <template #default="{ row }">
              {{ dataStore.getResearcherName(row.researcher) }}
            </template>
          </ElTableColumn>
        </ElTable>
      </ElCollapseItem>
    </ElCollapse>

    <TwoFactorModal :show="show2FAModal" @verified="check2FAStatus" @close="show2FAModal = false" />
  </div>
</template>

<style scoped>
.el-collapse-item__header {
  font-size: 1.25rem;
  font-weight: 600;
}

.astronomer-bio {
  min-height: 120px;
}

.astronomer-bio p {
  margin-bottom: 0.5rem;
  color: inherit;
}

.astronomer-bio p.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

</style>