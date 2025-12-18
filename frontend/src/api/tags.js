import request from '@/utils/request'

export const listTags = (params) => {
  return request({
    url: '/tags',
    method: 'get',
    params
  })
}

export const getAllTags = () => {
  return request({
    url: '/tags/all',
    method: 'get'
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

export const batchGetOrCreateTags = (data) => {
  return request({
    url: '/tags/batch',
    method: 'post',
    data
  })
}

export const matchTags = (data) => {
  return request({
    url: '/tags/match',
    method: 'post',
    data
  })
}

export const getTagsByNames = (data) => {
  return request({
    url: '/tags/by-names',
    method: 'post',
    data
  })
}
