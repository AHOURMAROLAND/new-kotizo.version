import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../utils/axios';
import { ENDPOINTS } from '../constants/api';

const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  init: async () => {
    try {
      const [token, userData] = await AsyncStorage.multiGet(['access_token', 'user_data']);
      if (token[1] && userData[1]) {
        set({ user: JSON.parse(userData[1]), isAuthenticated: true });
      }
    } catch {}
    set({ isLoading: false });
  },

  login: async (tokens, user) => {
    await AsyncStorage.multiSet([
      ['access_token', tokens.access],
      ['refresh_token', tokens.refresh],
      ['user_data', JSON.stringify(user)],
    ]);
    set({ user, isAuthenticated: true });
  },

  logout: async (refreshToken) => {
    try {
      if (refreshToken) {
        await api.post(ENDPOINTS.auth.deconnexion, { refresh: refreshToken });
      }
    } catch {}
    await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user_data']);
    set({ user: null, isAuthenticated: false });
  },

  updateUser: async (userData) => {
    const updated = { ...get().user, ...userData };
    await AsyncStorage.setItem('user_data', JSON.stringify(updated));
    set({ user: updated });
  },

  refreshProfil: async () => {
    try {
      const res = await api.get(ENDPOINTS.users.moi);
      if (res.data.success) {
        await AsyncStorage.setItem('user_data', JSON.stringify(res.data.user));
        set({ user: res.data.user });
      }
    } catch {}
  },
}));

export default useAuthStore;
