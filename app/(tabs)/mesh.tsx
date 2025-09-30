import React from "react";
import { View } from "react-native";
import { ModernWalletProvider } from "../../contexts/ModernWalletContext";
import ModernMeshInterface from "../../components/ModernMeshInterface";

export default function MeshScreen() {
  return (
    <ModernWalletProvider>
      <View style={{ flex: 1 }}>
        <ModernMeshInterface />
      </View>
    </ModernWalletProvider>
  );
}
