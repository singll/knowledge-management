import request from '@/utils/request'

export const listWebhookConfigs = (params) => {
  return request({
    url: '/webhooks/configs',
    method: 'get',
    params
  })
}

export const getWebhookConfig = (id) => {
  return request({
    url: `/webhooks/configs/${id}`,
    method: 'get'
  })
}

export const createWebhookConfig = (data) => {
  return request({
    url: '/webhooks/configs',
    method: 'post',
    data
  })
}

export const updateWebhookConfig = (id, data) => {
  return request({
    url: `/webhooks/configs/${id}`,
    method: 'put',
    data
  })
}

export const deleteWebhookConfig = (id) => {
  return request({
    url: `/webhooks/configs/${id}`,
    method: 'delete'
  })
}

export const triggerWebhook = (data) => {
  return request({
    url: '/webhooks/trigger',
    method: 'post',
    data
  })
}

export const listWebhookHistory = (params) => {
  return request({
    url: '/webhooks/history',
    method: 'get',
    params
  })
}

export const getWebhookHistory = (id) => {
  return request({
    url: `/webhooks/history/${id}`,
    method: 'get'
  })
}
