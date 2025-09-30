import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { PeraWalletConnect } from "@perawallet/connect";
import algosdk from "algosdk";
import { getAlgodClient, ALGORAND_CONFIG } from "../constants/algorand";

// Pera Wallet instance
const peraWallet = new PeraWalletConnect({
  shouldShowSignTxnToast: true,
  chainId: ALGORAND_CONFIG.NETWORK === "MainNet" ? 416001 : 416002,
});

interface WalletContextType {
  // Connection state
  isConnected: boolean;
  accountAddress: string | null;
  balance: number;
  isLoading: boolean;
  error: string | null;

  // Wallet actions
  connectWallet: () => Promise<void>;
  disconnectWallet: () => Promise<void>;
  refreshBalance: () => Promise<void>;

  // Utility methods
  formatBalance: (balance: number) => string;
  isValidAddress: (address: string) => boolean;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

interface WalletProviderProps {
  children: ReactNode;
}

export const WalletProvider: React.FC<WalletProviderProps> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [accountAddress, setAccountAddress] = useState<string | null>(null);
  const [balance, setBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const algodClient = getAlgodClient();

  // Check for existing connection on mount
  useEffect(() => {
    peraWallet
      .reconnectSession()
      .then((accounts) => {
        if (accounts.length > 0) {
          setAccountAddress(accounts[0]);
          setIsConnected(true);
          refreshBalance();
        }
      })
      .catch(console.error);

    // Listen for disconnect events
    peraWallet.connector?.on("disconnect", () => {
      setIsConnected(false);
      setAccountAddress(null);
      setBalance(0);
    });
  }, []);

  const connectWallet = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const newAccounts = await peraWallet.connect();

      if (newAccounts.length > 0) {
        setAccountAddress(newAccounts[0]);
        setIsConnected(true);
        await refreshBalance();
      }
    } catch (err: any) {
      console.error("Wallet connection failed:", err);
      setError(err.message || "Failed to connect wallet");
    } finally {
      setIsLoading(false);
    }
  };

  const disconnectWallet = async () => {
    try {
      await peraWallet.disconnect();
      setIsConnected(false);
      setAccountAddress(null);
      setBalance(0);
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
    isLoading,
    error,

    // Wallet actions
    connectWallet,
    disconnectWallet,
    refreshBalance,

    // Utility methods
    formatBalance,
    isValidAddress,
  };

  return (
    <WalletContext.Provider value={contextValue}>
      {children}
    </WalletContext.Provider>
  );
};

// Hook to use the wallet context
export const useWallet = (): WalletContextType => {
  const context = useContext(WalletContext);
  if (context === undefined) {
    throw new Error("useWallet must be used within a WalletProvider");
  }
  return context;
};
