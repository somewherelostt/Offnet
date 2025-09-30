# Offnet Token Smart Contract for Algorand
# This contract implements a custom ASA (Algorand Standard Asset) with mesh relay functionality

from pyteal import *

def offnet_token_contract():
    """
    Offnet Token ASA smart contract with mesh relay capabilities
    Features:
    - Token creation and management
    - Mesh relay fee distribution
    - Transaction validation for offline broadcasts
    """
    
    # Global state keys
    total_supply_key = Bytes("total_supply")
    creator_key = Bytes("creator")
    mesh_fee_key = Bytes("mesh_fee")
    relay_count_key = Bytes("relay_count")
    
    # Local state keys for relay nodes
    relay_balance_key = Bytes("relay_balance")
    relay_count_local_key = Bytes("relay_count_local")
    is_active_relay_key = Bytes("is_active_relay")
    
    @Subroutine(TealType.uint64)
    def is_creator():
        """Check if sender is the contract creator"""
        return Global.creator_address() == Txn.sender()
    
    @Subroutine(TealType.uint64)
    def validate_mesh_transaction():
        """Validate mesh network transaction parameters"""
        return And(
            Txn.type_enum() == TxnType.ApplicationCall,
            Txn.application_args.length() >= Int(3),  # Minimum required args
            Global.group_size() == Int(1)  # Single transaction for mesh relay
        )
    
    # Initialize contract
    on_creation = Seq([
        App.globalPut(total_supply_key, Int(1000000)),  # 1M tokens
        App.globalPut(creator_key, Global.creator_address()),
        App.globalPut(mesh_fee_key, Int(1000)),  # 0.001 ALGO mesh fee
        App.globalPut(relay_count_key, Int(0)),
        Return(Int(1))
    ])
    
    # Opt-in for relay nodes
    on_opt_in = Seq([
        App.localPut(Txn.sender(), relay_balance_key, Int(0)),
        App.localPut(Txn.sender(), relay_count_local_key, Int(0)),
        App.localPut(Txn.sender(), is_active_relay_key, Int(1)),
        App.globalPut(relay_count_key, App.globalGet(relay_count_key) + Int(1)),
        Return(Int(1))
    ])
    
    # Handle mesh relay transactions
    handle_mesh_relay = Seq([
        Assert(validate_mesh_transaction()),
        Assert(App.localGet(Txn.sender(), is_active_relay_key) == Int(1)),
        
        # Award relay fee to the relay node
        App.localPut(
            Txn.sender(), 
            relay_balance_key, 
            App.localGet(Txn.sender(), relay_balance_key) + App.globalGet(mesh_fee_key)
        ),
        
        # Increment relay count
        App.localPut(
            Txn.sender(),
            relay_count_local_key,
            App.localGet(Txn.sender(), relay_count_local_key) + Int(1)
        ),
        
        Return(Int(1))
    ])
    
    # Handle token minting (creator only)
    handle_mint = Seq([
        Assert(is_creator()),
        Assert(Txn.application_args.length() == Int(2)),
        
        # Mint logic would go here
        # For simplicity, we'll just return success
        Return(Int(1))
    ])
    
    # Handle relay node status updates
    handle_relay_status = Seq([
        Assert(App.localGet(Txn.sender(), is_active_relay_key) == Int(1)),
        
        # Toggle relay status based on application argument
        If(Btoi(Txn.application_args[1]) == Int(0)).Then(
            Seq([
                App.localPut(Txn.sender(), is_active_relay_key, Int(0)),
                App.globalPut(relay_count_key, App.globalGet(relay_count_key) - Int(1))
            ])
        ).Else(
            Seq([
                App.localPut(Txn.sender(), is_active_relay_key, Int(1)),
                App.globalPut(relay_count_key, App.globalGet(relay_count_key) + Int(1))
            ])
        ),
        
        Return(Int(1))
    ])
    
    # Handle fee withdrawal for relay nodes
    handle_withdraw_fees = Seq([
        Assert(App.localGet(Txn.sender(), relay_balance_key) > Int(0)),
        
        # Logic to send accumulated fees to relay node
        # This would require an inner transaction in a full implementation
        App.localPut(Txn.sender(), relay_balance_key, Int(0)),
        
        Return(Int(1))
    ])
    
    # Main application call router
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnCall.OptIn, on_opt_in],
        [Txn.on_completion() == OnCall.CloseOut, Return(Int(1))],
        [Txn.on_completion() == OnCall.UpdateApplication, Return(is_creator())],
        [Txn.on_completion() == OnCall.DeleteApplication, Return(is_creator())],
        [
            And(
                Txn.on_completion() == OnCall.NoOp,
                Txn.application_args[0] == Bytes("mesh_relay")
            ),
            handle_mesh_relay
        ],
        [
            And(
                Txn.on_completion() == OnCall.NoOp,
                Txn.application_args[0] == Bytes("mint")
            ),
            handle_mint
        ],
        [
            And(
                Txn.on_completion() == OnCall.NoOp,
                Txn.application_args[0] == Bytes("relay_status")
            ),
            handle_relay_status
        ],
        [
            And(
                Txn.on_completion() == OnCall.NoOp,
                Txn.application_args[0] == Bytes("withdraw_fees")
            ),
            handle_withdraw_fees
        ]
    )
    
    return program

def clear_state_program():
    """Clear state program (always approve)"""
    return Return(Int(1))

if __name__ == "__main__":
    # Compile the contract
    approval_program = offnet_token_contract()
    clear_program = clear_state_program()
    
    # Output TEAL code
    print("=== APPROVAL PROGRAM ===")
    print(compileTeal(approval_program, Mode.Application, version=6))
    print("\n=== CLEAR STATE PROGRAM ===")
    print(compileTeal(clear_program, Mode.Application, version=6))