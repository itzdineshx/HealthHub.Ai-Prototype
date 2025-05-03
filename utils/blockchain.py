# utils/blockchain.py

import os
import hashlib
import datetime
import json
from pathlib import Path
from utils.db import add_health_record, get_health_records

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using default values")

# Mock mode for development/testing without blockchain connection
MOCK_MODE = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")

# Setup Web3 with error handling
try:
    from web3 import Web3
    
    # Setup Web3 connection
    web3_provider = os.getenv("WEB3_RPC", "http://localhost:8545")
    w3 = Web3(Web3.HTTPProvider(web3_provider))
    
    # Check connection
    if not w3.is_connected():
        print(f"Warning: Could not connect to Web3 provider at {web3_provider}")
        print("Running in MOCK_MODE")
        MOCK_MODE = True
    
    # Setup contract
    try:
        contract_address = os.getenv("CONTRACT_ADDRESS")
        if contract_address:
            contract_address = Web3.toChecksumAddress(contract_address)
            
            # Try to load ABI
            abi_path = Path("contract_abi.json")
            if abi_path.exists():
                with open(abi_path) as f:
                    abi = json.load(f)
                contract = w3.eth.contract(address=contract_address, abi=abi)
            else:
                print(f"Warning: ABI file not found at {abi_path}")
                MOCK_MODE = True
        else:
            print("Warning: CONTRACT_ADDRESS not set in environment")
            MOCK_MODE = True
            
        # Check for account
        if not MOCK_MODE:
            try:
                ADMIN_ADDR = w3.eth.accounts[0]
            except (IndexError, Exception) as e:
                print(f"Warning: No available accounts: {e}")
                MOCK_MODE = True
    except Exception as e:
        print(f"Error setting up contract: {e}")
        MOCK_MODE = True
        
except ImportError:
    print("Warning: web3 not installed, running in mock mode")
    MOCK_MODE = True

def generate_mock_tx_hash():
    """Generate a mock transaction hash for testing"""
    import random
    return "0x" + "".join(random.choices("0123456789abcdef", k=64))

def store_hash(pdf_file, user_id="user_123"):
    """
    - Computes SHA-256 of the uploaded PDF
    - Sends tx to store it on‑chain (or mocks if MOCK_MODE)
    - Logs metadata in SQLite
    - Returns the transaction hash
    """
    # 1. Read file bytes & compute SHA-256
    pdf_bytes = pdf_file.read()
    file_hash = hashlib.sha256(pdf_bytes).hexdigest()
    
    # Reset file pointer for potential future reads
    pdf_file.seek(0)
    
    try:
        if MOCK_MODE:
            # Mock blockchain transaction in test mode
            tx_hash = generate_mock_tx_hash()
            block_number = 12345678
        else:
            # 2. Send blockchain transaction
            nonce = w3.eth.get_transaction_count(ADMIN_ADDR)
            tx = contract.functions.storeHash(file_hash).buildTransaction({
                "from": ADMIN_ADDR,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": w3.toWei("2", "gwei")
            })
            
            # Use private key if provided, otherwise use unlocked account
            private_key = os.getenv("ADMIN_PRIVATE_KEY")
            if private_key:
                signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            else:
                tx_hash = w3.eth.send_transaction(tx)
                
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            block_number = tx_receipt.blockNumber
            tx_hash = tx_hash.hex()
        
        # 3. Store metadata in SQLite
        record = {
            "user_id": user_id,
            "filename": pdf_file.name,
            "file_hash": file_hash,
            "tx_hash": tx_hash,
            "block_number": block_number,
            "timestamp": datetime.datetime.utcnow(),
        }
        record_id = add_health_record(record)
        
        return tx_hash
        
    except Exception as e:
        # Log the error and re-raise it
        error_msg = f"Error storing hash: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)


def fetch_records(user_id="user_123"):
    """
    Query SQLite for all health_records by this user.
    Returns a list of dicts.
    """
    try:
        records = get_health_records(user_id)
        
        # Format timestamps
        for rec in records:
            if isinstance(rec["timestamp"], datetime.datetime):
                rec["timestamp"] = rec["timestamp"].isoformat() + "Z"
                
        return records
    except Exception as e:
        print(f"Error fetching records: {e}")
        return []
