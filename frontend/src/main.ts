import { createApp } from 'vue'
import { ElButton, ElInput, ElOption, ElSelect } from 'element-plus'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/input/style/css'
import 'element-plus/es/components/select/style/css'
import 'element-plus/es/components/option/style/css'
import 'element-plus/es/components/message/style/css'
import './style.css'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(router)
app.use(ElButton).use(ElInput).use(ElSelect).use(ElOption)
app.mount('#app')
