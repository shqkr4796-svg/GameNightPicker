import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import AsyncStorage from '@react-native-async-storage/async-storage';
import LoginScreen from './src/screens/LoginScreen';
import MainHubScreen from './src/screens/MainHubScreen';
import AdventureScreen from './src/screens/AdventureScreen';
import CompendiumScreen from './src/screens/CompendiumScreen';
import SkillsScreen from './src/screens/SkillsScreen';
import DungeonScreen from './src/screens/DungeonScreen';
import ShopScreen from './src/screens/ShopScreen';
import RealEstateScreen from './src/screens/RealEstateScreen';
import JobScreen from './src/screens/JobScreen';
import DailyExpressionsScreen from './src/screens/DailyExpressionsScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import InventoryScreen from './src/screens/InventoryScreen';
import AchievementsScreen from './src/screens/AchievementsScreen';

const Stack = createStackNavigator();

export default function App() {
  const [initialRoute, setInitialRoute] = useState(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = await AsyncStorage.getItem('auth_token');
    setInitialRoute(token ? 'MainHub' : 'Login');
  };

  if (initialRoute === null) {
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName={initialRoute}
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1a1a1a'
          },
          headerTintColor: '#6366f1',
          headerTitleStyle: {
            color: '#fff',
            fontWeight: 'bold'
          }
        }}
      >
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen
          name="MainHub"
          component={MainHubScreen}
          options={{ title: '게임 허브' }}
        />
        <Stack.Screen
          name="Adventure"
          component={AdventureScreen}
          options={{ title: '모험' }}
        />
        <Stack.Screen
          name="Compendium"
          component={CompendiumScreen}
          options={{ title: '도감' }}
        />
        <Stack.Screen
          name="Skills"
          component={SkillsScreen}
          options={{ title: '스킬' }}
        />
        <Stack.Screen
          name="Dungeon"
          component={DungeonScreen}
          options={{ title: '던전' }}
        />
        <Stack.Screen
          name="Shop"
          component={ShopScreen}
          options={{ title: '상점' }}
        />
        <Stack.Screen
          name="RealEstate"
          component={RealEstateScreen}
          options={{ title: '부동산' }}
        />
        <Stack.Screen
          name="Job"
          component={JobScreen}
          options={{ title: '직업' }}
        />
        <Stack.Screen
          name="DailyExpressions"
          component={DailyExpressionsScreen}
          options={{ title: '일일 표현' }}
        />
        <Stack.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{ title: '대시보드' }}
        />
        <Stack.Screen
          name="Inventory"
          component={InventoryScreen}
          options={{ title: '인벤토리' }}
        />
        <Stack.Screen
          name="Achievements"
          component={AchievementsScreen}
          options={{ title: '성취' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
