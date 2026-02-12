import { createRouter, createWebHistory } from 'vue-router'
import ObservatoriesView from '@/views/ObservatoriesView.vue';
import AstronomersView from '@/views/AstronomersView.vue';
import ResearchersView from '@/views/ResearchersView.vue';
import ObservationsView from '@/views/ObservationsView.vue';
import SpaceObjectsView from '@/views/SpaceObjectsView.vue';
import LoginView from '@/views/LoginView.vue';
import StatisticsView from '@/views/StatisticsView.vue';
import SecondAuthView from '@/views/SecondAuthView.vue';
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "ObservatoriesView",
      component: ObservatoriesView,
    },
    {
      path: "/login",
      name: "Login",
      component: LoginView
    },
    {
      path: "/astronomers",
      name: "AstronomersView",
      component: AstronomersView,
    },
    {
      path: "/researchers",
      name: "ResearchersView",
      component: ResearchersView,
    },
    {
      path: "/observations",
      name: "ObservationsView",
      component: ObservationsView,
    },
    {
      path: "/space-objects",
      name: "SpaceObjectsView",
      component: SpaceObjectsView,
    },
    {
      path: "/statistics",
      name: "StatisticsView",
      component: StatisticsView,
    },
    {
      path: "/second-auth",
      name: "SecondAuth",
      component: SecondAuthView,
      meta: { requiresAuth: true }
    },
  ]
})

export default router
