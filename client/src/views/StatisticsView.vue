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
  <div class="container mt-4" v-if="is_authenticated && canSeeStatistics()">  
    <h2 class="text-center mb-4">Статистика обсерваторий</h2>

    <div class="card mb-4" v-if="observatoryStats">
      <div class="card-header bg-primary text-white">
        <h4>Статистика обсерваторий</h4>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-primary">{{ observatoryStats.aggregate_stats.total_count }}</h3>
              <p class="text-muted">Всего обсерваторий</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-success">{{ observatoryStats.aggregate_stats.astronomers_count }}</h3>
              <p class="text-muted">Всего астрономов</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-warning">{{ (observatoryStats.observatory_stats && observatoryStats.observatory_stats[0]?.astronomer_count) || 0 }}</h3>
              <p class="text-muted">Астрономов в топ-обсерватории</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-info">{{ Math.round(observatoryStats.aggregate_stats.astronomers_count / observatoryStats.aggregate_stats.total_count) || 0 }}</h3>
              <p class="text-muted">Среднее астрономов на обсерваторию</p>
            </div>
          </div>
        </div>
        <div class="row mt-3" v-if="observatoryStats.observatory_stats && observatoryStats.observatory_stats.length > 0">
          <div class="col">
            <div class="alert alert-info">
              <strong>Топ обсерватория по астрономам:</strong><br>
              {{ observatoryStats.observatory_stats[0].name }} ({{ observatoryStats.observatory_stats[0].astronomer_count }} астрономов)
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-4" v-if="astronomerStats">
      <div class="card-header bg-success text-white">
        <h4>Статистика астрономов</h4>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-primary">{{ astronomerStats.aggregate_stats.total_count }}</h3>
              <p class="text-muted">Всего астрономов</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-success">{{ astronomerStats.aggregate_stats.research_fields_count }}</h3>
              <p class="text-muted">Областей исследований</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-warning">{{ astronomerStats.aggregate_stats.observatories_count }}</h3>
              <p class="text-muted">Обсерваторий</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-info">{{ astronomerStats.aggregate_stats.observations_count }}</h3>
              <p class="text-muted">Всего наблюдений</p>
            </div>
          </div>
        </div>
        <div class="row mt-3" v-if="astronomerStats.specialization_stats && astronomerStats.specialization_stats.length > 0">
          <div class="col">
            <div class="alert alert-info">
              <strong>Самая популярная область исследований:</strong><br>
              {{ (astronomerStats.specialization_stats[0].specialization || astronomerStats.specialization_stats[0].research_field) }} ({{ astronomerStats.specialization_stats[0].count }} астрономов)
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-4" v-if="researcherStats">
      <div class="card-header bg-warning text-dark">
        <h4>Статистика исследователей</h4>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-4 mb-3">
            <div class="stat-card">
              <h3 class="text-primary">{{ researcherStats.aggregate_stats.total_count }}</h3>
              <p class="text-muted">Всего исследователей</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card">
              <h3 class="text-success">{{ researcherStats.aggregate_stats.with_user_account }}</h3>
              <p class="text-muted">С аккаунтом</p>
            </div>
          </div>
          <div class="col-md-4 mb-3">
            <div class="stat-card">
              <h3 class="text-danger">{{ researcherStats.aggregate_stats.observations_count }}</h3>
              <p class="text-muted">Всего наблюдений</p>
            </div>
          </div>
        </div>
        <div class="row mt-3" v-if="(researcherStats.top_patients_by_appointments && researcherStats.top_patients_by_appointments.length > 0) || (researcherStats.top_researchers_by_observations && researcherStats.top_researchers_by_observations.length > 0)">
          <div class="col">
            <div class="alert alert-info">
              <strong>Самый активный исследователь:</strong><br>
              {{ (researcherStats.top_patients_by_appointments?.[0]?.name) || (researcherStats.top_researchers_by_observations?.[0]?.name) }} ({{ (researcherStats.top_patients_by_appointments?.[0]?.appointment_count || researcherStats.top_patients_by_appointments?.[0]?.observation_count) || (researcherStats.top_researchers_by_observations?.[0]?.observation_count) }} записей)
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card mb-4" v-if="observationStats">
      <div class="card-header bg-info text-white">
        <h4>Статистика наблюдений</h4>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-primary">{{ observationStats.aggregate_stats.total_count }}</h3>
              <p class="text-muted">Всего наблюдений</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-success">{{ observationStats.aggregate_stats.completed_count }}</h3>
              <p class="text-muted">Завершено</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-warning">{{ observationStats.aggregate_stats.planned_count }}</h3>
              <p class="text-muted">Запланировано</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-danger">{{ observationStats.aggregate_stats.cancelled_count }}</h3>
              <p class="text-muted">Отменено</p>
            </div>
          </div>
        </div>
        <div class="row mt-3" v-if="observationStats.status_stats && observationStats.status_stats.length > 0">

        </div>
      </div>
    </div>

    <div class="card mb-4" v-if="observationRecordStats">
      <div class="card-header bg-secondary text-white">
        <h4>Статистика космических объектов</h4>
      </div>
      <div class="card-body">
        <div class="row text-center">
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-primary">{{ observationRecordStats.aggregate_stats.total_count }}</h3>
              <p class="text-muted">Всего объектов</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-success">{{ observationRecordStats.aggregate_stats.unique_astronomers }}</h3>
              <p class="text-muted">Уникальных астрономов</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-warning">{{ Math.round((observationRecordStats.aggregate_stats.total_count || 0) / (observationRecordStats.aggregate_stats.unique_astronomers || 1)) || 0 }}</h3>
              <p class="text-muted">Средне объектов на астронома</p>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="stat-card">
              <h3 class="text-info">{{ (observationRecordStats.top_astronomers_by_objects?.[0]?.object_count) || 0 }}</h3>
              <p class="text-muted">Объектов у топ-астронома</p>
            </div>
          </div>
        </div>
        <div class="row mt-3" v-if="observationRecordStats.top_astronomers_by_objects && observationRecordStats.top_astronomers_by_objects.length > 0">
          <div class="col">
            <div class="alert alert-info">
              <strong>Самый активный астроном:</strong><br>
              {{ observationRecordStats.top_astronomers_by_objects[0].astronomer__name }} ({{ observationRecordStats.top_astronomers_by_objects[0].object_count }} объектов)
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-2">Загрузка статистики...</p>
    </div>

    <div v-if="error" class="alert alert-danger text-center">
      {{ error }}
    </div>

  </div>

  <div v-else-if="is_authenticated">  <!-- Изменено -->
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

