import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import AppNavigator from './src/navigation/AppNavigator';
import useAuthStore from './src/store/authStore';
import useThemeStore from './src/store/themeStore';

export default function App() {
  const initAuth = useAuthStore(s => s.init);
  const initTheme = useThemeStore(s => s.init);
  const isDark = useThemeStore(s => s.isDark);

  useEffect(() => {
    initTheme();
    initAuth();
  }, []);

  return (
    <>
      <StatusBar style={isDark ? 'light' : 'dark'} />
      <AppNavigator />
    </>
  );
}
