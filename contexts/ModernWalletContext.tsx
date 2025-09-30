import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { PeraWalletConnect } from "@perawallet/connect";
import algosdk from "algosdk";
import {
  getAlgodClient,
  getIndexerClient,
  ALGORAND_CONFIG,
} from "../constants/algorand";

// Enhanced Pera Wallet instance with error handling
const peraWallet = new PeraWalletConnect({
  shouldShowSignTxnToast: true,
  chainId: ALGORAND_CONFIG.NETWORK === "MainNet" ? 416001 : 416002,
});

interface WalletContextType {
  // Connection state
  isConnected: boolean;
  accountAddress: string | null;
  balance: number;
  assetBalance: number;
  isLoading: boolean;
  error: string | null;

  // Algorand clients
  algodClient: algosdk.Algodv2;
  indexerClient: algosdk.Indexer;

  // Wallet actions
  connectWallet: () => Promise<void>;
  disconnectWallet: () => Promise<void>;
  refreshBalance: () => Promise<void>;
  refreshAssetBalance: () => Promise<void>;

  // Smart contract interactions
  callSmartContract: (
    appId: number,
    method: string,
    args: algosdk.ABIValue[],
    assetReferences?: number[]
  ) => Promise<any>;

  optInToAsset: (assetId: number) => Promise<any>;

  // Modern transaction handling
  sendTransaction: (
    receiver: string,
    amount: number,
    note?: string
  ) => Promise<string>;

  sendAssetTransaction: (
    receiver: string,
    amount: number,
    assetId: number,
    note?: string
  ) => Promise<string>;

  // Utility methods
  formatBalance: (balance: number) => string;
  isValidAddress: (address: string) => boolean;
}

const ModernWalletContext = createContext<WalletContextType | undefined>(
  undefined
);

interface WalletProviderProps {
  children: ReactNode;
}

export const ModernWalletProvider: React.FC<WalletProviderProps> = ({
  children,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [accountAddress, setAccountAddress] = useState<string | null>(null);
  const [balance, setBalance] = useState(0);
  const [assetBalance, setAssetBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize Algorand clients
  const algodClient = getAlgodClient();
  const indexerClient = getIndexerClient();

  // Check for existing wallet connection on mount
  useEffect(() => {
    const checkExistingConnection = async () => {
      try {
        const accounts = peraWallet.connector?.accounts;
        if (accounts && accounts.length > 0) {
          setAccountAddress(accounts[0]);
          setIsConnected(true);
          await refreshBalance();
          await refreshAssetBalance();
        }
      } catch (err) {
        console.log("No existing wallet connection found");
      }
    };

    checkExistingConnection();

    // Listen for wallet connection events
    peraWallet.connector?.on("connect", (error: Error | null, payload: any) => {
      if (error || !payload?.accounts) {
        console.error("Wallet connection event error:", error);
        return;
      }

      const accounts = payload.accounts;
      if (accounts.length > 0) {
        setAccountAddress(accounts[0]);
        setIsConnected(true);
        refreshBalance();
        refreshAssetBalance();
      }
    });

    peraWallet.connector?.on("disconnect", () => {
      setAccountAddress(null);
      setIsConnected(false);
      setBalance(0);
      setAssetBalance(0);
    });
  }, []);

  const connectWallet = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const newAccounts = await peraWallet.connect();
      if (newAccounts.length > 0) {
        setAccountAddress(newAccounts[0]);
        setIsConnected(true);
        await refreshBalance();
        await refreshAssetBalance();
      }
    } catch (err: any) {
      console.error("Wallet connection failed:", err);
      setError(err.message || "Failed to connect wallet");
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const disconnectWallet = async () => {
    try {
      await peraWallet.disconnect();
      setAccountAddress(null);
      setIsConnected(false);
      setBalance(0);
      setAssetBalance(0);
      setError(null);
    } catch (err: any) {
      console.error("Wallet disconnection failed:", err);
      setError(err.message || "Failed to disconnect wallet");
    }
  };

  const refreshBalance = async () => {
    if (!accountAddress) return;

    try {
      const accountInfo = await algodClient
        .accountInformation(accountAddress)
        .do();

      setBalance(Number(accountInfo.amount));
    } catch (err: any) {
      console.error("Failed to fetch balance:", err);
      setError("Failed to fetch balance");
    }
  };

  const refreshAssetBalance = async () => {
    if (!accountAddress || !ALGORAND_CONFIG.OFFNET_TOKEN_ID) return;

    try {
      const accountInfo = await algodClient
        .accountInformation(accountAddress)
        .do();

      const assetHolding = accountInfo.assets?.find(
        (asset: any) => asset["asset-id"] === ALGORAND_CONFIG.OFFNET_TOKEN_ID
      );

      setAssetBalance(Number(assetHolding?.amount || 0));
    } catch (err: any) {
      console.error("Failed to fetch asset balance:", err);
      // Don't set error for asset balance as token might not be created yet
    }
  };

  const callSmartContract = async (
    appId: number,
    method: string,
    args: algosdk.ABIValue[],
    assetReferences?: number[]
  ) => {
    if (!accountAddress) {
      throw new Error("Wallet not connected");
    }

    try {
      setIsLoading(true);

      // Get suggested params
      const suggestedParams = await algodClient.getTransactionParams().do();

      // Create app call transaction
      const txn = algosdk.makeApplicationCallTxnFromObject({
        sender: accountAddress,
        appIndex: appId,
        onComplete: algosdk.OnApplicationComplete.NoOpOC,
        appArgs: args.map((arg) => new Uint8Array(Buffer.from(String(arg)))),
        foreignAssets: assetReferences,
        suggestedParams,
        note: new Uint8Array(Buffer.from(`${method} call`)),
      });

      // Sign transaction with wallet
      const signedTxns = await peraWallet.signTransaction([txn]);

      // Send transaction
      const result = await algodClient.sendRawTransaction(signedTxns).do();

      return result;
    } catch (err: any) {
      console.error("Smart contract call failed:", err);
      throw new Error(err.message || "Smart contract call failed");
    } finally {
      setIsLoading(false);
    }
  };

  const optInToAsset = async (assetId: number) => {
    if (!accountAddress) {
      throw new Error("Wallet not connected");
    }

    try {
      setIsLoading(true);

      const suggestedParams = await algodClient.getTransactionParams().do();

      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        sender: accountAddress,
        receiver: accountAddress,
        assetIndex: assetId,
        amount: 0,
        suggestedParams,
        note: new Uint8Array(Buffer.from("Asset opt-in")),
      });

      const signedTxn = await peraWallet.signTransaction([
        { txn: txn, signers: [accountAddress] },
      ]);

      const result = await algodClient.sendRawTransaction(signedTxn).do();

      await refreshAssetBalance();
      return result;
    } catch (err: any) {
      console.error("Asset opt-in failed:", err);
      throw new Error(err.message || "Asset opt-in failed");
    } finally {
      setIsLoading(false);
    }
  };

  const sendTransaction = async (
    receiver: string,
    amount: number,
    note?: string
  ): Promise<string> => {
    if (!accountAddress) {
      throw new Error("Wallet not connected");
    }

    try {
      setIsLoading(true);

      const suggestedParams = await algodClient.getTransactionParams().do();

      const txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
        sender: accountAddress,
        receiver: receiver,
        amount: amount, // amount in microAlgos
        suggestedParams,
        note: note ? new Uint8Array(Buffer.from(note)) : undefined,
      });

      const signedTxn = await peraWallet.signTransaction([
        { txn: txn, signers: [accountAddress] },
      ]);

      const result = await algodClient.sendRawTransaction(signedTxn).do();

      await refreshBalance();
      return result.txid;
    } catch (err: any) {
      console.error("Transaction failed:", err);
      throw new Error(err.message || "Transaction failed");
    } finally {
      setIsLoading(false);
    }
  };

  const sendAssetTransaction = async (
    receiver: string,
    amount: number,
    assetId: number,
    note?: string
  ): Promise<string> => {
    if (!accountAddress) {
      throw new Error("Wallet not connected");
    }

    try {
      setIsLoading(true);

      const suggestedParams = await algodClient.getTransactionParams().do();

      const txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        sender: accountAddress,
        receiver: receiver,
        assetIndex: assetId,
        amount: amount,
        suggestedParams,
        note: note ? new Uint8Array(Buffer.from(note)) : undefined,
      });

      const signedTxn = await peraWallet.signTransaction([
        { txn: txn, signers: [accountAddress] },
      ]);

      const result = await algodClient.sendRawTransaction(signedTxn).do();

      await refreshAssetBalance();
      return result.txid;
    } catch (err: any) {
      console.error("Asset transaction failed:", err);
      throw new Error(err.message || "Asset transaction failed");
    } finally {
      setIsLoading(false);
    }
  };

  const formatBalance = (balance: number): string => {
    return (balance / 1000000).toFixed(6); // Convert microAlgos to Algos
  };

  const isValidAddress = (address: string): boolean => {
    try {
      return algosdk.isValidAddress(address);
    } catch {
      return false;
    }
  };

  const contextValue: WalletContextType = {
    // Connection state
    isConnected,
    accountAddress,
    balance,
    assetBalance,
    isLoading,
    error,
    algodClient,
    indexerClient,

    // Wallet actions
    connectWallet,
    disconnectWallet,
    refreshBalance,
    refreshAssetBalance,

    // Smart contract interactions
    callSmartContract,
    optInToAsset,

    // Transaction methods
    sendTransaction,
    sendAssetTransaction,

    // Utility methods
    formatBalance,
    isValidAddress,
  };

  return (
    <ModernWalletContext.Provider value={contextValue}>
      {children}
    </ModernWalletContext.Provider>
  );
};

// Hook to use the modern wallet context
export const useModernWallet = (): WalletContextType => {
  const context = useContext(ModernWalletContext);
  if (context === undefined) {
    throw new Error(
      "useModernWallet must be used within a ModernWalletProvider"
    );
  }
  return context;
};
