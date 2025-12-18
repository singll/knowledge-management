import request from '@/utils/request'

// 知识库（Dataset）管理 API

export const listDatasets = (params) => {
  return request({
    url: '/ragflow/datasets',
    method: 'get',
    params
  })
}

export const getDataset = (datasetId) => {
  return request({
    url: `/ragflow/datasets/${datasetId}`,
    method: 'get'
  })
}

export const createDataset = (data) => {
  return request({
    url: '/ragflow/datasets',
    method: 'post',
    data
  })
}

export const updateDataset = (datasetId, data) => {
  return request({
    url: `/ragflow/datasets/${datasetId}`,
    method: 'put',
    data
  })
}

export const deleteDataset = (datasetId) => {
  return request({
    url: `/ragflow/datasets/${datasetId}`,
    method: 'delete'
  })
}

// 文档管理 API

export const uploadString = (data) => {
  return request({
    url: '/ragflow/upload/string',
    method: 'post',
    data
  })
}

export const uploadWithTags = (data) => {
  return request({
    url: '/ragflow/upload/with-tags',
    method: 'post',
    data
  })
}

export const listDocuments = (params) => {
  return request({
    url: '/ragflow/documents',
    method: 'get',
    params
  })
}

export const getDocument = (params) => {
  return request({
    url: '/ragflow/documents/detail',
    method: 'get',
    params
  })
}

export const deleteDocument = (data) => {
  return request({
    url: '/ragflow/documents',
    method: 'delete',
    data
  })
}

export const uploadBatch = (data) => {
  return request({
    url: '/ragflow/upload/batch',
    method: 'post',
    data
  })
}
