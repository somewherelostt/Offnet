import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import {
  OffnetCard,
  OffnetText,
  OffnetButton,
  OffnetColors,
  OffnetSpacing,
} from "../../components/OffnetUI";
import { useWallet } from "../../contexts/WalletContext";

export default function WalletScreen() {
  const {
    isConnected,
    accountAddress,
    balance,
    formatBalance,
    connectWallet,
    disconnectWallet,
    refreshBalance,
    isLoading,
    error,
  } = useWallet();

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Wallet Connection */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Pera Wallet
          </OffnetText>

          {isConnected ? (
            <View>
              <View style={styles.addressContainer}>
                <OffnetText variant="caption" color="muted">
                  Connected Address:
                </OffnetText>
                <OffnetText
                  variant="body"
                  color="onSurface"
                  style={styles.address}
                >
                  {accountAddress}
                </OffnetText>
              </View>

              <View style={styles.balanceContainer}>
                <OffnetText variant="caption" color="muted">
                  Account Balance:
                </OffnetText>
                <OffnetText variant="h2" color="success">
                  {formatBalance(balance)} ALGO
                </OffnetText>
              </View>

              <View style={styles.buttonRow}>
                <OffnetButton
                  title="Refresh"
                  onPress={refreshBalance}
                  variant="outline"
                  size="small"
                  loading={isLoading}
                  style={styles.halfButton}
                />
                <OffnetButton
                  title="Disconnect"
                  onPress={disconnectWallet}
                  variant="ghost"
                  size="small"
                  style={styles.halfButton}
                />
              </View>
            </View>
          ) : (
            <View style={styles.disconnectedContainer}>
              <OffnetText
                variant="body"
                color="muted"
                style={styles.disconnectedText}
              >
                Connect your Pera wallet to manage your Algorand assets
              </OffnetText>

              <OffnetButton
                title="Connect Pera Wallet"
                onPress={connectWallet}
                variant="primary"
                loading={isLoading}
                style={styles.connectButton}
              />
            </View>
          )}

          {error && (
            <View style={styles.errorContainer}>
              <OffnetText variant="caption" color="error">
                {error}
              </OffnetText>
            </View>
          )}
        </OffnetCard>

        {/* Account Details */}
        {isConnected && (
          <OffnetCard style={styles.card}>
            <OffnetText variant="h3" style={styles.cardTitle}>
              Account Details
            </OffnetText>

            <View style={styles.detailRow}>
              <OffnetText variant="caption" color="muted">
                Network:
              </OffnetText>
              <OffnetText variant="caption" color="accent">
                Algorand TestNet
              </OffnetText>
            </View>

            <View style={styles.detailRow}>
              <OffnetText variant="caption" color="muted">
                Status:
              </OffnetText>
              <OffnetText variant="caption" color="success">
                Connected
              </OffnetText>
            </View>

            <View style={styles.detailRow}>
              <OffnetText variant="caption" color="muted">
                Balance (microAlgos):
              </OffnetText>
              <OffnetText variant="caption" color="onSurface">
                {balance.toLocaleString()}
              </OffnetText>
            </View>
          </OffnetCard>
        )}

        {/* Wallet Features */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Wallet Features
          </OffnetText>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              🔐 Secure Connection
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Your keys never leave your Pera wallet
            </OffnetText>
          </View>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              ⚡ Fast Transactions
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Low fees and quick confirmations on Algorand
            </OffnetText>
          </View>

          <View style={styles.featureItem}>
            <OffnetText variant="body" color="onSurface">
              📱 Mobile Native
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Optimized for mobile transactions
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
  card: {
    marginBottom: OffnetSpacing.md,
  },
  cardTitle: {
    marginBottom: OffnetSpacing.sm,
  },
  addressContainer: {
    marginBottom: OffnetSpacing.md,
  },
  address: {
    marginTop: OffnetSpacing.xs,
    fontFamily: "monospace",
    fontSize: 12,
  },
  balanceContainer: {
    marginBottom: OffnetSpacing.md,
    alignItems: "center",
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  halfButton: {
    flex: 0.48,
  },
  disconnectedContainer: {
    alignItems: "center",
  },
  disconnectedText: {
    textAlign: "center",
    marginBottom: OffnetSpacing.md,
  },
  connectButton: {
    width: "100%",
  },
  errorContainer: {
    marginTop: OffnetSpacing.sm,
    padding: OffnetSpacing.sm,
    backgroundColor: OffnetColors.error + "20",
    borderRadius: 8,
  },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: OffnetSpacing.xs,
  },
  featureItem: {
    marginBottom: OffnetSpacing.sm,
  },
});
