import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import useThemeStore from '../store/themeStore';

import DashboardScreen from '../screens/app/DashboardScreen';
import CotisationsScreen from '../screens/app/cotisations/CotisationsScreen';
import QuickPayScreen from '../screens/app/quickpay/QuickPayScreen';
import ProfilScreen from '../screens/app/profil/ProfilScreen';

const Tab = createBottomTabNavigator();

const TABS = [
  { name: 'Accueil', component: DashboardScreen, icon: 'home' },
  { name: 'Cotisations', component: CotisationsScreen, icon: 'wallet' },
  { name: 'QuickPay', component: QuickPayScreen, icon: 'flash' },
  { name: 'Profil', component: ProfilScreen, icon: 'person' },
];

export default function MainNavigator() {
  const { colors } = useThemeStore();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colors.tabBar,
          borderTopColor: colors.border,
          height: 70,
          paddingBottom: 10,
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textTertiary,
        tabBarIcon: ({ focused, color, size }) => {
          const tab = TABS.find(t => t.name === route.name);
          const iconName = focused ? tab.icon : `${tab.icon}-outline`;
          return <Ionicons name={iconName} size={24} color={color} />;
        },
      })}
    >
      {TABS.map(tab => (
        <Tab.Screen key={tab.name} name={tab.name} component={tab.component} />
      ))}
    </Tab.Navigator>
  );
}
