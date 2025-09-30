import React from "react";
import { Stack } from "expo-router";
import { WalletProvider } from "../contexts/WalletContext";
import { OffnetColors } from "../components/OffnetUI";

export default function RootLayout() {
  return (
    <WalletProvider>
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: OffnetColors.background,
          },
          headerTintColor: OffnetColors.onSurface,
          headerTitleStyle: {
            fontWeight: "600",
          },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      </Stack>
    </WalletProvider>
  );
}
