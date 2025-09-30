"""
Modern Offnet Token Smart Contract using AlgoKit patterns
"""

from pyteal import *
from typing import Final


class OffnetTokenContract:
    """
    Modern implementation of Offnet Token contract with improved patterns
    """
    
    # Global state keys
    TOTAL_SUPPLY: Final[Bytes] = Bytes("total_supply")
    CREATOR: Final[Bytes] = Bytes("creator")
    MESH_FEE: Final[Bytes] = Bytes("mesh_fee")
    RELAY_COUNT: Final[Bytes] = Bytes("relay_count")
    TOKEN_ASSET_ID: Final[Bytes] = Bytes("token_asset_id")
    
    # Local state keys
    RELAY_BALANCE: Final[Bytes] = Bytes("relay_balance")
    RELAY_COUNT_LOCAL: Final[Bytes] = Bytes("relay_count_local")
    IS_ACTIVE_RELAY: Final[Bytes] = Bytes("is_active_relay")
    REPUTATION_SCORE: Final[Bytes] = Bytes("reputation_score")
    LAST_ACTIVITY: Final[Bytes] = Bytes("last_activity")

    @staticmethod
    @Subroutine(TealType.uint64)
    def is_creator() -> Expr:
        """Check if sender is the contract creator"""
        return App.globalGet(OffnetTokenContract.CREATOR) == Txn.sender()

    @staticmethod
    @Subroutine(TealType.uint64)
    def is_valid_relay() -> Expr:
        """Check if sender is a valid active relay"""
        return And(
            App.localGet(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY) == Int(1),
            App.localGet(Txn.sender(), OffnetTokenContract.REPUTATION_SCORE) >= Int(10)
        )

    @staticmethod
    @Subroutine(TealType.uint64)
    def validate_mesh_transaction() -> Expr:
        """Validate mesh network transaction parameters"""
        return And(
            Txn.type_enum() == TxnType.ApplicationCall,
            Txn.application_args.length() >= Int(1),
            Global.group_size() >= Int(1)
        )

    @staticmethod
    def create_application() -> Expr:
        """Initialize contract on creation"""
        return Seq([
            App.globalPut(OffnetTokenContract.TOTAL_SUPPLY, Int(1_000_000)),
            App.globalPut(OffnetTokenContract.CREATOR, Global.creator_address()),
            App.globalPut(OffnetTokenContract.MESH_FEE, Int(1000)),  # 0.001 ALGO
            App.globalPut(OffnetTokenContract.RELAY_COUNT, Int(0)),
            App.globalPut(OffnetTokenContract.TOKEN_ASSET_ID, Int(0)),
            Log(Bytes("Contract created successfully")),
            Return(Int(1))
        ])

    @staticmethod
    def create_token_asset() -> Expr:
        """Create ASA token using inner transactions"""
        return Seq([
            Assert(OffnetTokenContract.is_creator()),
            Assert(App.globalGet(OffnetTokenContract.TOKEN_ASSET_ID) == Int(0)),
            
            # Create ASA inner transaction
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: Int(1_000_000_000_000),  # 1M with 6 decimals
                TxnField.config_asset_decimals: Int(6),
                TxnField.config_asset_unit_name: Bytes("OFFNET"),
                TxnField.config_asset_name: Bytes("Offnet Token"),
                TxnField.config_asset_url: Bytes("https://offnet.app"),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
            }),
            InnerTxnBuilder.Submit(),
            
            # Store asset ID
            App.globalPut(OffnetTokenContract.TOKEN_ASSET_ID, InnerTxn.created_asset_id()),
            Log(Concat(Bytes("Token created with ID: "), Itob(InnerTxn.created_asset_id()))),
            Return(Int(1))
        ])

    @staticmethod
    def opt_in_relay() -> Expr:
        """Opt-in to become a relay node"""
        return Seq([
            # Initialize local state
            App.localPut(Txn.sender(), OffnetTokenContract.RELAY_BALANCE, Int(0)),
            App.localPut(Txn.sender(), OffnetTokenContract.RELAY_COUNT_LOCAL, Int(0)),
            App.localPut(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY, Int(1)),
            App.localPut(Txn.sender(), OffnetTokenContract.REPUTATION_SCORE, Int(50)),
            App.localPut(Txn.sender(), OffnetTokenContract.LAST_ACTIVITY, Global.latest_timestamp()),
            
            # Increment global relay count
            App.globalPut(
                OffnetTokenContract.RELAY_COUNT,
                App.globalGet(OffnetTokenContract.RELAY_COUNT) + Int(1)
            ),
            
            Log(Concat(Bytes("Relay node opted in: "), Txn.sender())),
            Return(Int(1))
        ])

    @staticmethod
    def process_mesh_relay() -> Expr:
        """Process mesh relay transaction with fee distribution"""
        return Seq([
            Assert(OffnetTokenContract.validate_mesh_transaction()),
            Assert(OffnetTokenContract.is_valid_relay()),
            Assert(Txn.application_args.length() >= Int(3)),  # relay_data, destination, hop_count
            
            # Validate hop count
            Assert(Btoi(Txn.application_args[2]) <= Int(10)),  # Max 10 hops
            
            # Update relay statistics
            App.localPut(
                Txn.sender(),
                OffnetTokenContract.RELAY_COUNT_LOCAL,
                App.localGet(Txn.sender(), OffnetTokenContract.RELAY_COUNT_LOCAL) + Int(1)
            ),
            App.localPut(
                Txn.sender(),
                OffnetTokenContract.LAST_ACTIVITY,
                Global.latest_timestamp()
            ),
            
            # Award relay fee
            App.localPut(
                Txn.sender(),
                OffnetTokenContract.RELAY_BALANCE,
                App.localGet(Txn.sender(), OffnetTokenContract.RELAY_BALANCE) + 
                App.globalGet(OffnetTokenContract.MESH_FEE)
            ),
            
            # Improve reputation (max 100)
            App.localPut(
                Txn.sender(),
                OffnetTokenContract.REPUTATION_SCORE,
                If(
                    App.localGet(Txn.sender(), OffnetTokenContract.REPUTATION_SCORE) < Int(100),
                    App.localGet(Txn.sender(), OffnetTokenContract.REPUTATION_SCORE) + Int(1),
                    Int(100)
                )
            ),
            
            Log(Concat(
                Bytes("Mesh relay processed by: "),
                Txn.sender(),
                Bytes(" Fee: "),
                Itob(App.globalGet(OffnetTokenContract.MESH_FEE))
            )),
            Return(Int(1))
        ])

    @staticmethod
    def withdraw_relay_fees() -> Expr:
        """Withdraw accumulated relay fees using inner transactions"""
        accumulated_fees = App.localGet(Txn.sender(), OffnetTokenContract.RELAY_BALANCE)
        
        return Seq([
            Assert(accumulated_fees > Int(0)),
            Assert(App.localGet(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY) == Int(1)),
            
            # Reset relay balance
            App.localPut(Txn.sender(), OffnetTokenContract.RELAY_BALANCE, Int(0)),
            
            # Send payment using inner transaction
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                TxnField.type_enum: TxnType.Payment,
                TxnField.receiver: Txn.sender(),
                TxnField.amount: accumulated_fees,
                TxnField.fee: Int(0),  # Parent covers fee
            }),
            InnerTxnBuilder.Submit(),
            
            Log(Concat(
                Bytes("Fees withdrawn: "),
                Itob(accumulated_fees),
                Bytes(" to: "),
                Txn.sender()
            )),
            Return(Int(1))
        ])

    @staticmethod
    def update_relay_status() -> Expr:
        """Update relay node status"""
        return Seq([
            Assert(Txn.application_args.length() >= Int(2)),
            
            If(Btoi(Txn.application_args[1]) == Int(1))
            .Then(
                Seq([
                    # Activate relay
                    If(App.localGet(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY) == Int(0))
                    .Then(
                        Seq([
                            App.localPut(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY, Int(1)),
                            App.globalPut(
                                OffnetTokenContract.RELAY_COUNT,
                                App.globalGet(OffnetTokenContract.RELAY_COUNT) + Int(1)
                            ),
                        ])
                    ),
                ])
            )
            .Else(
                Seq([
                    # Deactivate relay
                    If(App.localGet(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY) == Int(1))
                    .Then(
                        Seq([
                            App.localPut(Txn.sender(), OffnetTokenContract.IS_ACTIVE_RELAY, Int(0)),
                            App.globalPut(
                                OffnetTokenContract.RELAY_COUNT,
                                App.globalGet(OffnetTokenContract.RELAY_COUNT) - Int(1)
                            ),
                        ])
                    ),
                ])
            ),
            
            Return(Int(1))
        ])

    @staticmethod
    def update_mesh_fee() -> Expr:
        """Update mesh relay fee (creator only)"""
        return Seq([
            Assert(OffnetTokenContract.is_creator()),
            Assert(Txn.application_args.length() >= Int(2)),
            Assert(Btoi(Txn.application_args[1]) <= Int(10_000)),  # Max 0.01 ALGO
            Assert(Btoi(Txn.application_args[1]) >= Int(100)),     # Min 0.0001 ALGO
            
            App.globalPut(OffnetTokenContract.MESH_FEE, Btoi(Txn.application_args[1])),
            Log(Concat(Bytes("Mesh fee updated to: "), Txn.application_args[1])),
            Return(Int(1))
        ])

    @staticmethod
    def approval_program() -> Expr:
        """Main approval program logic"""
        return Cond(
            # Application creation
            [Txn.application_id() == Int(0), OffnetTokenContract.create_application()],
            
            # Handle different OnComplete types
            [Txn.on_completion() == OnComplete.OptIn, OffnetTokenContract.opt_in_relay()],
            [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))],
            [Txn.on_completion() == OnComplete.UpdateApplication, Return(OffnetTokenContract.is_creator())],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(OffnetTokenContract.is_creator())],
            
            # NoOp calls with method routing
            [
                And(
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.application_args[0] == Bytes("create_token")
                ),
                OffnetTokenContract.create_token_asset()
            ],
            [
                And(
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.application_args[0] == Bytes("mesh_relay")
                ),
                OffnetTokenContract.process_mesh_relay()
            ],
            [
                And(
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.application_args[0] == Bytes("withdraw_fees")
                ),
                OffnetTokenContract.withdraw_relay_fees()
            ],
            [
                And(
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.application_args[0] == Bytes("update_status")
                ),
                OffnetTokenContract.update_relay_status()
            ],
            [
                And(
                    Txn.on_completion() == OnComplete.NoOp,
                    Txn.application_args[0] == Bytes("update_fee")
                ),
                OffnetTokenContract.update_mesh_fee()
            ]
        )

    @staticmethod
    def clear_state_program() -> Expr:
        """Clear state program (always approve)"""
        return Return(Int(1))


def approval_program():
    """Entry point for approval program"""
    return OffnetTokenContract.approval_program()


def clear_state_program():
    """Entry point for clear state program"""
    return OffnetTokenContract.clear_state_program()


if __name__ == "__main__":
    # Compile and output TEAL
    print("=== APPROVAL PROGRAM ===")
    print(compileTeal(approval_program(), Mode.Application, version=8))
    print("\n=== CLEAR STATE PROGRAM ===")
    print(compileTeal(clear_state_program(), Mode.Application, version=8))