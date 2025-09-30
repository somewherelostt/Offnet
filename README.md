# Offnet

Offnet is an open-source offline Web3 payment system that enables peer-to-peer digital transactions through Bluetooth mesh networking without requiring internet connectivity.

## Overview

Offnet creates a decentralized payment network where transactions propagate across devices using Bluetooth Low Energy (BLE) mesh networking. The system maintains transaction integrity through local ledgers and cryptographic validation, preventing double-spending while operating completely offline.

## Core Features

### Offline Transaction Processing
- Bluetooth mesh network for transaction propagation
- Local ledger maintenance on each device
- Cryptographic transaction validation
- Double-spending prevention without centralized authority

### Decentralized Identity
- Self-sovereign identity management
- Cryptographic key pairs for secure authentication
- Identity verification through mesh network consensus
- Privacy-preserving transaction signatures

### Smart Vouchers
- Conditional payment contracts
- Time-locked transactions
- Multi-signature requirements
- Programmable spending conditions

### Incentive System
- Node rewards for transaction relaying
- Mesh network participation incentives
- Automatic fee distribution
- Network health metrics and rewards

## Technical Architecture

### Network Layer
- Bluetooth Low Energy (BLE) for device communication
- Custom mesh protocol for message routing
- Packet fragmentation for large transaction data
- Automatic network topology discovery

### Transaction Layer
- Algorand-based transaction format
- Local transaction pool management
- Conflict resolution algorithms
- Batch transaction processing

### Consensus Layer
- Proof-of-relay consensus mechanism
- Local ledger synchronization
- Fork resolution protocols
- Network partition handling

### Application Layer
- React Native mobile application
- Pera Wallet integration
- Transaction history management
- Network status monitoring

## Getting Started

### Prerequisites
- Node.js 18+
- React Native development environment
- Android Studio (for Android builds)
- Python 3.8+ (for smart contract deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/somewherelostt/offnet.git
cd offnet
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm start
```

### Smart Contract Deployment

1. Install Python dependencies:
```bash
cd contracts
pip install -r requirements.txt
```

2. Deploy to Algorand TestNet:
```bash
export ALGORAND_PRIVATE_KEY="your-private-key"
python deploy.py
```

## Project Structure

```
offnet/
├── app/                    # React Native application screens
├── components/             # Reusable UI components
├── contexts/              # React context providers
├── utils/                 # Utility functions and helpers
├── constants/             # Configuration and constants
├── contracts/             # Algorand smart contracts
└── assets/               # Static assets and images
```

## Development

### Running Tests
```bash
npm test
```

### Building for Production
```bash
npm run build
```

### Linting
```bash
npm run lint
```

## Network Protocol

### Transaction Format
Transactions follow the Algorand transaction specification with additional metadata for mesh routing:
- Sender and receiver addresses
- Transaction amount and asset ID
- Mesh routing headers
- Digital signatures
- Timestamp and validity period

### Mesh Routing
The mesh protocol implements a flooding algorithm with TTL (time-to-live) counters:
- Transactions broadcast to all connected peers
- Duplicate detection prevents loops
- Hop counting limits network traversal
- Priority queuing for time-sensitive transactions

### Consensus Mechanism
Offnet uses a hybrid consensus approach:
- Local transaction validation
- Peer verification for conflict resolution
- Eventual consistency across network partitions
- Incentive alignment through relay rewards

## Security Considerations

### Cryptographic Security
- Ed25519 digital signatures for transaction authentication
- ECDH key exchange for secure communication channels
- AES-256 encryption for sensitive data storage
- Secure random number generation for key material

### Network Security
- Message authentication codes (MAC) for packet integrity
- Replay attack prevention through nonce mechanisms
- Rate limiting to prevent spam attacks
- Sybil attack resistance through proof-of-work

### Privacy Protection
- Transaction amount obfuscation techniques
- Identity unlinkability across transactions
- Metadata minimization in network protocols
- Optional transaction mixing capabilities

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request
5. Code review and approval process

### Code Standards
- TypeScript for type safety
- ESLint configuration enforcement
- Automated testing requirements
- Documentation for public APIs

### Issue Reporting
- Use GitHub Issues for bug reports
- Include reproduction steps and environment details
- Security issues should be reported privately
- Feature requests welcome with use case descriptions

## Roadmap

### Phase 1: Core Infrastructure
- Basic mesh networking implementation
- Transaction validation and storage
- Mobile application framework
- Smart contract deployment

### Phase 2: Advanced Features
- Smart voucher implementation
- Decentralized identity system
- Network incentive mechanisms
- Performance optimizations

### Phase 3: Network Expansion
- Cross-platform compatibility
- Advanced routing algorithms
- Integration with existing Web3 infrastructure
- Merchant and business tools

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Research and Documentation

### Academic References
- Bluetooth mesh networking specifications
- Offline consensus algorithm research
- Digital currency security analysis
- Peer-to-peer network topology studies

### Technical Documentation
- API reference documentation
- Protocol specification documents
- Security audit reports
- Performance benchmarking results

## Community

### Communication Channels
- GitHub Discussions for general questions
- Technical discussions in project issues
- Development coordination through project boards
- Regular community calls for major decisions

### Governance
- Community-driven development process
- Technical steering committee oversight
- Transparent decision-making procedures
- Open source contribution guidelines
