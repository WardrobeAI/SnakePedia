# @version ^0.3.2
# @dev Implementation of Vault.
# @author Arjuna Sky Kok (@arjunaskykok)
# Based on https://solidity-by-example.org/defi/vault


from vyper.interfaces import ERC20 as IERC20


token: public(IERC20)
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])


@external
def __init__(_token: address):
    """
     @dev Initialize the vault.
     @param _token the ERC-20 token that the vault accepts.
    """
    self.token = IERC20(_token)


@internal
def _mint(_to: address, _shares: uint256):
    """
     @dev Mint the shares.
     @param _to the address that will accept the new shares.
     @param _shares number of shares that will be printed.
    """
    self.totalSupply += _shares
    self.balanceOf[_to] += _shares


@internal
def _burn(_from: address, _shares: uint256):
    """
     @dev Burn the shares.
     @param _from the address that will lose the shares.
     @param _shares number of shares that will be burnt.
    """
    self.totalSupply -= _shares
    self.balanceOf[_from] -= _shares


@external
def deposit(_amount: uint256):
    """
     @dev Deposit the ERC-20 token to the vault.
     @param _amount amount of ERC-20 token to be stored to the vault.
    """
    shares: uint256 = 0
    if self.totalSupply == 0:
        shares = _amount
    else:
        shares = (_amount * self.totalSupply) / self.token.balanceOf(self)

    self._mint(msg.sender, shares)
    self.token.transferFrom(msg.sender, self, _amount)


@external
def withdraw(_shares: uint256):
    """
     @dev Withdraw the ERC-20 token from the vault.
     @param _shares amount of the shares that will be burnt.
    """
    amount: uint256 = (_shares * self.token.balanceOf(self)) / self.totalSupply
    self._burn(msg.sender, _shares)
    self.token.transfer(msg.sender, amount)
