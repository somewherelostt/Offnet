"""
Offnet Token Smart Contract - Modern Algorand Python Implementation
A mesh network token system with relay functionality and fee distribution.
"""

from algopy import (
    ARC4Contract,
    GlobalState,
    LocalState,
    Txn,
    Global,
    subroutine,
    UInt64,
    Account,
    Asset,
    Application,
    Bytes,
    log,
)
from algopy import arc4, itxn


class OffnetToken(ARC4Contract):
    """
    Offnet Token contract implementing mesh relay functionality with modern Algorand Python.
    
    Features:
    - Mesh relay fee distribution
    - Relay node reputation system
    - Secure token operations
    - Inner transactions for payments
    """

    def __init__(self) -> None:
        """Initialize the contract with default values."""
        # Global state - contract-wide settings
        self.total_supply = GlobalState(UInt64(1_000_000))  # 1M tokens
        self.mesh_fee = GlobalState(UInt64(1000))  # 0.001 ALGO in microAlgos
        self.relay_count = GlobalState(UInt64(0))
        self.creator = GlobalState(Account(Global.creator_address))
        self.token_asset_id = GlobalState(UInt64(0))  # Will be set when ASA is created
        
        # Local state - per-account data
        self.relay_balance = LocalState(UInt64)  # Accumulated fees for relay node
        self.relay_count_local = LocalState(UInt64)  # Number of relays performed
        self.is_active_relay = LocalState(bool)  # Whether account is active relay
        self.reputation_score = LocalState(UInt64)  # Relay node reputation (0-100)
        self.last_activity = LocalState(UInt64)  # Last relay timestamp

    @arc4.abimethod(create="require")
    def create_application(self) -> None:
        """
        Initialize the application when created.
        This method is called when the application is first deployed.
        """
        # Initialize global state
        self.total_supply.value = UInt64(1_000_000)
        self.mesh_fee.value = UInt64(1000)  # 0.001 ALGO
        self.relay_count.value = UInt64(0)
        self.creator.value = Global.creator_address
        
        log("Offnet Token contract created successfully")

    @arc4.abimethod
    def create_token_asset(
        self,
        unit_name: arc4.String,
        asset_name: arc4.String,
        total: arc4.UInt64,
        decimals: arc4.UInt32,
        url: arc4.String,
    ) -> arc4.UInt64:
        """
        Create the Offnet ASA token using inner transactions.
        Only the creator can call this method.
        
        Args:
            unit_name: Short name for the token (e.g., "OFFNET")
            asset_name: Full name for the token
            total: Total supply of tokens
            decimals: Number of decimal places
            url: Asset URL for metadata
            
        Returns:
            The created asset ID
        """
        # Verify sender is creator
        assert Txn.sender == self.creator.value, "Only creator can create token"
        assert self.token_asset_id.value == 0, "Token already created"
        
        # Create ASA using inner transaction
        itxn.AssetConfig(
            config_asset_total=total.native,
            config_asset_decimals=decimals.native,
            config_asset_unit_name=unit_name.native,
            config_asset_name=asset_name.native,
            config_asset_url=url.native,
            config_asset_manager=Global.current_application_address,
            config_asset_reserve=Global.current_application_address,
            config_asset_freeze=Global.current_application_address,
            config_asset_clawback=Global.current_application_address,
        ).submit()
        
        # Store the created asset ID
        asset_id = itxn.AssetConfig.created_asset_id
        self.token_asset_id.value = asset_id
        
        log(f"Token asset created with ID: {asset_id}")
        return arc4.UInt64(asset_id)

    @arc4.abimethod
    def opt_in_relay(self) -> None:
        """
        Opt-in to become a relay node.
        Initializes local state for the calling account.
        """
        # Initialize local state for new relay node
        self.relay_balance[Txn.sender] = UInt64(0)
        self.relay_count_local[Txn.sender] = UInt64(0)
        self.is_active_relay[Txn.sender] = True
        self.reputation_score[Txn.sender] = UInt64(50)  # Start with neutral reputation
        self.last_activity[Txn.sender] = Global.latest_timestamp
        
        # Increment global relay count
        self.relay_count.value += 1
        
        log(f"Relay node {Txn.sender} opted in successfully")

    @arc4.abimethod
    def process_mesh_relay(
        self,
        relay_data: arc4.String,
        destination: arc4.Address,
        hop_count: arc4.UInt64,
    ) -> arc4.String:
        """
        Process a mesh network relay transaction.
        
        Args:
            relay_data: The data being relayed through the mesh
            destination: Final destination address
            hop_count: Number of hops in the relay chain
            
        Returns:
            Success message with relay confirmation
        """
        # Verify sender is an active relay node
        assert self.is_active_relay[Txn.sender], "Sender is not an active relay node"
        assert hop_count.native <= 10, "Too many hops in relay chain"
        
        # Update relay statistics
        self.relay_count_local[Txn.sender] += 1
        self.last_activity[Txn.sender] = Global.latest_timestamp
        
        # Award relay fee to the relay node
        relay_fee = self.mesh_fee.value
        self.relay_balance[Txn.sender] += relay_fee
        
        # Improve reputation for successful relay (max 100)
        current_reputation = self.reputation_score[Txn.sender]
        if current_reputation < 100:
            self.reputation_score[Txn.sender] = min(current_reputation + 1, UInt64(100))
        
        log(f"Mesh relay processed by {Txn.sender}, fee: {relay_fee}")
        return arc4.String(f"Relay processed successfully, hop: {hop_count}")

    @arc4.abimethod
    def withdraw_relay_fees(self) -> None:
        """
        Allow relay nodes to withdraw their accumulated fees.
        Uses inner transactions to send actual ALGO payments.
        """
        accumulated_fees = self.relay_balance[Txn.sender]
        assert accumulated_fees > 0, "No fees to withdraw"
        assert self.is_active_relay[Txn.sender], "Not an active relay node"
        
        # Reset the relay balance
        self.relay_balance[Txn.sender] = UInt64(0)
        
        # Send payment using inner transaction
        itxn.Payment(
            receiver=Txn.sender,
            amount=accumulated_fees,
            fee=0,  # Parent transaction covers the fee
        ).submit()
        
        log(f"Relay fees withdrawn: {accumulated_fees} to {Txn.sender}")

    @arc4.abimethod
    def update_relay_status(self, active: arc4.Bool) -> None:
        """
        Toggle relay node active status.
        
        Args:
            active: Whether to activate or deactivate the relay node
        """
        current_status = self.is_active_relay[Txn.sender]
        
        if active.native and not current_status:
            # Activating relay node
            self.is_active_relay[Txn.sender] = True
            self.relay_count.value += 1
            log(f"Relay node {Txn.sender} activated")
            
        elif not active.native and current_status:
            # Deactivating relay node
            self.is_active_relay[Txn.sender] = False
            self.relay_count.value -= 1
            log(f"Relay node {Txn.sender} deactivated")

    @arc4.abimethod
    def get_relay_info(self, relay_address: arc4.Address) -> arc4.Tuple[
        arc4.UInt64,  # relay_balance
        arc4.UInt64,  # relay_count
        arc4.Bool,    # is_active
        arc4.UInt64,  # reputation_score
        arc4.UInt64,  # last_activity
    ]:
        """
        Get information about a relay node.
        
        Args:
            relay_address: The address of the relay node to query
            
        Returns:
            Tuple containing relay node information
        """
        address = relay_address.native
        return arc4.Tuple((
            arc4.UInt64(self.relay_balance[address]),
            arc4.UInt64(self.relay_count_local[address]),
            arc4.Bool(self.is_active_relay[address]),
            arc4.UInt64(self.reputation_score[address]),
            arc4.UInt64(self.last_activity[address]),
        ))

    @arc4.abimethod
    def get_contract_info(self) -> arc4.Tuple[
        arc4.UInt64,  # total_supply
        arc4.UInt64,  # mesh_fee
        arc4.UInt64,  # relay_count
        arc4.UInt64,  # token_asset_id
    ]:
        """
        Get general contract information.
        
        Returns:
            Tuple containing contract state information
        """
        return arc4.Tuple((
            arc4.UInt64(self.total_supply.value),
            arc4.UInt64(self.mesh_fee.value),
            arc4.UInt64(self.relay_count.value),
            arc4.UInt64(self.token_asset_id.value),
        ))

    @arc4.abimethod
    def update_mesh_fee(self, new_fee: arc4.UInt64) -> None:
        """
        Update the mesh relay fee (creator only).
        
        Args:
            new_fee: New fee amount in microAlgos
        """
        assert Txn.sender == self.creator.value, "Only creator can update fee"
        assert new_fee.native <= 10_000, "Fee cannot exceed 0.01 ALGO"
        assert new_fee.native >= 100, "Fee cannot be less than 0.0001 ALGO"
        
        old_fee = self.mesh_fee.value
        self.mesh_fee.value = new_fee.native
        
        log(f"Mesh fee updated from {old_fee} to {new_fee.native}")

    @subroutine
    def _validate_relay_node(self, address: Account) -> bool:
        """
        Internal function to validate if an address is a valid relay node.
        
        Args:
            address: The address to validate
            
        Returns:
            True if valid relay node, False otherwise
        """
        return (
            self.is_active_relay[address] and 
            self.reputation_score[address] >= 10  # Minimum reputation required
        )