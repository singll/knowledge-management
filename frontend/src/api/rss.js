import request from '@/utils/request'

export const listRSSFeeds = (params) => {
  return request({
    url: '/rss',
    method: 'get',
    params
  })
}

export const getRSSFeed = (id) => {
  return request({
    url: `/rss/${id}`,
    method: 'get'
  })
}

export const createRSSFeed = (data) => {
  return request({
    url: '/rss',
    method: 'post',
    data
  })
}

export const updateRSSFeed = (id, data) => {
  return request({
    url: `/rss/${id}`,
    method: 'put',
    data
  })
}

export const deleteRSSFeed = (id) => {
  return request({
    url: `/rss/${id}`,
    method: 'delete'
  })
}
