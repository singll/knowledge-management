import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/ragflow',
    name: 'RagFlow',
    component: () => import('@/views/RagFlow.vue')
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
