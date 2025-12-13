import request from '@/utils/request'

export const listDataSources = (params) => {
  return request({
    url: '/datasources',
    method: 'get',
    params
  })
}

export const getDataSource = (id) => {
  return request({
    url: `/datasources/${id}`,
    method: 'get'
  })
}

export const createDataSource = (data) => {
  return request({
    url: '/datasources',
    method: 'post',
    data
  })
}

export const updateDataSource = (id, data) => {
  return request({
    url: `/datasources/${id}`,
    method: 'put',
    data
  })
}

export const deleteDataSource = (id) => {
  return request({
    url: `/datasources/${id}`,
    method: 'delete'
  })
}
