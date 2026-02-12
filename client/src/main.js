// main.js - должно быть ТОЧНО как в примере
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap/dist/css/bootstrap.css';

import App from './App.vue'
import router from './router'

import axios from 'axios'
import Cookies from 'js-cookie'
axios.defaults.headers.common["X-CSRFToken"] = Cookies.get("csrftoken");

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')



