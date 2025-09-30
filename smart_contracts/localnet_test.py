"""
LocalNet Testing Script for Offnet Smart Contract
Tests deployment and functionality on Algorand LocalNet
"""

import sys
import time
import algosdk
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk import transaction

# LocalNet connection parameters
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def get_algod_client():
    """Get algod client for LocalNet"""
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def wait_for_confirmation(client, txid, timeout=4):
    """Wait for transaction confirmation"""
    start_round = client.status()["last-round"] + 1
    current_round = start_round
    
    while current_round < start_round + timeout:
        try:
            pending_txn = client.pending_transaction_info(txid)
        except Exception:
            return {}
        
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception(f'Pool error: {pending_txn["pool-error"]}')
            
        client.status_after_block(current_round)
        current_round += 1
        
    raise Exception(f"Transaction {txid} not confirmed after {timeout} rounds")

def create_test_account(client):
    """Create and fund a test account"""
    # Generate new account
    private_key, address = account.generate_account()
    
    print(f"Created test account: {address}")
    
    # Get dispenser account (pre-funded on LocalNet)
    dispenser_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    dispenser_key = mnemonic.to_private_key(dispenser_mnemonic)
    dispenser_address = account.address_from_private_key(dispenser_key)
    
    # Fund the test account
    params = client.suggested_params()
    txn = transaction.PaymentTxn(
        sender=dispenser_address,
        sp=params,
        receiver=address,
        amt=10_000_000  # 10 ALGO
    )
    
    signed_txn = txn.sign(dispenser_key)
    txid = client.send_transaction(signed_txn)
    wait_for_confirmation(client, txid)
    
    print(f"Funded account with 10 ALGO")
    return private_key, address

def deploy_contract(client, creator_key, creator_address):
    """Deploy the Offnet smart contract"""
    print("Deploying Offnet smart contract...")
    
    # Import and compile the contract
    try:
        from modern_offnet_contract import approval_program, clear_state_program
        print("Contract programs loaded successfully")
    except ImportError as e:
        print(f"Failed to import contract: {e}")
        print("Please ensure modern_offnet_contract.py exists and compiles")
        return None
    
    # Get transaction parameters
    params = client.suggested_params()
    
    # Create application transaction
    txn = transaction.ApplicationCreateTxn(
        sender=creator_address,
        sp=params,
        on_complete=algosdk.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_state_program,
        global_schema=transaction.StateSchema(num_uints=10, num_byte_slices=10),
        local_schema=transaction.StateSchema(num_uints=15, num_byte_slices=5)
    )
    
    # Sign and send
    signed_txn = txn.sign(creator_key)
    txid = client.send_transaction(signed_txn)
    
    # Wait for confirmation
    result = wait_for_confirmation(client, txid)
    app_id = result["application-index"]
    
    print(f"Contract deployed! App ID: {app_id}")
    return app_id

def test_opt_in_relay(client, user_key, user_address, app_id):
    """Test opt-in to relay network"""
    print("Testing relay opt-in...")
    
    params = client.suggested_params()
    
    # Opt-in to application
    txn = transaction.ApplicationOptInTxn(
        sender=user_address,
        sp=params,
        index=app_id
    )
    
    signed_txn = txn.sign(user_key)
    txid = client.send_transaction(signed_txn)
    wait_for_confirmation(client, txid)
    
    print("Successfully opted into relay network")

def test_process_relay(client, user_key, user_address, app_id):
    """Test mesh relay processing"""
    print("Testing mesh relay processing...")
    
    params = client.suggested_params()
    
    # Create application call for mesh relay
    app_args = [
        "process_mesh_relay".encode(),
        "test_relay_data".encode(),
        user_address.encode(),  # destination
        (1).to_bytes(8, 'big')  # hop_count
    ]
    
    txn = transaction.ApplicationNoOpTxn(
        sender=user_address,
        sp=params,
        index=app_id,
        app_args=app_args
    )
    
    signed_txn = txn.sign(user_key)
    txid = client.send_transaction(signed_txn)
    result = wait_for_confirmation(client, txid)
    
    print("Mesh relay processed successfully")
    return result

def run_localnet_tests():
    """Run comprehensive LocalNet tests"""
    print("Starting Offnet LocalNet Tests...")
    print("=" * 50)
    
    try:
        # Connect to LocalNet
        client = get_algod_client()
        status = client.status()
        print(f"Connected to LocalNet - Round: {status['last-round']}")
        
        # Create test accounts
        creator_key, creator_address = create_test_account(client)
        user_key, user_address = create_test_account(client)
        
        print(f"Creator: {creator_address}")
        print(f"User: {user_address}")
        
        # Deploy contract
        app_id = deploy_contract(client, creator_key, creator_address)
        
        # Test opt-in
        test_opt_in_relay(client, user_key, user_address, app_id)
        
        # Test relay processing
        test_process_relay(client, user_key, user_address, app_id)
        
        # Get account info to verify state
        account_info = client.account_info(user_address)
        local_state = account_info.get('apps-local-state', [])
        
        for app_state in local_state:
            if app_state['id'] == app_id:
                print("Local state after tests:")
                for kv in app_state.get('key-value', []):
                    key = kv['key']
                    value = kv['value']
                    print(f"  {key}: {value}")
        
        print("\n" + "=" * 50)
        print("All LocalNet tests completed successfully!")
        print(f"Contract App ID: {app_id}")
        print("You can interact with this contract using the React Native app")
        
        return app_id
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Offnet LocalNet Testing")
    print("Make sure LocalNet is running: algokit localnet start")
    
    # Check if LocalNet is running
    try:
        client = get_algod_client()
        client.status()
        print("LocalNet detected - starting tests...")
        run_localnet_tests()
    except Exception as e:
        print(f"Cannot connect to LocalNet: {e}")
        print("Please start LocalNet with: algokit localnet start")
        sys.exit(1)