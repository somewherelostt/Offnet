import algosdk from "algosdk";

export const ALGORAND_CONFIG = {
  // Algorand TestNet configuration
  ALGOD_SERVER: "https://testnet-api.algonode.cloud",
  ALGOD_PORT: "",
  ALGOD_TOKEN: "",

  // Algorand MainNet configuration (for production)
  MAINNET_ALGOD_SERVER: "https://mainnet-api.algonode.cloud",

  // Network configuration
  NETWORK: "TestNet" as "TestNet" | "MainNet",

  // Offnet Token Configuration (will be deployed)
  OFFNET_TOKEN_ID: 0, // Will be set after deployment
  OFFNET_TOKEN_NAME: "Offnet Token",
  OFFNET_TOKEN_SYMBOL: "OFFNET",
  OFFNET_TOKEN_DECIMALS: 6,
  OFFNET_TOKEN_TOTAL_SUPPLY: 1000000, // 1M tokens

  // Application ID for smart contracts (will be set after deployment)
  MESH_RELAY_APP_ID: 0,

  // Transaction configurations
  DEFAULT_FEE: 1000, // 0.001 ALGO
  MIN_BALANCE: 100000, // 0.1 ALGO minimum balance

  // BLE mesh networking
  MESH_PROTOCOL_VERSION: "1.0.0",
  MAX_RELAY_HOPS: 10,
  TRANSACTION_TIMEOUT: 300000, // 5 minutes
};

export const getAlgodClient = () => {
  const server =
    ALGORAND_CONFIG.NETWORK === "MainNet"
      ? ALGORAND_CONFIG.MAINNET_ALGOD_SERVER
      : ALGORAND_CONFIG.ALGOD_SERVER;

  return new algosdk.Algodv2(
    ALGORAND_CONFIG.ALGOD_TOKEN,
    server,
    ALGORAND_CONFIG.ALGOD_PORT
  );
};

export const getIndexerClient = () => {
  const server =
    ALGORAND_CONFIG.NETWORK === "MainNet"
      ? "https://mainnet-idx.algonode.cloud"
      : "https://testnet-idx.algonode.cloud";

  return new algosdk.Indexer("", server, "");
};

// Network info
export const SUPPORTED_NETWORKS = [
  {
    id: "algorand-testnet",
    name: "Algorand TestNet",
    chainId: "testnet-v1.0",
    rpcUrl: ALGORAND_CONFIG.ALGOD_SERVER,
    explorerUrl: "https://testnet.algoexplorer.io",
    currency: {
      name: "Algorand",
      symbol: "ALGO",
      decimals: 6,
    },
  },
  {
    id: "algorand-mainnet",
    name: "Algorand MainNet",
    chainId: "mainnet-v1.0",
    rpcUrl: ALGORAND_CONFIG.MAINNET_ALGOD_SERVER,
    explorerUrl: "https://algoexplorer.io",
    currency: {
      name: "Algorand",
      symbol: "ALGO",
      decimals: 6,
    },
  },
];

export interface AlgorandTransactionPayload {
  type: "ALGORAND_TRANSFER" | "ASSET_TRANSFER" | "APP_CALL";
  sender: string;
  receiver: string;
  amount: number;
  assetId?: number;
  appId?: number;
  appArgs?: Uint8Array[];
  note?: string;
  signature: string;
  txnId: string;
  fee: number;
  firstValid: number;
  lastValid: number;
  genesisHash: string;
  genesisId: string;
}
