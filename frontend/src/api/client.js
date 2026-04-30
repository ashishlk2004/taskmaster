import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
});

export const taskApi = {
  list: (params) => api.get('/tasks', { params }).then(r => r.data),
  get: (id) => api.get(`/tasks/${id}`).then(r => r.data),
  create: (data) => api.post('/tasks', data).then(r => r.data),
  update: (id, data) => api.put(`/tasks/${id}`, data).then(r => r.data),
  delete: (id) => api.delete(`/tasks/${id}`),
  complete: (id) => api.post(`/tasks/${id}/complete`).then(r => r.data),
  predict: (id) => api.get(`/tasks/${id}/predict`).then(r => r.data),
};

export const categoryApi = {
  list: () => api.get('/categories').then(r => r.data),
  create: (data) => api.post('/categories', data).then(r => r.data),
  update: (id, data) => api.put(`/categories/${id}`, data).then(r => r.data),
  delete: (id) => api.delete(`/categories/${id}`),
};

export const statsApi = {
  get: () => api.get('/stats').then(r => r.data),
};

export const badgeApi = {
  list: () => api.get('/badges').then(r => r.data),
};

export const mlApi = {
  train: () => api.post('/ml/train').then(r => r.data),
  status: () => api.get('/ml/status').then(r => r.data),
};
