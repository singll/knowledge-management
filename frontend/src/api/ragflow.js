import request from '@/utils/request'

export const uploadString = (data) => {
  return request({
    url: '/ragflow/upload/string',
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
