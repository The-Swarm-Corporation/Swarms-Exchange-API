import requests
import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.commitment_config import CommitmentLevel
from solders.rpc.requests import SendVersionedTransaction
from solders.rpc.config import RpcSendTransactionConfig
from loguru import logger
import base58

# Initialize FastAPI application
app = FastAPI(
    title="Token Creation API",
    description="API for creating and managing tokens via Pump.fun",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global constants
SWARM_FEE_ADDRESS = "7MaX4muAn8ZQREJxnupm8sgokwFHujgrGfH9Qn81BuEV"

# Request model for token creation
class TokenCreationRequest(BaseModel):
    private_key: str
    token_name: str
    token_symbol: str
    description: str
    twitter: str
    telegram: str
    website: str
    amount: int
    slippage: int = 10
    priority_fee: float = 0.0005
    pool: str = "pump"
    rpc_endpoint: str = "https://api.mainnet-beta.solana.com/"

# Request model for token purchase
class TokenPurchaseRequest(BaseModel):
    private_key: str
    mint_address: str
    amount: int
    slippage: int = 10
    priority_fee: float = 0.0005
    pool: str = "pump"
    rpc_endpoint: str = "https://api.mainnet-beta.solana.com/"

# Event handlers for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Token Creation API server...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Token Creation API server...")

@app.post("/create-token", summary="Create a new token", tags=["Token Operations"])
async def create_token(request: TokenCreationRequest, file: UploadFile = File(...)):
    try:
        logger.info("Processing token creation request...")

        # Load keypair
        signer_keypair = Keypair.from_base58_string(request.private_key)
        mint_keypair = Keypair()

        # Define token metadata
        form_data = {
            "name": request.token_name,
            "symbol": request.token_symbol,
            "description": request.description,
            "twitter": request.twitter,
            "telegram": request.telegram,
            "website": request.website,
            "showName": "true",
        }

        # Read the uploaded image file
        file_content = await file.read()
        files = {"file": (file.filename, file_content, file.content_type)}

        # Upload metadata to IPFS
        metadata_response = requests.post("https://pump.fun/api/ipfs", data=form_data, files=files)
        if metadata_response.status_code != 200:
            logger.error(f"Metadata upload failed: {metadata_response.text}")
            raise HTTPException(status_code=400, detail=f"Metadata upload failed: {metadata_response.text}")

        metadata_uri = metadata_response.json()["metadataUri"]
        token_metadata = {
            "name": request.token_name,
            "symbol": request.token_symbol,
            "uri": metadata_uri,
        }

        # Create the token
        create_response = requests.post(
            "https://pumpportal.fun/api/trade-local",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "publicKey": str(signer_keypair.pubkey()),
                "action": "create",
                "tokenMetadata": token_metadata,
                "mint": str(mint_keypair.pubkey()),
                "denominatedInSol": "true",
                "amount": request.amount,
                "slippage": request.slippage,
                "priorityFee": request.priority_fee,
                "pool": request.pool,
            }),
        )

        if create_response.status_code != 200:
            logger.error(f"Token creation failed: {create_response.text}")
            raise HTTPException(status_code=400, detail=f"Token creation failed: {create_response.text}")

        tx = VersionedTransaction(VersionedTransaction.from_bytes(create_response.content).message, [mint_keypair, signer_keypair])
        config = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.Confirmed)
        tx_payload = SendVersionedTransaction(tx, config)

        rpc_response = requests.post(
            url=request.rpc_endpoint,
            headers={"Content-Type": "application/json"},
            data=tx_payload.to_json(),
        )

        if rpc_response.status_code != 200:
            logger.error(f"Transaction failed: {rpc_response.text}")
            raise HTTPException(status_code=400, detail=f"Transaction failed: {rpc_response.text}")

        tx_signature = rpc_response.json()["result"]

        # Send Swarm Fee
        fee_response = requests.post(
            "https://pumpportal.fun/api/trade-local",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "publicKey": str(signer_keypair.pubkey()),
                "action": "transfer",
                "mint": "So11111111111111111111111111111111111111112",
                "recipient": SWARM_FEE_ADDRESS,
                "amount": 0.2,
            }),
        )

        if fee_response.status_code != 200:
            logger.error(f"Fee transfer failed: {fee_response.text}")
            raise HTTPException(status_code=400, detail=f"Fee transfer failed: {fee_response.text}")

        logger.info("Token creation successful.")
        return {"message": "Token created successfully", "transaction_url": f"https://solscan.io/tx/{tx_signature}"}

    except Exception as e:
        logger.exception("An error occurred during token creation.")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/buy-token", summary="Buy a token", tags=["Token Operations"])
async def buy_token(request: TokenPurchaseRequest):
    try:
        logger.info("Processing token purchase request...")

        # Load keypair
        signer_keypair = Keypair.from_base58_string(request.private_key)

        # Prepare the buy transaction
        buy_response = requests.post(
            "https://pumpportal.fun/api/trade-local",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "publicKey": str(signer_keypair.pubkey()),
                "action": "buy",
                "mint": request.mint_address,
                "denominatedInSol": "true",
                "amount": request.amount,
                "slippage": request.slippage,
                "priorityFee": request.priority_fee,
                "pool": request.pool,
            }),
        )

        if buy_response.status_code != 200:
            logger.error(f"Token purchase failed: {buy_response.text}")
            raise HTTPException(status_code=400, detail=f"Token purchase failed: {buy_response.text}")

        tx = VersionedTransaction(VersionedTransaction.from_bytes(buy_response.content).message, [signer_keypair])
        config = RpcSendTransactionConfig(preflight_commitment=CommitmentLevel.Confirmed)
        tx_payload = SendVersionedTransaction(tx, config)

        rpc_response = requests.post(
            url=request.rpc_endpoint,
            headers={"Content-Type": "application/json"},
            data=tx_payload.to_json(),
        )

        if rpc_response.status_code != 200:
            logger.error(f"Transaction failed: {rpc_response.text}")
            raise HTTPException(status_code=400, detail=f"Transaction failed: {rpc_response.text}")

        tx_signature = rpc_response.json()["result"]

        logger.info("Token purchase successful.")
        return {"message": "Token purchased successfully", "transaction_url": f"https://solscan.io/tx/{tx_signature}"}

    except Exception as e:
        logger.exception("An error occurred during token purchase.")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
