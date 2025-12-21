import { defineStore } from 'pinia'
import axios from 'axios'
import { ElMessage } from 'element-plus'

export const useDataStore = defineStore('data', {
    state: () => ({
        researchers: [],
        spaceObjects: [],
        objectTypes: [],
        astronomers: [],
        observations: [],

        astronomersStats: null,
        objectTypesStats: null,
        spaceObjectsStats: null,
        researchersStats: null,
        observationsStats: null,
    }),

    actions: {
        async fetchResearchers() {
            try {
                const response = await axios.get('/api/researchers')
                this.researchers = response.data
            } catch (error) {
                console.error('Error fetching researchers:', error)
            }
        },
        async fetchSpaceObjects() {
            try {
                const response = await axios.get('/api/spaceobjects')
                this.spaceObjects = response.data
            } catch (error) {
                console.error('Error fetching space objects:', error)
            }
        },
        async fetchObjectTypes() {
            try {
                const response = await axios.get('/api/objecttypes')
                this.objectTypes = response.data
            } catch (error) {
                console.error('Error fetching object types:', error)
            }
        },
        async fetchAstronomers() {
            try {
                const response = await axios.get('/api/astronomers')
                this.astronomers = response.data
            } catch (error) {
                console.error('Error fetching astronomers:', error)
            }
        },
        async fetchObservations() {
            try {
                const response = await axios.get('/api/observations')
                this.observations = response.data
            } catch (error) {
                console.error('Error fetching observations:', error)
            }
        },

        async fetchAstronomersStats() {
            try {
                const response = await axios.get('/api/astronomers/statistics/')
                this.astronomersStats = response.data
            } catch (error) { }
        },
        async fetchObjectTypesStats() {
            try {
                const response = await axios.get('/api/objecttypes/statistics/')
                this.objectTypesStats = response.data
            } catch (error) { }
        },
        async fetchSpaceObjectsStats() {
            try {
                const response = await axios.get('/api/spaceobjects/statistics/')
                this.spaceObjectsStats = response.data
            } catch (error) { }
        },
        async fetchResearchersStats() {
            try {
                const response = await axios.get('/api/researchers/statistics/')
                this.researchersStats = response.data
            } catch (error) { }
        },
        async fetchObservationsStats() {
            try {
                const response = await axios.get('/api/observations/statistics/')
                this.observationsStats = response.data
            } catch (error) { }
        },

        async fetchAllData() {
            await Promise.all([
                this.fetchResearchers(),
                this.fetchSpaceObjects(),
                this.fetchObjectTypes(),
                this.fetchAstronomers(),
                this.fetchObservations()
            ])
        },

        async fetchAllStats() {
            await Promise.all([
                this.fetchAstronomersStats(),
                this.fetchObjectTypesStats(),
                this.fetchSpaceObjectsStats(),
                this.fetchResearchersStats(),
                this.fetchObservationsStats()
            ])
        },

        async exportToExcel(endpoint, filename) {
            try {
                const response = await axios.get(endpoint, {
                    responseType: 'blob'
                })

                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', filename)
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                window.URL.revokeObjectURL(url)

                ElMessage.success('Экспорт завершён: ' + filename)
            } catch (error) {
                ElMessage.error('Ошибка при экспорте в Excel')
                console.error(error)
            }
        }
    },

    getters: {
        getAstronomerName: (state) => (id) => {
            return state.astronomers.find(a => a.id === id)?.name || '—'
        },
        getObjectTypeName: (state) => (id) => {
            return state.objectTypes.find(t => t.id === id)?.name || 'Не указан'
        },
        getResearcherName: (state) => (id) => {
            const r = state.researchers.find(re => re.id === id)
            return r ? `${r.first_name} ${r.last_name}` : 'Не назначен'
        }
    }
})
