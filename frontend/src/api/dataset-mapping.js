import request from '@/utils/request'

// 知识库映射 API

export const listMappings = (params) => {
  return request({
    url: '/dataset-mappings',
    method: 'get',
    params
  })
}

export const getAllMappings = () => {
  return request({
    url: '/dataset-mappings/all',
    method: 'get'
  })
}

export const getMappingByName = (name) => {
  return request({
    url: `/dataset-mappings/by-name/${name}`,
    method: 'get'
  })
}

export const getMappingByTag = (data) => {
  return request({
    url: '/dataset-mappings/by-tag',
    method: 'post',
    data
  })
}

export const getMapping = (id) => {
  return request({
    url: `/dataset-mappings/${id}`,
    method: 'get'
  })
}

export const createMapping = (data) => {
  return request({
    url: '/dataset-mappings',
    method: 'post',
    data
  })
}

export const updateMapping = (id, data) => {
  return request({
    url: `/dataset-mappings/${id}`,
    method: 'put',
    data
  })
}

export const deleteMapping = (id) => {
  return request({
    url: `/dataset-mappings/${id}`,
    method: 'delete'
  })
}

// 文章标签关联 API

export const addArticleTags = (data) => {
  return request({
    url: '/dataset-mappings/article-tags',
    method: 'post',
    data
  })
}

export const getArticleTags = (documentId, params) => {
  return request({
    url: `/dataset-mappings/article-tags/${documentId}`,
    method: 'get',
    params
  })
}

export const getArticlesByTag = (tagId, params) => {
  return request({
    url: `/dataset-mappings/articles-by-tag/${tagId}`,
    method: 'get',
    params
  })
}
