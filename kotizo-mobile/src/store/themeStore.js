import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { COLORS_DARK, COLORS_LIGHT } from '../constants/colors';

const useThemeStore = create((set) => ({
  isDark: true,
  colors: COLORS_DARK,

  init: async () => {
    try {
      const saved = await AsyncStorage.getItem('theme');
      const isDark = saved !== 'light';
      set({ isDark, colors: isDark ? COLORS_DARK : COLORS_LIGHT });
    } catch {}
  },

  toggle: async () => {
    set((state) => {
      const isDark = !state.isDark;
      AsyncStorage.setItem('theme', isDark ? 'dark' : 'light');
      return { isDark, colors: isDark ? COLORS_DARK : COLORS_LIGHT };
    });
  },
}));

export default useThemeStore;
