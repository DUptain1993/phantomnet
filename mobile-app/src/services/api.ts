import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Alert } from 'react-native';

// API Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:8443'  // Android emulator localhost
  : 'https://your-production-domain.com'; // Production URL

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && originalRequest) {
      try {
        // Try to refresh token
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          if (response.data.token) {
            await SecureStore.setItemAsync('auth_token', response.data.token);
            originalRequest.headers.Authorization = `Bearer ${response.data.token}`;
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Clear stored tokens and redirect to login
        await SecureStore.deleteItemAsync('auth_token');
        await SecureStore.deleteItemAsync('refresh_token');
        // You might want to emit an event here to trigger navigation to login
      }
    }

    // Handle network errors
    if (!error.response) {
      Alert.alert(
        'Network Error',
        'Please check your internet connection and try again.',
        [{ text: 'OK' }]
      );
    }

    // Handle server errors
    if (error.response?.status >= 500) {
      Alert.alert(
        'Server Error',
        'Something went wrong on our end. Please try again later.',
        [{ text: 'OK' }]
      );
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Authentication
  auth: {
    login: '/admin/login',
    logout: '/admin/logout',
    refresh: '/auth/refresh',
    me: '/auth/me',
    profile: '/auth/profile',
  },
  
  // Bots
  bots: {
    list: '/api/bots',
    create: '/api/bots',
    get: (id: string) => `/api/bots/${id}`,
    update: (id: string) => `/api/bots/${id}`,
    delete: (id: string) => `/api/bots/${id}`,
    status: (id: string) => `/api/bots/${id}/status`,
    commands: (id: string) => `/api/bots/${id}/commands`,
  },
  
  // Targets
  targets: {
    list: '/api/targets',
    create: '/api/targets',
    get: (id: string) => `/api/targets/${id}`,
    update: (id: string) => `/api/targets/${id}`,
    delete: (id: string) => `/api/targets/${id}`,
    scan: (id: string) => `/api/targets/${id}/scan`,
    exploit: (id: string) => `/api/targets/${id}/exploit`,
  },
  
  // Commands
  commands: {
    list: '/api/commands',
    create: '/api/commands',
    get: (id: string) => `/api/commands/${id}`,
    update: (id: string) => `/api/commands/${id}`,
    delete: (id: string) => `/api/commands/${id}`,
    execute: (id: string) => `/api/commands/${id}/execute`,
    results: (id: string) => `/api/commands/${id}/results`,
  },
  
  // Tasks
  tasks: {
    list: '/api/tasks',
    create: '/api/tasks',
    get: (id: string) => `/api/tasks/${id}`,
    update: (id: string) => `/api/tasks/${id}`,
    delete: (id: string) => `/api/tasks/${id}`,
    start: (id: string) => `/api/tasks/${id}/start`,
    stop: (id: string) => `/api/tasks/${id}/stop`,
    status: (id: string) => `/api/tasks/${id}/status`,
  },
  
  // Payloads
  payloads: {
    list: '/api/payloads',
    create: '/api/payloads',
    get: (id: string) => `/api/payloads/${id}`,
    update: (id: string) => `/api/payloads/${id}`,
    delete: (id: string) => `/api/payloads/${id}`,
    generate: (id: string) => `/api/payloads/${id}/generate`,
    download: (id: string) => `/api/payloads/${id}/download`,
  },
  
  // Dashboard
  dashboard: {
    stats: '/api/dashboard/stats',
    recent: '/api/dashboard/recent',
    alerts: '/api/dashboard/alerts',
    logs: '/api/dashboard/logs',
  },
  
  // System
  system: {
    health: '/health',
    status: '/api/system/status',
    logs: '/api/system/logs',
    config: '/api/system/config',
    update: '/api/system/update',
  },
};

// API service functions
export const apiService = {
  // Authentication
  login: async (username: string, password: string) => {
    const response = await api.post(endpoints.auth.login, { username, password });
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post(endpoints.auth.logout);
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get(endpoints.auth.me);
    return response.data;
  },
  
  updateProfile: async (userData: any) => {
    const response = await api.put(endpoints.auth.profile, userData);
    return response.data;
  },
  
  // Bots
  getBots: async (params?: any) => {
    const response = await api.get(endpoints.bots.list, { params });
    return response.data;
  },
  
  createBot: async (botData: any) => {
    const response = await api.post(endpoints.bots.create, botData);
    return response.data;
  },
  
  getBot: async (id: string) => {
    const response = await api.get(endpoints.bots.get(id));
    return response.data;
  },
  
  updateBot: async (id: string, botData: any) => {
    const response = await api.put(endpoints.bots.update(id), botData);
    return response.data;
  },
  
  deleteBot: async (id: string) => {
    const response = await api.delete(endpoints.bots.delete(id));
    return response.data;
  },
  
  // Targets
  getTargets: async (params?: any) => {
    const response = await api.get(endpoints.targets.list, { params });
    return response.data;
  },
  
  createTarget: async (targetData: any) => {
    const response = await api.post(endpoints.targets.create, targetData);
    return response.data;
  },
  
  getTarget: async (id: string) => {
    const response = await api.get(endpoints.targets.get(id));
    return response.data;
  },
  
  updateTarget: async (id: string, targetData: any) => {
    const response = await api.put(endpoints.targets.update(id), targetData);
    return response.data;
  },
  
  deleteTarget: async (id: string) => {
    const response = await api.delete(endpoints.targets.delete(id));
    return response.data;
  },
  
  // Commands
  getCommands: async (params?: any) => {
    const response = await api.get(endpoints.commands.list, { params });
    return response.data;
  },
  
  createCommand: async (commandData: any) => {
    const response = await api.post(endpoints.commands.create, commandData);
    return response.data;
  },
  
  getCommand: async (id: string) => {
    const response = await api.get(endpoints.commands.get(id));
    return response.data;
  },
  
  updateCommand: async (id: string, commandData: any) => {
    const response = await api.put(endpoints.commands.update(id), commandData);
    return response.data;
  },
  
  deleteCommand: async (id: string) => {
    const response = await api.delete(endpoints.commands.delete(id));
    return response.data;
  },
  
  executeCommand: async (id: string, params?: any) => {
    const response = await api.post(endpoints.commands.execute(id), params);
    return response.data;
  },
  
  // Tasks
  getTasks: async (params?: any) => {
    const response = await api.get(endpoints.tasks.list, { params });
    return response.data;
  },
  
  createTask: async (taskData: any) => {
    const response = await api.post(endpoints.tasks.create, taskData);
    return response.data;
  },
  
  getTask: async (id: string) => {
    const response = await api.get(endpoints.tasks.get(id));
    return response.data;
  },
  
  updateTask: async (id: string, taskData: any) => {
    const response = await api.put(endpoints.tasks.update(id), taskData);
    return response.data;
  },
  
  deleteTask: async (id: string) => {
    const response = await api.delete(endpoints.tasks.delete(id));
    return response.data;
  },
  
  startTask: async (id: string) => {
    const response = await api.post(endpoints.tasks.start(id));
    return response.data;
  },
  
  stopTask: async (id: string) => {
    const response = await api.post(endpoints.tasks.stop(id));
    return response.data;
  },
  
  // Dashboard
  getDashboardStats: async () => {
    const response = await api.get(endpoints.dashboard.stats);
    return response.data;
  },
  
  getRecentActivity: async () => {
    const response = await api.get(endpoints.dashboard.recent);
    return response.data;
  },
  
  getAlerts: async () => {
    const response = await api.get(endpoints.dashboard.alerts);
    return response.data;
  },
  
  // System
  getSystemHealth: async () => {
    const response = await api.get(endpoints.system.health);
    return response.data;
  },
  
  getSystemStatus: async () => {
    const response = await api.get(endpoints.system.status);
    return response.data;
  },
};

export default api;
