import request from '@/utils/request'

// Dataset API
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
