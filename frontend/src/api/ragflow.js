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

// 文档解析 API

export const runParsing = (data) => {
  return request({
    url: '/ragflow/documents/parse',
    method: 'post',
    data
  })
}

export const stopParsing = (data) => {
  return request({
    url: '/ragflow/documents/parse/stop',
    method: 'post',
    data
  })
}

export const getParsingStatus = (params) => {
  return request({
    url: '/ragflow/documents/parse/status',
    method: 'get',
    params
  })
}

// 批量操作 API

export const batchDeleteDocuments = (data) => {
  return request({
    url: '/ragflow/documents/batch-delete',
    method: 'post',
    data
  })
}

export const transferDocument = (data) => {
  return request({
    url: '/ragflow/documents/transfer',
    method: 'post',
    data
  })
}

export const batchTransferDocuments = (data) => {
  return request({
    url: '/ragflow/documents/batch-transfer',
    method: 'post',
    data
  })
}

// 文档元数据 API

export const updateDocumentMetadata = (data) => {
  return request({
    url: '/ragflow/documents/metadata',
    method: 'put',
    data
  })
}

export const checkUrlExists = (data) => {
  return request({
    url: '/ragflow/check-url',
    method: 'post',
    data
  })
}

// Chunk 分块 API

export const listChunks = (params) => {
  return request({
    url: '/ragflow/chunks',
    method: 'get',
    params
  })
}

export const deleteChunks = (data) => {
  return request({
    url: '/ragflow/chunks',
    method: 'delete',
    data
  })
}
