
# Swarms Exchange API

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)


[![GitHub stars](https://img.shields.io/github/stars/The-Swarm-Corporation/Legal-Swarm-Template?style=social)](https://github.com/The-Swarm-Corporation/Legal-Swarm-Template)
[![Swarms Framework](https://img.shields.io/badge/Built%20with-Swarms-blue)](https://github.com/kyegomez/swarms)

This project provides a production-grade API to create and manage tokens on the Solana blockchain using the Pump.fun platform. Built with **FastAPI**, it offers endpoints for creating tokens, buying tokens, and performing both actions together.

## Features
- Create custom tokens with metadata uploaded to IPFS.
- Purchase tokens immediately after creation.
- Integrated logging using `loguru`.
- Robust error handling with detailed feedback.
- CORS-enabled for cross-origin requests.
- Configurable endpoints with middleware support.

## Requirements

- Python 3.9 or higher
- Solana development environment set up
- Dependencies installed (see below)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/The-Swarm-Corporation/Swarms-Exchange-API
   cd Swarms-Exchange-API
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Access API Documentation**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

### 1. Create Token
**POST** `/create-token`

Uploads token metadata to IPFS and creates a new token on the Solana blockchain.

#### Request Body
```json
{
    "private_key": "<base58-private-key>",
    "token_name": "MyToken",
    "token_symbol": "MTK",
    "description": "This is a test token.",
    "twitter": "https://twitter.com/mytoken",
    "telegram": "https://t.me/mytoken",
    "website": "https://mytoken.com",
    "amount": 1000,
    "slippage": 10,
    "priority_fee": 0.0005,
    "pool": "pump",
    "rpc_endpoint": "https://api.mainnet-beta.solana.com/"
}
```

#### Response
```json
{
    "message": "Token created successfully",
    "transaction_url": "https://solscan.io/tx/<transaction-id>"
}
```

---

### 2. Buy Token
**POST** `/buy-token`

Allows users to purchase existing tokens.

#### Request Body
```json
{
    "private_key": "<base58-private-key>",
    "mint_address": "<mint-address>",
    "amount": 100,
    "slippage": 10,
    "priority_fee": 0.0005,
    "pool": "pump",
    "rpc_endpoint": "https://api.mainnet-beta.solana.com/"
}
```

#### Response
```json
{
    "message": "Token purchased successfully",
    "transaction_url": "https://solscan.io/tx/<transaction-id>"
}
```

---

### 3. Create and Buy Tokens
**POST** `/create-and-buy`

Combines token creation and purchase into a single action.

#### Request Body
```json
{
    "private_key": "<base58-private-key>",
    "token_name": "MyToken",
    "token_symbol": "MTK",
    "description": "This is a test token.",
    "twitter": "https://twitter.com/mytoken",
    "telegram": "https://t.me/mytoken",
    "website": "https://mytoken.com",
    "total_tokens": 1000,
    "slippage": 10,
    "priority_fee": 0.0005,
    "pool": "pump",
    "rpc_endpoint": "https://api.mainnet-beta.solana.com/"
}
```

#### Response
```json
{
    "message": "Token created and purchased successfully",
    "create_transaction_url": "https://solscan.io/tx/<create-transaction-id>",
    "buy_transaction_url": "https://solscan.io/tx/<buy-transaction-id>"
}
```

## Environment Variables
- Ensure your environment supports Python's FastAPI and Solana libraries.
- Configure Solana RPC endpoints if using custom networks.

## Logging
- All API activities are logged using `loguru` for better debugging and traceability.

## Error Handling
Detailed HTTP exceptions and logs are provided for issues related to:
- Metadata upload
- Token creation
- Transaction signing and submission
- Swarm fee transfers

## License
This project is licensed under the MIT License.

