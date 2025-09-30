"""
Modern Offnet Token Deployment Script using AlgoKit patterns
"""

import base64
import json
from pathlib import Path
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import (
    ApplicationCreateTxn, 
    PaymentTxn, 
    ApplicationCallTxn,
    wait_for_confirmation,
    OnComplete, 
    StateSchema
)
import os
import sys

# Add the smart_contracts directory to the path
sys.path.append(str(Path(__file__).parent))

from modern_offnet_contract import approval_program, clear_state_program
from pyteal import compileTeal, Mode


class ModernOffnetDeployer:
    """Modern deployment class with improved error handling and logging"""
    
    def __init__(self, algod_client, creator_private_key):
        self.algod_client = algod_client
        self.creator_private_key = creator_private_key
        self.creator_address = account.address_from_private_key(creator_private_key)
        
    def compile_program(self, source_code):
        """Compile TEAL source to bytecode"""
        try:
            teal_code = compileTeal(source_code, Mode.Application, version=8)
            response = self.algod_client.compile(teal_code)
            return base64.b64decode(response['result'])
        except Exception as e:
            print(f"Compilation error: {e}")
            raise
    
    def check_account_balance(self):
        """Check if account has sufficient balance"""
        try:
            account_info = self.algod_client.account_information(self.creator_address)
            balance = account_info.get('amount', 0) / 1_000_000  # Convert to ALGO
            print(f"Account balance: {balance} ALGO")
            
            if balance < 0.5:  # Need at least 0.5 ALGO for deployment
                print("⚠️  Warning: Low account balance. Please fund the account.")
                return False
            return True
        except Exception as e:
            print(f"Error checking account balance: {e}")
            return False
    
    def deploy_contract(self):
        """Deploy the modernized Offnet Token contract"""
        try:
            print("🚀 Starting contract deployment...")
            
            # Check balance first
            if not self.check_account_balance():
                return None
            
            # Get network parameters
            params = self.algod_client.suggested_params()
            
            # Compile programs
            print("📝 Compiling contract programs...")
            approval_bytecode = self.compile_program(approval_program())
            clear_bytecode = self.compile_program(clear_state_program())
            
            # Define state schema - increased for new features
            global_schema = StateSchema(
                num_uints=5,  # total_supply, mesh_fee, relay_count, token_asset_id, creator
                num_byte_slices=1  # For any string storage if needed
            )
            
            local_schema = StateSchema(
                num_uints=5,  # relay_balance, relay_count_local, is_active_relay, reputation_score, last_activity
                num_byte_slices=0
            )
            
            # Create application transaction
            print("📦 Creating application transaction...")
            app_create_txn = ApplicationCreateTxn(
                sender=self.creator_address,
                sp=params,
                on_complete=OnComplete.NoOpOC,
                approval_program=approval_bytecode,
                clear_program=clear_bytecode,
                global_schema=global_schema,
                local_schema=local_schema,
            )
            
            # Sign and submit transaction
            print("✏️  Signing and submitting transaction...")
            signed_txn = app_create_txn.sign(self.creator_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            print(f"Transaction ID: {txn_id}")
            
            # Wait for confirmation
            print("⏳ Waiting for confirmation...")
            confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            # Get application ID
            app_id = confirmed_txn["application-index"]
            app_address = self.get_application_address(app_id)
            
            print(f"✅ Contract deployed successfully!")
            print(f"📱 Application ID: {app_id}")
            print(f"🏠 Application Address: {app_address}")
            print(f"👤 Creator Address: {self.creator_address}")
            
            # Save deployment info
            deployment_info = {
                "app_id": app_id,
                "app_address": app_address,
                "creator_address": self.creator_address,
                "txn_id": txn_id,
                "network": "LocalNet",
                "timestamp": confirmed_txn["confirmed-round"],
                "global_schema": {
                    "num_uints": global_schema.num_uints,
                    "num_byte_slices": global_schema.num_byte_slices
                },
                "local_schema": {
                    "num_uints": local_schema.num_uints,
                    "num_byte_slices": local_schema.num_byte_slices
                }
            }
            
            # Save to file
            deployment_file = Path(__file__).parent / "deployment_info.json"
            with open(deployment_file, "w") as f:
                json.dump(deployment_info, f, indent=2)
            print(f"💾 Deployment info saved to: {deployment_file}")
            
            return app_id
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            return None
    
    def get_application_address(self, app_id):
        """Get the application's Algorand address"""
        import algosdk.encoding as encoding
        return encoding.encode_address(encoding.checksum(b"appID" + app_id.to_bytes(8, "big")))
    
    def fund_application(self, app_id, amount_algo=1):
        """Fund the application account with ALGOs"""
        try:
            print(f"💰 Funding application account with {amount_algo} ALGO...")
            
            app_address = self.get_application_address(app_id)
            params = self.algod_client.suggested_params()
            
            # Create payment transaction
            pay_txn = PaymentTxn(
                sender=self.creator_address,
                sp=params,
                receiver=app_address,
                amt=int(amount_algo * 1_000_000),  # Convert to microAlgos
            )
            
            # Sign and submit
            signed_pay_txn = pay_txn.sign(self.creator_private_key)
            txn_id = self.algod_client.send_transaction(signed_pay_txn)
            
            # Wait for confirmation
            wait_for_confirmation(self.algod_client, txn_id, 4)
            print(f"✅ Application funded successfully! Transaction ID: {txn_id}")
            
            return txn_id
            
        except Exception as e:
            print(f"❌ Application funding failed: {str(e)}")
            return None
    
    def create_token_asset(self, app_id):
        """Call the contract to create the token asset"""
        try:
            print("🪙 Creating token asset...")
            
            params = self.algod_client.suggested_params()
            
            # Create application call transaction
            app_call_txn = ApplicationCallTxn(
                sender=self.creator_address,
                sp=params,
                index=app_id,
                on_complete=OnComplete.NoOpOC,
                app_args=["create_token"],
            )
            
            # Sign and submit
            signed_txn = app_call_txn.sign(self.creator_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            # Try to extract asset ID from logs
            asset_id = None
            if 'logs' in confirmed_txn:
                for log_entry in confirmed_txn['logs']:
                    decoded_log = base64.b64decode(log_entry).decode('utf-8', errors='ignore')
                    print(f"📋 Log: {decoded_log}")
            
            print(f"✅ Token creation transaction confirmed! Transaction ID: {txn_id}")
            return txn_id
            
        except Exception as e:
            print(f"❌ Token creation failed: {str(e)}")
            return None


def get_localnet_client():
    """Get AlgoKit LocalNet client"""
    return algod.AlgodClient(
        algod_token="a" * 64,
        algod_address="http://localhost:4001"
    )


def get_localnet_dispenser():
    """Get LocalNet dispenser account for testing"""
    # Default LocalNet dispenser mnemonic
    dispenser_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon absorb"
    return mnemonic.to_private_key(dispenser_mnemonic)


def main():
    """Main deployment function"""
    print("🎯 Modern Offnet Token Deployment")
    print("=" * 50)
    
    try:
        # Get AlgoKit LocalNet client
        algod_client = get_localnet_client()
        
        # Test connection
        status = algod_client.status()
        print(f"🌐 Connected to LocalNet (Round: {status['last-round']})")
        
        # Get deployer account
        private_key = os.getenv("ALGORAND_PRIVATE_KEY") or get_localnet_dispenser()
        
        # Initialize deployer
        deployer = ModernOffnetDeployer(algod_client, private_key)
        
        print(f"👤 Deploying from: {deployer.creator_address}")
        
        # Deploy contract
        app_id = deployer.deploy_contract()
        
        if app_id:
            print(f"\n🎉 Phase 1 Complete - Contract Deployed!")
            
            # Fund the application
            fund_txn = deployer.fund_application(app_id, 2)  # Fund with 2 ALGO
            
            if fund_txn:
                print(f"\n💰 Phase 2 Complete - Application Funded!")
                
                # Create token asset
                create_txn = deployer.create_token_asset(app_id)
                
                if create_txn:
                    print(f"\n🪙 Phase 3 Complete - Token Asset Created!")
                    
                    print(f"\n🎊 DEPLOYMENT SUCCESSFUL! 🎊")
                    print(f"Application ID: {app_id}")
                    print(f"Application Address: {deployer.get_application_address(app_id)}")
                    print(f"🔗 LocalNet Explorer: http://localhost:8980/application/{app_id}")
                else:
                    print("⚠️  Token creation failed, but contract is deployed")
            else:
                print("⚠️  Application funding failed, but contract is deployed")
                
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)