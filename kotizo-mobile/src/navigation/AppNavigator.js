import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import useAuthStore from '../store/authStore';
import MainNavigator from './MainNavigator';

import SplashScreen from '../screens/onboarding/SplashScreen';
import TutorialScreen from '../screens/onboarding/TutorialScreen';
import CGUScreen from '../screens/onboarding/CGUScreen';
import ConnexionScreen from '../screens/auth/ConnexionScreen';
import InscriptionScreen from '../screens/auth/InscriptionScreen';
import VerificationScreen from '../screens/auth/VerificationScreen';
import MotDePasseOublieScreen from '../screens/auth/MotDePasseOublieScreen';

const Stack = createStackNavigator();

export default function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuthStore();

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false, gestureEnabled: false }}>
        {isLoading ? (
          <Stack.Screen name="Splash" component={SplashScreen} />
        ) : !isAuthenticated ? (
          <>
            <Stack.Screen name="Tutorial" component={TutorialScreen} />
            <Stack.Screen name="CGU" component={CGUScreen} />
            <Stack.Screen name="Connexion" component={ConnexionScreen} />
            <Stack.Screen name="Inscription" component={InscriptionScreen} />
            <Stack.Screen name="Verification" component={VerificationScreen} />
            <Stack.Screen name="MotDePasseOublie" component={MotDePasseOublieScreen} />
          </>
        ) : (
          <Stack.Screen name="Main" component={MainNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
