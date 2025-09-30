import React from "react";
import { View, ScrollView, StyleSheet } from "react-native";
import {
  OffnetCard,
  OffnetText,
  OffnetColors,
  OffnetSpacing,
} from "../../components/OffnetUI";

export default function TransactionsScreen() {
  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        showsVerticalScrollIndicator={false}
      >
        {/* Transaction History */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Transaction History
          </OffnetText>

          <View style={styles.emptyState}>
            <OffnetText variant="body" color="muted" style={styles.emptyText}>
              No transactions yet
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Your transaction history will appear here
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Pending Transactions */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Pending Transactions
          </OffnetText>

          <View style={styles.emptyState}>
            <OffnetText variant="body" color="muted" style={styles.emptyText}>
              No pending transactions
            </OffnetText>
            <OffnetText variant="caption" color="muted">
              Transactions waiting for mesh network confirmation
            </OffnetText>
          </View>
        </OffnetCard>

        {/* Transaction Stats */}
        <OffnetCard style={styles.card}>
          <OffnetText variant="h3" style={styles.cardTitle}>
            Statistics
          </OffnetText>

          <View style={styles.statRow}>
            <OffnetText variant="caption" color="muted">
              Total Transactions:
            </OffnetText>
            <OffnetText variant="caption" color="onSurface">
              0
            </OffnetText>
          </View>

          <View style={styles.statRow}>
            <OffnetText variant="caption" color="muted">
              Successful:
            </OffnetText>
            <OffnetText variant="caption" color="success">
              0
            </OffnetText>
          </View>

          <View style={styles.statRow}>
            <OffnetText variant="caption" color="muted">
              Failed:
            </OffnetText>
            <OffnetText variant="caption" color="error">
              0
            </OffnetText>
          </View>

          <View style={styles.statRow}>
            <OffnetText variant="caption" color="muted">
              Via Mesh Network:
            </OffnetText>
            <OffnetText variant="caption" color="accent">
              0
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
  emptyState: {
    alignItems: "center",
    padding: OffnetSpacing.lg,
  },
  emptyText: {
    marginBottom: OffnetSpacing.xs,
    textAlign: "center",
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: OffnetSpacing.xs,
  },
});
