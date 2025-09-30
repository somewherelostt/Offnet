import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import {
  OffnetCard,
  OffnetText,
  OffnetButton,
  OffnetColors,
  OffnetSpacing,
} from "../../components/OffnetUI";

export default function MeshScreen() {
  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Mesh Network Status */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Mesh Network Status
          </OffnetText>

          <View style={styles.statusRow}>
            <OffnetText variant="caption" color="muted">
              BLE Status:
            </OffnetText>
            <OffnetText variant="caption" color="warning">
              Scanning...
            </OffnetText>
          </View>

          <View style={styles.statusRow}>
            <OffnetText variant="caption" color="muted">
              Connected Devices:
            </OffnetText>
            <OffnetText variant="caption" color="onSurface">
              0
            </OffnetText>
          </View>

          <View style={styles.statusRow}>
            <OffnetText variant="caption" color="muted">
              Network Range:
            </OffnetText>
            <OffnetText variant="caption" color="onSurface">
              ~100m
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Active Transactions */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Active Transactions
          </OffnetText>

          <View style={styles.emptyState}>
            <OffnetText variant="body" color="muted" style={styles.emptyText}>
              No active mesh transactions
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Transactions will appear here when broadcasting through the mesh
              network
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Mesh Network Info */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            How It Works
          </OffnetText>

          <View style={styles.infoItem}>
            <OffnetText variant="body" color="onSurface">
              1. 📡 Create Transaction
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Sign your Algorand transaction offline
            </OffnetText>
          </View>

          <View style={styles.infoItem}>
            <OffnetText variant="body" color="onSurface">
              2. 🔗 Mesh Broadcast
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Transaction fragments hop through nearby devices
            </OffnetText>
          </View>

          <View style={styles.infoItem}>
            <OffnetText variant="body" color="onSurface">
              3. 🌐 Internet Gateway
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Reaches a device with internet to submit to Algorand
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Controls */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Mesh Controls
          </OffnetText>

          <View style={styles.buttonContainer}>
            <OffnetButton
              title="Start Scanning"
              onPress={() => console.log("Start scanning")}
              variant="primary"
              style={styles.controlButton}
            />

            <OffnetButton
              title="Stop Broadcasting"
              onPress={() => console.log("Stop broadcasting")}
              variant="outline"
              style={styles.controlButton}
            />
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
  statusRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: OffnetSpacing.xs,
  },
  emptyState: {
    alignItems: "center",
    padding: OffnetSpacing.lg,
  },
  emptyText: {
    marginBottom: OffnetSpacing.xs,
    textAlign: "center",
  },
  infoItem: {
    marginBottom: OffnetSpacing.md,
  },
  buttonContainer: {
    gap: OffnetSpacing.sm,
  },
  controlButton: {
    width: "100%",
  },
});
