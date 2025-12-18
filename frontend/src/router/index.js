import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/datasets',
    name: 'Datasets',
    component: () => import('@/views/Datasets.vue')
  },
  {
    path: '/datasources',
    name: 'DataSources',
    component: () => import('@/views/DataSources.vue')
  },
  {
    path: '/rss',
    name: 'RSS',
    component: () => import('@/views/RSS.vue')
  },
  {
    path: '/tags',
    name: 'Tags',
    component: () => import('@/views/Tags.vue')
  },
  {
    path: '/webhook',
    name: 'Webhook',
    component: () => import('@/views/Webhook.vue')
  },
  // 兼容旧路由，重定向到知识库
  {
    path: '/ragflow',
    redirect: '/datasets'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
