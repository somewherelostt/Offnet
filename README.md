# Offnet - Algorand Mesh Network

Offline Web3 payment system enabling peer-to-peer transactions through Bluetooth mesh networking without internet connectivity.

## Features

- Offline Algorand transactions via Bluetooth mesh
- Smart contract-based relay fee system
- React Native mobile application
- Modern AlgoKit development environment

## Installation

### Prerequisites

- Node.js 16+
- Python 3.11+
- AlgoKit CLI
- Docker (for LocalNet)

### Setup

```bash
# Install dependencies
npm install
pip install -r smart_contracts/requirements.txt

# Install AlgoKit
pip install algokit

# Start Algorand LocalNet
algokit localnet start
```

## Smart Contract

### Compilation

```bash
cd smart_contracts
python test_compilation.py
```

### Deployment

```bash
# Deploy to LocalNet
python localnet_test.py

# Deploy to TestNet
python deploy_modern.py
```

## Development

### Run Mobile App

```bash
npm start
```

### Test Contract

```bash
cd smart_contracts
python test_contract.py
```

## LocalNet Testing

LocalNet is Algorand's local blockchain for development:

1. **Start LocalNet**: `algokit localnet start`
2. **Deploy Contract**: `python smart_contracts/localnet_test.py`  
3. **Test Functions**: Use React Native app or direct contract calls

LocalNet provides:
- Instant block times
- Pre-funded accounts
- Full Algorand node locally
- Reset on restart

## Contract API

### Core Methods

- `opt_in_relay()` - Join relay network
- `process_mesh_relay(data, destination, hops)` - Process relay transaction
- `withdraw_relay_fees()` - Withdraw earned fees
- `create_token(name, symbol, supply)` - Create OFFNET token

### State

**Global State**
- `mesh_fee` - Relay fee in microAlgos
- `relay_count` - Active relay nodes
- `token_asset_id` - Created token ID

**Local State**
- `reputation_score` - Node reputation (0-100)
- `relay_balance` - Accumulated fees
- `is_active_relay` - Active status

## Architecture

### Smart Contract
- PyTeal-based Algorand smart contract
- Inner transaction support
- Reputation system
- Fee distribution

### Mobile App
- React Native with Expo
- Pera Wallet integration
- Bluetooth mesh networking
- Offline transaction storage

### Mesh Protocol
- Bluetooth LE for device discovery
- Transaction fragment broadcasting
- Multi-hop routing with TTL
- Economic incentives for relaying

## Configuration

Update `constants/algorand.ts`:

```typescript
export const ALGORAND_CONFIG = {
  NETWORK: "TestNet", // or "MainNet"
  MESH_RELAY_APP_ID: 0, // Set after deployment
  OFFNET_TOKEN_ID: 0,   // Set after token creation
};
```

## Testing

### Contract Tests
```bash
cd smart_contracts
python test_compilation.py  # Test compilation
python localnet_test.py     # Test on LocalNet
```

### Mobile App Tests
```bash
npm test
npm run lint
```

## Contributing

1. Fork repository
2. Create feature branch
3. Test changes locally
4. Submit pull request

## License

MIT License