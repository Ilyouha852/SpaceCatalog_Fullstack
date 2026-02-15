<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { storeToRefs } from "pinia";
import { useUserInfoStore } from "@/stores/user_info_store";  // Изменено

const observatoryStats = ref(null)
const astronomerStats = ref(null)
const researcherStats = ref(null)
const observationStats = ref(null)
const observationRecordStats = ref(null)
const loading = ref(false)
const error = ref(null)

async function loadObservatoryStats() {
  const response = await axios.get('/api/observatories/stats/')
  observatoryStats.value = response.data
}

async function loadAstronomerStats() {
  const response = await axios.get('/api/astronomers/stats/')
  astronomerStats.value = response.data
}

async function loadResearcherStats() {
  const response = await axios.get('/api/researchers/stats/')
  researcherStats.value = response.data
}

async function loadObservationStats() {
  const response = await axios.get('/api/observations/stats/')
  observationStats.value = response.data
}

async function loadObservationRecordStats() {
  const response = await axios.get('/api/space-objects/stats/')
  observationRecordStats.value = response.data
}

async function loadAllStats() {
  loading.value = true
  try {
    await Promise.all([
      loadObservatoryStats(),
      loadAstronomerStats(),
      loadResearcherStats(),
      loadObservationStats(),
      loadObservationRecordStats()
    ])
  } catch (err) {
    error.value = 'Ошибка при загрузке статистики'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllStats()
})

const userInfoStore = useUserInfoStore()  
const { is_authenticated, is_superuser, can_see_statistics } = storeToRefs(userInfoStore)  

const canSeeStatistics = () => {
  return is_superuser || can_see_statistics || userInfoStore.hasPermission('can_see_statistics_page') || userInfoStore.isAdmin()
}
</script>

<template>
  <div v-if="is_authenticated && canSeeStatistics()">
    <h2 class="text-center mb-4">Статистика</h2>

    <el-row :gutter="16">
      <el-col :span="12" v-if="observatoryStats">
        <el-card>
          <template #header><h4>Статистика обсерваторий</h4></template>
          <el-row>
            <el-col :span="6"><div class="stat-card"><h3>{{ observatoryStats.aggregate_stats.total_count }}</h3><p class="text-muted">Всего обсерваторий</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ observatoryStats.aggregate_stats.astronomers_count }}</h3><p class="text-muted">Всего астрономов</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ (observatoryStats.observatory_stats && observatoryStats.observatory_stats[0]?.astronomer_count) || 0 }}</h3><p class="text-muted">Астрономов в топ-обсерватории</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ Math.round(observatoryStats.aggregate_stats.astronomers_count / observatoryStats.aggregate_stats.total_count) || 0 }}</h3><p class="text-muted">Среднее астрономов на обсерваторию</p></div></el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12" v-if="astronomerStats">
        <el-card>
          <template #header><h4>Статистика астрономов</h4></template>
          <el-row>
            <el-col :span="6"><div class="stat-card"><h3>{{ astronomerStats.aggregate_stats.total_count }}</h3><p class="text-muted">Всего астрономов</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ astronomerStats.aggregate_stats.research_fields_count }}</h3><p class="text-muted">Областей исследований</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ astronomerStats.aggregate_stats.observatories_count }}</h3><p class="text-muted">Обсерваторий</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ astronomerStats.aggregate_stats.observations_count }}</h3><p class="text-muted">Всего наблюдений</p></div></el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-3">
      <el-col :span="12" v-if="researcherStats">
        <el-card>
          <template #header><h4>Статистика исследователей</h4></template>
          <el-row>
            <el-col :span="8"><div class="stat-card"><h3>{{ researcherStats.aggregate_stats.total_count }}</h3><p class="text-muted">Всего исследователей</p></div></el-col>
            <el-col :span="8"><div class="stat-card"><h3>{{ researcherStats.aggregate_stats.with_user_account }}</h3><p class="text-muted">С аккаунтом</p></div></el-col>
            <el-col :span="8"><div class="stat-card"><h3>{{ researcherStats.aggregate_stats.observations_count }}</h3><p class="text-muted">Всего наблюдений</p></div></el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12" v-if="observationStats">
        <el-card>
          <template #header><h4>Статистика наблюдений</h4></template>
          <el-row>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationStats.aggregate_stats.total_count }}</h3><p class="text-muted">Всего наблюдений</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationStats.aggregate_stats.completed_count }}</h3><p class="text-muted">Завершено</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationStats.aggregate_stats.planned_count }}</h3><p class="text-muted">Запланировано</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationStats.aggregate_stats.cancelled_count }}</h3><p class="text-muted">Отменено</p></div></el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="mt-3" v-if="observationRecordStats">
      <el-col :span="12">
        <el-card>
          <template #header><h4>Статистика космических объектов</h4></template>
          <el-row>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationRecordStats.aggregate_stats.total_count }}</h3><p class="text-muted">Всего объектов</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ observationRecordStats.aggregate_stats.unique_astronomers }}</h3><p class="text-muted">Уникальных астрономов</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ Math.round((observationRecordStats.aggregate_stats.total_count || 0) / (observationRecordStats.aggregate_stats.unique_astronomers || 1)) || 0 }}</h3><p class="text-muted">Средне объектов на астронома</p></div></el-col>
            <el-col :span="6"><div class="stat-card"><h3>{{ (observationRecordStats.top_astronomers_by_objects?.[0]?.object_count) || 0 }}</h3><p class="text-muted">Объектов у топ-астронома</p></div></el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <div v-if="loading">Загрузка данных...</div>
    <el-alert v-if="error" type="error" :title="error" />
  </div>

  <div v-else-if="is_authenticated">
    <h2 class="mt-2 text-center">Эта информация доступна только для администраторов и пользователей с правами доступа к статистике</h2>
  </div>
  <div v-else>
    <h2 class="mt-2 text-center">Вы не авторизованы</h2>
    <p class="text-center">Пожалуйста, войдите в систему для просмотра статистики</p>
  </div>
</template>

<style scoped>
.stat-card {
  padding: 15px;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.card-header h4 {
  margin-bottom: 0;
}

.alert {
  margin-bottom: 0;
}
</style>

