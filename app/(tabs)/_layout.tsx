import React from "react";
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { OffnetColors } from "../../components/OffnetUI";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarStyle: {
          backgroundColor: OffnetColors.surface,
          borderTopColor: OffnetColors.border,
          borderTopWidth: 1,
        },
        tabBarActiveTintColor: OffnetColors.primary,
        tabBarInactiveTintColor: OffnetColors.muted,
        headerStyle: {
          backgroundColor: OffnetColors.background,
          borderBottomColor: OffnetColors.border,
          borderBottomWidth: 1,
        },
        headerTintColor: OffnetColors.onSurface,
        headerTitleStyle: {
          fontWeight: "600",
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Home",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="wallet"
        options={{
          title: "Wallet",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="wallet-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="mesh"
        options={{
          title: "Mesh",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="radio-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="transactions"
        options={{
          title: "History",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="time-outline" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
