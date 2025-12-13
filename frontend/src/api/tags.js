import request from '@/utils/request'

export const listTags = (params) => {
  return request({
    url: '/tags',
    method: 'get',
    params
  })
}

export const getTag = (id) => {
  return request({
    url: `/tags/${id}`,
    method: 'get'
  })
}

export const createTag = (data) => {
  return request({
    url: '/tags',
    method: 'post',
    data
  })
}

export const updateTag = (id, data) => {
  return request({
    url: `/tags/${id}`,
    method: 'put',
    data
  })
}

export const deleteTag = (id) => {
  return request({
    url: `/tags/${id}`,
    method: 'delete'
  })
}
