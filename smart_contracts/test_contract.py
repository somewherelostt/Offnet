"""
Test script for Modern Offnet Token Contract
Tests all major functionality on LocalNet
"""

import json
import base64
from pathlib import Path
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import (
    ApplicationCallTxn, 
    ApplicationOptInTxn,
    wait_for_confirmation,
    OnComplete
)


class OffnetTokenTester:
    """Test suite for Offnet Token contract"""
    
    def __init__(self, algod_client, app_id, creator_private_key):
        self.algod_client = algod_client
        self.app_id = app_id
        self.creator_private_key = creator_private_key
        self.creator_address = account.address_from_private_key(creator_private_key)
        
        # Create test relay accounts
        self.relay1_private_key, self.relay1_address = account.generate_account()
        self.relay2_private_key, self.relay2_address = account.generate_account()
        
    def fund_test_accounts(self):
        """Fund test relay accounts"""
        print("💰 Funding test accounts...")
        
        from deploy_modern import get_localnet_dispenser
        dispenser_key = get_localnet_dispenser()
        
        for i, (name, address, _) in enumerate([
            ("relay1", self.relay1_address, self.relay1_private_key),
            ("relay2", self.relay2_address, self.relay2_private_key)
        ]):
            try:
                params = self.algod_client.suggested_params()
                from algosdk.transaction import PaymentTxn
                
                pay_txn = PaymentTxn(
                    sender=account.address_from_private_key(dispenser_key),
                    sp=params,
                    receiver=address,
                    amt=5_000_000,  # 5 ALGO
                )
                
                signed_txn = pay_txn.sign(dispenser_key)
                txn_id = self.algod_client.send_transaction(signed_txn)
                wait_for_confirmation(self.algod_client, txn_id, 4)
                
                print(f"✅ Funded {name}: {address}")
                
            except Exception as e:
                print(f"❌ Failed to fund {name}: {e}")
    
    def test_relay_opt_in(self):
        """Test relay node opt-in functionality"""
        print("\n🔄 Testing Relay Opt-in...")
        
        for name, address, private_key in [
            ("relay1", self.relay1_address, self.relay1_private_key),
            ("relay2", self.relay2_address, self.relay2_private_key)
        ]:
            try:
                params = self.algod_client.suggested_params()
                
                opt_in_txn = ApplicationOptInTxn(
                    sender=address,
                    sp=params,
                    index=self.app_id,
                )
                
                signed_txn = opt_in_txn.sign(private_key)
                txn_id = self.algod_client.send_transaction(signed_txn)
                
                confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
                
                # Check for logs
                if 'logs' in confirmed_txn:
                    for log_entry in confirmed_txn['logs']:
                        decoded_log = base64.b64decode(log_entry).decode('utf-8', errors='ignore')
                        print(f"📋 {name} opt-in log: {decoded_log}")
                
                print(f"✅ {name} opted in successfully")
                
            except Exception as e:
                print(f"❌ {name} opt-in failed: {e}")
    
    def test_mesh_relay(self):
        """Test mesh relay functionality"""
        print("\n🌐 Testing Mesh Relay...")
        
        for i, (name, address, private_key) in enumerate([
            ("relay1", self.relay1_address, self.relay1_private_key),
            ("relay2", self.relay2_address, self.relay2_private_key)
        ]):
            try:
                params = self.algod_client.suggested_params()
                
                app_call_txn = ApplicationCallTxn(
                    sender=address,
                    sp=params,
                    index=self.app_id,
                    on_complete=OnComplete.NoOpOC,
                    app_args=[
                        "mesh_relay",
                        f"test_data_from_{name}",
                        self.creator_address,  # destination
                        str(i + 1)  # hop count
                    ],
                )
                
                signed_txn = app_call_txn.sign(private_key)
                txn_id = self.algod_client.send_transaction(signed_txn)
                
                confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
                
                # Check for logs
                if 'logs' in confirmed_txn:
                    for log_entry in confirmed_txn['logs']:
                        decoded_log = base64.b64decode(log_entry).decode('utf-8', errors='ignore')
                        print(f"📋 {name} relay log: {decoded_log}")
                
                print(f"✅ {name} mesh relay successful")
                
            except Exception as e:
                print(f"❌ {name} mesh relay failed: {e}")
    
    def test_fee_withdrawal(self):
        """Test relay fee withdrawal"""
        print("\n💸 Testing Fee Withdrawal...")
        
        for name, address, private_key in [
            ("relay1", self.relay1_address, self.relay1_private_key),
        ]:  # Test with just one for now
            try:
                params = self.algod_client.suggested_params()
                
                app_call_txn = ApplicationCallTxn(
                    sender=address,
                    sp=params,
                    index=self.app_id,
                    on_complete=OnComplete.NoOpOC,
                    app_args=["withdraw_fees"],
                )
                
                signed_txn = app_call_txn.sign(private_key)
                txn_id = self.algod_client.send_transaction(signed_txn)
                
                confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
                
                # Check for logs
                if 'logs' in confirmed_txn:
                    for log_entry in confirmed_txn['logs']:
                        decoded_log = base64.b64decode(log_entry).decode('utf-8', errors='ignore')
                        print(f"📋 {name} withdrawal log: {decoded_log}")
                
                print(f"✅ {name} fee withdrawal successful")
                
            except Exception as e:
                print(f"❌ {name} fee withdrawal failed: {e}")
    
    def test_update_mesh_fee(self):
        """Test mesh fee update (creator only)"""
        print("\n⚙️  Testing Mesh Fee Update...")
        
        try:
            params = self.algod_client.suggested_params()
            
            app_call_txn = ApplicationCallTxn(
                sender=self.creator_address,
                sp=params,
                index=self.app_id,
                on_complete=OnComplete.NoOpOC,
                app_args=["update_fee", "2000"],  # Change to 0.002 ALGO
            )
            
            signed_txn = app_call_txn.sign(self.creator_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            confirmed_txn = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            # Check for logs
            if 'logs' in confirmed_txn:
                for log_entry in confirmed_txn['logs']:
                    decoded_log = base64.b64decode(log_entry).decode('utf-8', errors='ignore')
                    print(f"📋 Fee update log: {decoded_log}")
            
            print("✅ Mesh fee update successful")
            
        except Exception as e:
            print(f"❌ Mesh fee update failed: {e}")
    
    def check_application_state(self):
        """Check global and local application state"""
        print("\n📊 Checking Application State...")
        
        try:
            # Get global state
            app_info = self.algod_client.application_info(self.app_id)
            global_state = app_info.get('params', {}).get('global-state', [])
            
            print("🌍 Global State:")
            for state_item in global_state:
                key = base64.b64decode(state_item['key']).decode('utf-8')
                value = state_item['value']
                
                if value['type'] == 1:  # bytes
                    decoded_value = base64.b64decode(value['bytes'])
                    print(f"  {key}: {decoded_value}")
                else:  # uint
                    print(f"  {key}: {value['uint']}")
            
            # Check local state for relay1
            try:
                account_info = self.algod_client.account_info(self.relay1_address)
                apps_local_state = account_info.get('apps-local-state', [])
                
                for app_state in apps_local_state:
                    if app_state['id'] == self.app_id:
                        print(f"\n🏠 Local State for {self.relay1_address}:")
                        local_state = app_state.get('key-value', [])
                        
                        for state_item in local_state:
                            key = base64.b64decode(state_item['key']).decode('utf-8')
                            value = state_item['value']
                            
                            if value['type'] == 1:  # bytes
                                decoded_value = base64.b64decode(value['bytes'])
                                print(f"  {key}: {decoded_value}")
                            else:  # uint
                                print(f"  {key}: {value['uint']}")
                        break
                        
            except Exception as e:
                print(f"Could not read local state: {e}")
                
        except Exception as e:
            print(f"❌ State check failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Modern Offnet Token Contract Tests")
    print("=" * 50)
    
    # Load deployment info
    deployment_file = Path(__file__).parent / "deployment_info.json"
    if not deployment_file.exists():
        print("❌ No deployment info found. Please deploy the contract first.")
        return False
    
    with open(deployment_file) as f:
        deployment_info = json.load(f)
    
    app_id = deployment_info['app_id']
    print(f"🎯 Testing Application ID: {app_id}")
    
    # Get LocalNet client
    from deploy_modern import get_localnet_client, get_localnet_dispenser
    algod_client = get_localnet_client()
    creator_key = get_localnet_dispenser()
    
    # Initialize tester
    tester = OffnetTokenTester(algod_client, app_id, creator_key)
    
    # Run tests
    try:
        tester.fund_test_accounts()
        tester.test_relay_opt_in()
        tester.test_mesh_relay()
        tester.test_update_mesh_fee()
        tester.test_mesh_relay()  # Test again with new fee
        tester.test_fee_withdrawal()
        tester.check_application_state()
        
        print(f"\n🎉 All tests completed!")
        print(f"🔗 View on LocalNet Explorer: http://localhost:8980/application/{app_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)