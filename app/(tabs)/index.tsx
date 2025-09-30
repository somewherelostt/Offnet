import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import { StatusBar } from "expo-status-bar";
import {
  OffnetCard,
  OffnetText,
  OffnetButton,
  OffnetColors,
  OffnetSpacing,
} from "../../components/OffnetUI";
import { useWallet } from "../../contexts/WalletContext";

export default function HomeScreen() {
  const { isConnected, accountAddress, balance, formatBalance, connectWallet } =
    useWallet();

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <OffnetText variant="h1" color="onSurface">
            Welcome to Offnet
          </OffnetText>
          <OffnetText variant="caption" color="muted" style={styles.subtitle}>
            Algorand mesh network for offline transactions
          </OffnetText>
        </View>

        {/* Wallet Status Card */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Wallet Status
          </OffnetText>

          {isConnected ? (
            <View>
              <View style={styles.statusRow}>
                <OffnetText variant="caption" color="muted">
                  Address:
                </OffnetText>
                <OffnetText variant="caption" color="onSurface">
                  {accountAddress?.slice(0, 8)}...{accountAddress?.slice(-8)}
                </OffnetText>
              </View>

              <View style={styles.statusRow}>
                <OffnetText variant="caption" color="muted">
                  Balance:
                </OffnetText>
                <OffnetText variant="h3" color="success">
                  {formatBalance(balance)} ALGO
                </OffnetText>
              </View>
            </View>
          ) : (
            <View>
              <OffnetText
                variant="body"
                color="muted"
                style={styles.disconnectedText}
              >
                Connect your Pera wallet to start using Offnet
              </OffnetText>
              <OffnetButton
                title="Connect Wallet"
                onPress={connectWallet}
                variant="primary"
                style={styles.connectButton}
              />
            </View>
          )}
        </OffnetCard>

        {/* Features Overview */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Features
          </OffnetText>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              📡 Mesh Network Transactions
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Send Algorand transactions without internet
            </OffnetText>
          </View>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              📱 Pera Wallet Integration
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Secure wallet connection and transaction signing
            </OffnetText>
          </View>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              🔗 BLE Protocol
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Custom Bluetooth mesh networking protocol
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Network Status */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Network Status
          </OffnetText>

          <View style={styles.statusRow}>
            <OffnetText variant="caption" color="muted">
              Algorand Network:
            </OffnetText>
            <OffnetText variant="caption" color="accent">
              TestNet
            </OffnetText>
          </View>

          <View style={styles.statusRow}>
            <OffnetText variant="caption" color="muted">
              BLE Status:
            </OffnetText>
            <OffnetText variant="caption" color="warning">
              Scanning...
            </OffnetText>
          </View>
        </OffnetCard>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: OffnetColors.background,
  },
  scrollView: {
    flex: 1,
    padding: OffnetSpacing.md,
  },
  header: {
    marginBottom: OffnetSpacing.lg,
    alignItems: "center",
  },
  subtitle: {
    marginTop: OffnetSpacing.xs,
    textAlign: "center",
  },
  card: {
    marginBottom: OffnetSpacing.md,
  },
  cardTitle: {
    marginBottom: OffnetSpacing.sm,
  },
  statusRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: OffnetSpacing.xs,
  },
  disconnectedText: {
    marginBottom: OffnetSpacing.md,
    textAlign: "center",
  },
  connectButton: {
    marginTop: OffnetSpacing.sm,
  },
  featureItem: {
    marginBottom: OffnetSpacing.sm,
  },
});
