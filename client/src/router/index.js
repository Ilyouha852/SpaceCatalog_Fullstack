
import AstronomersView from '@/views/AstronomersView.vue'
import ObservationsView from '@/views/ObservationsView.vue'
import SpaceObjectsView from '@/views/SpaceObjectsView.vue'
import ObjectTypesView from '@/views/ObjectTypesView.vue'
import CatalogView from '@/views/CatalogView.vue'
import ResearchersView from '@/views/ResearchersView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: CatalogView
    },
    {
      path: '/astronomers',
      component: AstronomersView
    },
    {
      path: '/spaceobjects',
      component: SpaceObjectsView
    },
    {
      path: '/researchers',
      component: ResearchersView
    },
    {
      path: '/objecttypes',
      component: ObjectTypesView
    },
    {
      path: '/observations',
      component: ObservationsView
    }],
})

export default router
