# MediFlow Ledger | Smart Contracts

This directory contains the Ethereum-based accountability layer for the MediFlow TB Diagnostic system.

## 🛠️ Tech Stack
- **Solidity** (^0.8.19)
- **Foundry** (Forge & Cast)

## 🚀 Quick Start for Judges

### 1. Install Foundry
If you don't have Foundry installed, run:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 2. Install Dependencies
Install the standard library (Forge-std):
```bash
forge install
```

### 3. Compile Contracts
Build the artifacts:
```bash
forge build
```

### 4. Run Tests
Verify the ledger logic:
```bash
forge test
```

## 🌐 Deployment (Local Anvil)

To deploy the ledger to a local test node:

1. **Start Anvil:**
```bash
anvil
```

2. **Deploy:**
In a new terminal, run:
```bash
forge create src/MediFlow.sol:MediFlow --rpc-url http://127.0.0.1:8545 --interactive
```

---
**Note:** After deployment, copy the `Deployed to:` address and update the `CONTRACT_ADDRESS` in the root `.env` file to enable backend integration.
