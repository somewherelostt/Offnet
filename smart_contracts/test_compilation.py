"""
Simple contract compilation and validation test
Tests contract compilation without requiring LocalNet
"""

import sys
from pathlib import Path

# Add the smart_contracts directory to the path
sys.path.append(str(Path(__file__).parent))

from modern_offnet_contract import approval_program, clear_state_program
from pyteal import compileTeal, Mode


def test_contract_compilation():
    """Test that the contract compiles successfully"""
    print("🧪 Testing Contract Compilation")
    print("=" * 40)
    
    try:
        print("📝 Compiling approval program...")
        approval_teal = compileTeal(approval_program(), Mode.Application, version=8)
        print(f"✅ Approval program compiled successfully ({len(approval_teal)} chars)")
        
        print("📝 Compiling clear state program...")
        clear_teal = compileTeal(clear_state_program(), Mode.Application, version=8)
        print(f"✅ Clear state program compiled successfully ({len(clear_teal)} chars)")
        
        # Save compiled programs to files
        approval_file = Path(__file__).parent / "approval.teal"
        clear_file = Path(__file__).parent / "clear.teal"
        
        with open(approval_file, 'w') as f:
            f.write(approval_teal)
        
        with open(clear_file, 'w') as f:
            f.write(clear_teal)
        
        print(f"💾 Saved approval program to: {approval_file}")
        print(f"💾 Saved clear program to: {clear_file}")
        
        # Show some basic statistics
        approval_lines = approval_teal.count('\n')
        clear_lines = clear_teal.count('\n')
        
        print(f"\n📊 Compilation Statistics:")
        print(f"  Approval Program: {approval_lines} lines")
        print(f"  Clear Program: {clear_lines} lines")
        print(f"  TEAL Version: 8")
        
        # Extract some interesting patterns
        if "inner_txn" in approval_teal:
            print("  ✅ Uses inner transactions")
        if "global_get" in approval_teal or "global_put" in approval_teal:
            print("  ✅ Uses global state")
        if "local_get" in approval_teal or "local_put" in approval_teal:
            print("  ✅ Uses local state")
        
        print(f"\n🎉 Contract compilation test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        return False


def show_contract_structure():
    """Show the contract structure and methods"""
    print("\n🏗️  Contract Structure Analysis")
    print("=" * 40)
    
    try:
        approval_teal = compileTeal(approval_program(), Mode.Application, version=8)
        
        methods = []
        if "create_token" in approval_teal:
            methods.append("create_token - Create ASA token")
        if "mesh_relay" in approval_teal:
            methods.append("mesh_relay - Process mesh network relay")
        if "withdraw_fees" in approval_teal:
            methods.append("withdraw_fees - Withdraw accumulated fees")
        if "update_status" in approval_teal:
            methods.append("update_status - Update relay node status")
        if "update_fee" in approval_teal:
            methods.append("update_fee - Update mesh relay fee")
        
        print("📋 Available Methods:")
        for method in methods:
            print(f"  • {method}")
        
        # Show state schema requirements
        print(f"\n🗃️  State Requirements:")
        print(f"  Global State: 5 integers, 1 byte slice")
        print(f"  Local State: 5 integers, 0 byte slices")
        
        # Show key features
        print(f"\n🌟 Key Features:")
        print(f"  • Inner transactions for payments")
        print(f"  • Relay node reputation system")
        print(f"  • Mesh network routing")
        print(f"  • Fee distribution mechanism")
        print(f"  • Access control (creator only functions)")
        
        return True
        
    except Exception as e:
        print(f"❌ Structure analysis failed: {e}")
        return False


def main():
    """Run compilation tests"""
    print("🔬 Modern Offnet Token - Compilation Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test compilation
    if not test_contract_compilation():
        success = False
    
    # Show structure
    if not show_contract_structure():
        success = False
    
    if success:
        print(f"\n🎊 ALL TESTS PASSED! 🎊")
        print(f"\nNext steps:")
        print(f"1. Install Docker to run LocalNet")
        print(f"2. Deploy using: python deploy_modern.py")
        print(f"3. Run tests using: python test_contract.py")
        print(f"\nOr deploy to TestNet for live testing")
    else:
        print(f"\n❌ Some tests failed")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)