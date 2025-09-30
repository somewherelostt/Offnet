"""
Offnet Token Deployment Script for Algorand
This script deploys the Offnet Token smart contract to Algorand TestNet
"""

import base64
import json
from algosdk import account, mnemonic, logic
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCreateTxn, PaymentTxn, wait_for_confirmation
from algosdk.transaction import OnComplete, StateSchema
from pyteal import *
import os

# Import our contract
from offnet_token import offnet_token_contract, clear_state_program

class OffnetTokenDeployer:
    def __init__(self, algod_client, creator_private_key):
        self.algod_client = algod_client
        self.creator_private_key = creator_private_key
        self.creator_address = account.address_from_private_key(creator_private_key)
        
    def compile_program(self, source_code):
        """Compile PyTeal to TEAL and then to bytecode"""
        teal_code = compileTeal(source_code, Mode.Application, version=6)
        response = self.algod_client.compile(teal_code)
        return base64.b64decode(response['result'])
    
    def deploy_contract(self):
        """Deploy the Offnet Token contract"""
        try:
            # Get network parameters
            params = self.algod_client.suggested_params()
            
            # Compile contract programs
            approval_program = self.compile_program(offnet_token_contract())
            clear_program = self.compile_program(clear_state_program())
            
            # Define state schema
            global_schema = StateSchema(
                num_uints=4,  # total_supply, mesh_fee, relay_count, creator
                num_byte_slices=1  # creator address
            )
            
            local_schema = StateSchema(
                num_uints=3,  # relay_balance, relay_count_local, is_active_relay
                num_byte_slices=0
            )
            
            # Create application transaction
            app_create_txn = ApplicationCreateTxn(
                sender=self.creator_address,
                sp=params,
                on_complete=OnComplete.NoOpOC,
                approval_program=approval_program,
                clear_program=clear_program,
                global_schema=global_schema,
                local_schema=local_schema
            )
            
            # Sign transaction
            signed_txn = app_create_txn.sign(self.creator_private_key)
            
            # Submit transaction
            txn_id = self.algod_client.send_transaction(signed_txn)
            print(f"Transaction ID: {txn_id}")
            
            # Wait for confirmation
            confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            # Get application ID
            app_id = confirmed_txn["application-index"]
            print(f"Offnet Token Contract deployed successfully!")
            print(f"Application ID: {app_id}")
            print(f"Creator Address: {self.creator_address}")
            
            # Save deployment info
            deployment_info = {
                "app_id": app_id,
                "creator_address": self.creator_address,
                "txn_id": txn_id,
                "network": "TestNet",
                "timestamp": confirmed_txn["confirmed-round"]
            }
            
            with open("deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            return app_id
            
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            return None
    
    def create_offnet_asset(self, app_id):
        """Create the Offnet ASA token"""
        try:
            params = self.algod_client.suggested_params()
            
            # Asset creation parameters
            asset_creation_txn = AssetConfigTxn(
                sender=self.creator_address,
                sp=params,
                total=1000000 * 1000000,  # 1M tokens with 6 decimals
                default_frozen=False,
                unit_name="OFFNET",
                asset_name="Offnet Token",
                manager=self.creator_address,
                reserve=self.creator_address,
                freeze=None,
                clawback=None,
                url="https://offnet.app",
                decimals=6
            )
            
            # Sign and submit
            signed_txn = asset_creation_txn.sign(self.creator_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
            asset_id = confirmed_txn["asset-index"]
            
            print(f"Offnet ASA Token created successfully!")
            print(f"Asset ID: {asset_id}")
            
            return asset_id
            
        except Exception as e:
            print(f"Asset creation failed: {str(e)}")
            return None

def main():
    """Main deployment function"""
    # Algorand TestNet connection
    algod_address = "https://testnet-api.algonode.cloud"
    algod_token = ""
    
    # Initialize Algod client
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    # Check if we have a private key
    private_key = os.getenv("ALGORAND_PRIVATE_KEY")
    if not private_key:
        print("Generating new account for deployment...")
        private_key, address = account.generate_account()
        print(f"Generated Address: {address}")
        print(f"Private Key: {private_key}")
        print("Please fund this account with TestNet ALGO and set ALGORAND_PRIVATE_KEY environment variable")
        return
    
    # Initialize deployer
    deployer = OffnetTokenDeployer(algod_client, private_key)
    
    print(f"Deploying from address: {deployer.creator_address}")
    
    # Check account balance
    try:
        account_info = algod_client.account_information(deployer.creator_address)
        balance = account_info.get('amount', 0) / 1000000  # Convert to ALGO
        print(f"Account balance: {balance} ALGO")
        
        if balance < 0.1:
            print("Insufficient balance for deployment. Please fund the account.")
            return
            
    except Exception as e:
        print(f"Error checking account: {str(e)}")
        return
    
    # Deploy the contract
    app_id = deployer.deploy_contract()
    
    if app_id:
        # Create the ASA token
        asset_id = deployer.create_offnet_asset(app_id)
        
        if asset_id:
            print(f"\n🎉 Deployment Complete!")
            print(f"📱 App ID: {app_id}")
            print(f"🪙 Asset ID: {asset_id}")
            print(f"🔗 Explorer: https://testnet.algoexplorer.io/application/{app_id}")
            
            # Update the constants file
            try:
                constants_path = "../constants/algorand.ts"
                if os.path.exists(constants_path):
                    with open(constants_path, 'r') as f:
                        content = f.read()
                    
                    # Update the app ID and asset ID
                    content = content.replace(
                        "OFFNET_TOKEN_ID: 0,", 
                        f"OFFNET_TOKEN_ID: {asset_id},"
                    )
                    content = content.replace(
                        "MESH_RELAY_APP_ID: 0,", 
                        f"MESH_RELAY_APP_ID: {app_id},"
                    )
                    
                    with open(constants_path, 'w') as f:
                        f.write(content)
                    
                    print(f"✅ Updated constants file with deployment info")
                        
            except Exception as e:
                print(f"Warning: Could not update constants file: {str(e)}")

if __name__ == "__main__":
    main()