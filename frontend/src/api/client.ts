import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tpvs_access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tpvs_access');
      localStorage.removeItem('tpvs_refresh');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login/', { username, password }),
  me: () => api.get('/auth/me/'),
};

export const analyticsApi = {
  executive: () => api.get('/analytics/dashboard/executive/'),
  transactions: (days = 30) => api.get(`/analytics/transactions/summary/?days=${days}`),
  transactionList: (days = 30) => api.get(`/analytics/transactions/?days=${days}`),
  agents: (months = 3) => api.get(`/analytics/agents/performance/?months=${months}`),
  missions: () => api.get('/analytics/missions/summary/'),
  missionList: () => api.get('/analytics/missions/'),
  stock: () => api.get('/analytics/stock/'),
  machines: () => api.get('/analytics/machines/'),
  motos: () => api.get('/analytics/motos/'),
  anomalies: () => api.get('/anomalies/'),
};

export const reportsApi = {
  list: () => api.get('/rapports/'),
  generate: (type_rapport: string) => api.post('/rapports/generate/', { type_rapport }),
  export: (id: string) => api.get(`/rapports/export/${id}/`, { responseType: 'blob' }),
};

export default api;
