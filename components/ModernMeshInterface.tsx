import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert,
  ScrollView,
} from "react-native";
import { StyleSheet } from "react-native";
import { useModernWallet } from "../contexts/ModernWalletContext";
import { ALGORAND_CONFIG } from "../constants/algorand";

interface MeshRelayData {
  id: string;
  sender: string;
  receiver: string;
  amount: number;
  timestamp: number;
  hopCount: number;
  status: "pending" | "relayed" | "completed" | "failed";
}

const ModernMeshInterface: React.FC = () => {
  const {
    isConnected,
    accountAddress,
    balance,
    assetBalance,
    isLoading,
    error,
    connectWallet,
    refreshBalance,
    refreshAssetBalance,
    callSmartContract,
    optInToAsset,
    sendAssetTransaction,
    formatBalance,
    isValidAddress,
  } = useModernWallet();

  const [relayRequests, setRelayRequests] = useState<MeshRelayData[]>([]);
  const [isRelayActive, setIsRelayActive] = useState(false);
  const [relayBalance, setRelayBalance] = useState(0);
  const [reputationScore, setReputationScore] = useState(0);

  // Form states
  const [destinationAddress, setDestinationAddress] = useState("");
  const [relayAmount, setRelayAmount] = useState("");
  const [relayData, setRelayData] = useState("");

  useEffect(() => {
    if (isConnected) {
      refreshBalance();
      refreshAssetBalance();
      fetchRelayStatus();
    }
  }, [isConnected]);

  const fetchRelayStatus = async () => {
    if (!accountAddress || !ALGORAND_CONFIG.MESH_RELAY_APP_ID) return;

    try {
      // This would normally query the smart contract for relay status
      // For now, we'll simulate the data
      setReputationScore(75);
      setRelayBalance(5000000); // 5 ALGO in microAlgos
      setIsRelayActive(true);
    } catch (err) {
      console.error("Failed to fetch relay status:", err);
    }
  };

  const handleOptInToAsset = async () => {
    if (!ALGORAND_CONFIG.OFFNET_TOKEN_ID) {
      Alert.alert("Error", "Offnet token not deployed yet");
      return;
    }

    try {
      await optInToAsset(ALGORAND_CONFIG.OFFNET_TOKEN_ID);
      Alert.alert("Success", "Successfully opted into Offnet token!");
      await refreshAssetBalance();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  const handleOptInToRelay = async () => {
    if (!ALGORAND_CONFIG.MESH_RELAY_APP_ID) {
      Alert.alert("Error", "Smart contract not deployed yet");
      return;
    }

    try {
      const result = await callSmartContract(
        ALGORAND_CONFIG.MESH_RELAY_APP_ID,
        "opt_in_relay",
        [],
        ALGORAND_CONFIG.OFFNET_TOKEN_ID
          ? [ALGORAND_CONFIG.OFFNET_TOKEN_ID]
          : undefined
      );

      Alert.alert("Success", "Successfully opted into relay network!");
      await fetchRelayStatus();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  const handleProcessRelayRequest = async () => {
    if (!destinationAddress || !relayData) {
      Alert.alert("Error", "Please fill in all fields");
      return;
    }

    if (!isValidAddress(destinationAddress)) {
      Alert.alert("Error", "Invalid destination address");
      return;
    }

    if (!ALGORAND_CONFIG.MESH_RELAY_APP_ID) {
      Alert.alert("Error", "Smart contract not deployed yet");
      return;
    }

    try {
      const hopCount = 1; // Starting hop count

      const result = await callSmartContract(
        ALGORAND_CONFIG.MESH_RELAY_APP_ID,
        "process_mesh_relay",
        [relayData, destinationAddress, hopCount],
        ALGORAND_CONFIG.OFFNET_TOKEN_ID
          ? [ALGORAND_CONFIG.OFFNET_TOKEN_ID]
          : undefined
      );

      Alert.alert("Success", "Relay request processed successfully!");

      // Add to local relay requests for tracking
      const newRelay: MeshRelayData = {
        id: result.txid || Date.now().toString(),
        sender: accountAddress!,
        receiver: destinationAddress,
        amount: parseInt(relayAmount) || 0,
        timestamp: Date.now(),
        hopCount: hopCount,
        status: "relayed",
      };

      setRelayRequests((prev) => [newRelay, ...prev]);

      // Clear form
      setDestinationAddress("");
      setRelayAmount("");
      setRelayData("");

      await fetchRelayStatus();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  const handleWithdrawFees = async () => {
    if (!ALGORAND_CONFIG.MESH_RELAY_APP_ID) {
      Alert.alert("Error", "Smart contract not deployed yet");
      return;
    }

    try {
      const result = await callSmartContract(
        ALGORAND_CONFIG.MESH_RELAY_APP_ID,
        "withdraw_relay_fees",
        []
      );

      Alert.alert("Success", "Fees withdrawn successfully!");
      await refreshBalance();
      await fetchRelayStatus();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  const handleToggleRelayStatus = async () => {
    if (!ALGORAND_CONFIG.MESH_RELAY_APP_ID) {
      Alert.alert("Error", "Smart contract not deployed yet");
      return;
    }

    try {
      const result = await callSmartContract(
        ALGORAND_CONFIG.MESH_RELAY_APP_ID,
        "update_relay_status",
        [!isRelayActive]
      );

      Alert.alert(
        "Success",
        `Relay ${!isRelayActive ? "activated" : "deactivated"} successfully!`
      );
      setIsRelayActive(!isRelayActive);
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  if (!isConnected) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Offnet Modern Mesh Network</Text>
        <Text style={styles.subtitle}>
          Connect your wallet to participate in the mesh
        </Text>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={connectWallet}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>
            {isLoading ? "Connecting..." : "Connect Pera Wallet"}
          </Text>
        </TouchableOpacity>

        {error && <Text style={styles.errorText}>{error}</Text>}
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Offnet Mesh Network</Text>
      <Text style={styles.subtitle}>Modern AlgoKit Implementation</Text>

      {/* Wallet Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Wallet Status</Text>
        <Text style={styles.addressText}>Address: {accountAddress}</Text>
        <Text style={styles.balanceText}>
          ALGO Balance: {formatBalance(balance)}
        </Text>
        <Text style={styles.balanceText}>
          OFFNET Balance: {formatBalance(assetBalance)}
        </Text>
      </View>

      {/* Relay Node Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Relay Node Status</Text>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Active:</Text>
          <Text
            style={[
              styles.statusValue,
              { color: isRelayActive ? "#4CAF50" : "#F44336" },
            ]}
          >
            {isRelayActive ? "YES" : "NO"}
          </Text>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Reputation:</Text>
          <Text style={styles.statusValue}>{reputationScore}/100</Text>
        </View>
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Earned Fees:</Text>
          <Text style={styles.statusValue}>
            {formatBalance(relayBalance)} ALGO
          </Text>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>

        {assetBalance === 0 && (
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={handleOptInToAsset}
            disabled={isLoading}
          >
            <Text style={styles.buttonText}>Opt-in to OFFNET Token</Text>
          </TouchableOpacity>
        )}

        {!isRelayActive && (
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={handleOptInToRelay}
            disabled={isLoading}
          >
            <Text style={styles.buttonText}>Join Relay Network</Text>
          </TouchableOpacity>
        )}

        {isRelayActive && (
          <>
            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={handleToggleRelayStatus}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>
                {isRelayActive ? "Deactivate" : "Activate"} Relay
              </Text>
            </TouchableOpacity>

            {relayBalance > 0 && (
              <TouchableOpacity
                style={styles.primaryButton}
                onPress={handleWithdrawFees}
                disabled={isLoading}
              >
                <Text style={styles.buttonText}>Withdraw Fees</Text>
              </TouchableOpacity>
            )}
          </>
        )}
      </View>

      {/* Mesh Relay Interface */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Process Mesh Relay</Text>

        <TextInput
          style={styles.input}
          placeholder="Destination Address"
          value={destinationAddress}
          onChangeText={setDestinationAddress}
          placeholderTextColor="#999"
        />

        <TextInput
          style={styles.input}
          placeholder="Relay Data"
          value={relayData}
          onChangeText={setRelayData}
          placeholderTextColor="#999"
          maxLength={1000}
        />

        <TextInput
          style={styles.input}
          placeholder="Amount (optional)"
          value={relayAmount}
          onChangeText={setRelayAmount}
          keyboardType="numeric"
          placeholderTextColor="#999"
        />

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={handleProcessRelayRequest}
          disabled={isLoading || !isRelayActive}
        >
          <Text style={styles.buttonText}>Process Relay</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Relay Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Relay Activity</Text>
        {relayRequests.length === 0 ? (
          <Text style={styles.emptyText}>No relay activity yet</Text>
        ) : (
          relayRequests.slice(0, 5).map((relay) => (
            <View key={relay.id} style={styles.relayItem}>
              <Text style={styles.relayId}>ID: {relay.id.slice(0, 8)}...</Text>
              <Text style={styles.relayDetail}>
                To: {relay.receiver.slice(0, 8)}...{relay.receiver.slice(-8)}
              </Text>
              <Text style={styles.relayDetail}>Hops: {relay.hopCount}</Text>
              <Text
                style={[
                  styles.relayStatus,
                  { color: getStatusColor(relay.status) },
                ]}
              >
                {relay.status.toUpperCase()}
              </Text>
            </View>
          ))
        )}
      </View>

      {error && <Text style={styles.errorText}>{error}</Text>}
      {isLoading && <Text style={styles.loadingText}>Processing...</Text>}
    </ScrollView>
  );
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "#4CAF50";
    case "relayed":
      return "#FF9800";
    case "pending":
      return "#2196F3";
    case "failed":
      return "#F44336";
    default:
      return "#666";
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f5f5f5",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 8,
    color: "#333",
  },
  subtitle: {
    fontSize: 16,
    textAlign: "center",
    marginBottom: 24,
    color: "#666",
  },
  section: {
    backgroundColor: "#fff",
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 12,
    color: "#333",
  },
  addressText: {
    fontSize: 12,
    color: "#666",
    marginBottom: 8,
    fontFamily: "monospace",
  },
  balanceText: {
    fontSize: 14,
    color: "#333",
    marginBottom: 4,
  },
  statusRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: "#666",
  },
  statusValue: {
    fontSize: 14,
    fontWeight: "bold",
    color: "#333",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 16,
    backgroundColor: "#fff",
    color: "#333",
  },
  primaryButton: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  secondaryButton: {
    backgroundColor: "#6C757D",
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  buttonText: {
    color: "#fff",
    textAlign: "center",
    fontSize: 16,
    fontWeight: "bold",
  },
  relayItem: {
    backgroundColor: "#f8f9fa",
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  relayId: {
    fontSize: 12,
    fontFamily: "monospace",
    color: "#666",
  },
  relayDetail: {
    fontSize: 12,
    color: "#333",
    marginTop: 2,
  },
  relayStatus: {
    fontSize: 12,
    fontWeight: "bold",
    marginTop: 4,
  },
  emptyText: {
    textAlign: "center",
    color: "#999",
    fontStyle: "italic",
    padding: 20,
  },
  errorText: {
    color: "#F44336",
    textAlign: "center",
    marginTop: 16,
    padding: 12,
    backgroundColor: "#FFEBEE",
    borderRadius: 8,
  },
  loadingText: {
    color: "#007AFF",
    textAlign: "center",
    marginTop: 16,
    fontStyle: "italic",
  },
});

export default ModernMeshInterface;
