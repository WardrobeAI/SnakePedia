# @version ^0.3.2
# @dev Implementation of PiggyBank.
# Based on https://www.youtube.com/watch?v=Geio70-SfSE
# @author Arjuna Sky Kok (@arjunaskykok)


owner: public(address)


# @dev This emits when people deposits ETH into this smart contract.
# @param amount the amount ETH deposited.
event Deposit:
    amount: uint256


# @dev This emits when owner withdraws ETH from this smart contract.
# @param amount the amount ETH withdrawed.
event Withdraw:
    amount: uint256


# @dev Initialize the owner when deploying the smart contract.
@external
def __init__():
    self.owner = msg.sender


# @dev The method to receive ETH.
@external
@payable
def receive():
    log Deposit(msg.value)


# @dev The method to withdraw ETH.
@external
def withdraw():
    assert msg.sender == self.owner, "not owner"
    log Withdraw(self.balance)
    selfdestruct(self.owner)
