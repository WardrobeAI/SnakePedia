# @version ^0.3.3
# @dev Implementation of Uniswap V1 part 2 and implementation of ERC-20 token standard.
# @author Arjuna Sky Kok (@arjunaskykok)
# @author Takayuki Jimba (@yudetamago)
# Based on https://jeiwan.net/posts/programming-defi-uniswap-2/


from vyper.interfaces import ERC20 as IERC20


implements: IERC20


interface Exchange:
    def getReserve() -> uint256: view
    def getAmount(inputAmount: uint256,
                  inputReserve: uint256,
                  outputReserve: uint256) -> uint256: view


interface Token:
    def mint(_to: address, _value: uint256): nonpayable


event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

name: public(String[32])
symbol: public(String[32])
decimals: public(uint8)

balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])
totalSupply: public(uint256)
minter: address


tokenAddress: public(address)


@external
def __init__(_token: address):
    assert _token != ZERO_ADDRESS, "invalid token address"

    self.tokenAddress = _token

    # ERC-20
    init_supply: uint256 = 0
    self.name = "Uniswap"
    self.symbol = "UNI"
    self.decimals = 18
    self.balanceOf[msg.sender] = init_supply
    self.totalSupply = init_supply
    self.minter = msg.sender


# ERC-20


@external
def transfer(_to : address, _value : uint256) -> bool:
    """
    @dev Transfer token for a specified address
    @param _to The address to transfer to.
    @param _value The amount to be transferred.
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def _transferFrom(_from : address, _to : address, _value : uint256, msg_sender: address) -> bool:
    """
     @dev Transfer tokens from one address to another.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    # NOTE: vyper does not allow underflows
    #      so the following subtraction would revert on insufficient allowance
    self.allowance[_from][msg_sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    """
     @dev Transfer tokens from one address to another.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    # NOTE: vyper does not allow underflows
    #      so the following subtraction would revert on insufficient allowance
    self.allowance[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    """
    @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
         Beware that changing an allowance with this method brings the risk that someone may use both the old
         and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
         race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
         https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    @param _spender The address which will spend the funds.
    @param _value The amount of tokens to be spent.
    """
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def mint(_to: address, _value: uint256):
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert msg.sender == self.minter
    assert _to != ZERO_ADDRESS
    self.totalSupply += _value
    self.balanceOf[_to] += _value
    log Transfer(ZERO_ADDRESS, _to, _value)


@internal
def _mint(_to: address, _value: uint256):
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted. For internal purpose.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert _to != ZERO_ADDRESS
    self.totalSupply += _value
    self.balanceOf[_to] += _value
    log Transfer(ZERO_ADDRESS, _to, _value)


@internal
def _burn(_to: address, _value: uint256):
    """
    @dev Internal function that burns an amount of the token of a given
         account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert _to != ZERO_ADDRESS
    self.totalSupply -= _value
    self.balanceOf[_to] -= _value
    log Transfer(_to, ZERO_ADDRESS, _value)


@external
def burn(_value: uint256):
    """
    @dev Burn an amount of the token of msg.sender.
    @param _value The amount that will be burned.
    """
    self._burn(msg.sender, _value)


@external
def burnFrom(_to: address, _value: uint256):
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    self.allowance[_to][msg.sender] -= _value
    self._burn(_to, _value)


# Exchange


@external
@view
def getReserve() -> uint256:
    return IERC20(self.tokenAddress).balanceOf(self)


@external
@view
def getAmount(inputAmount: uint256, inputReserve: uint256, outputReserve: uint256) -> uint256:
    assert inputReserve > 0 and outputReserve > 0, "invalid reserve"

    inputAmountWithFee: uint256 = inputAmount * 99 # fee is 1%
    numerator: uint256 = inputAmountWithFee * outputReserve
    denominator: uint256 = (inputReserve * 100) + inputAmountWithFee

    return numerator / denominator


@external
@payable
def addLiquidity(_tokenAmount: uint256) -> uint256:
    tokenReserve : uint256 = Exchange(self).getReserve()
    if tokenReserve == 0:
        token: IERC20 = IERC20(self.tokenAddress)
        token.transferFrom(msg.sender, self, _tokenAmount)

        liquidity: uint256 = self.balance
        self._mint(msg.sender, liquidity)

        return liquidity
    else:
        ethReserve: uint256 = self.balance - msg.value
        tokenAmount: uint256 = (msg.value * tokenReserve) / ethReserve

        assert _tokenAmount >= tokenAmount, "insufficient token amount"

        token: IERC20 = IERC20(self.tokenAddress)
        token.transferFrom(msg.sender, self, tokenAmount)

        liquidity: uint256 = (msg.value * self.totalSupply) / ethReserve
        self._mint(msg.sender, liquidity)

        return liquidity


@external
@payable
def removeLiquidity(_amount: uint256) -> (uint256, uint256):
    assert _amount > 0, "invalid amount"

    ethAmount: uint256 = (self.balance * _amount) / self.totalSupply
    tokenAmount: uint256 = (Exchange(self).getReserve() * _amount) / self.totalSupply

    self._burn(msg.sender, _amount)
    send(msg.sender, ethAmount)
    IERC20(self.tokenAddress).transfer(msg.sender, tokenAmount)

    return (ethAmount, tokenAmount)


@external
@view
def getTokenAmount(_ethSold: uint256) -> uint256:
    assert _ethSold > 0, "ethSold is too small"

    tokenReserve: uint256 = Exchange(self).getReserve()

    return Exchange(self).getAmount(_ethSold, self.balance, tokenReserve)


@external
@view
def getEthAmount(_tokenSold: uint256) -> uint256:
    assert _tokenSold > 0, "ethSold is too small"

    tokenReserve: uint256 = Exchange(self).getReserve()

    return Exchange(self).getAmount(_tokenSold, tokenReserve, self.balance)


@external
@payable
def ethToTokenSwap(_minTokens: uint256):
    tokenReserve: uint256 = Exchange(self).getReserve()
    tokensBought: uint256 = Exchange(self).getAmount(msg.value, self.balance - msg.value, tokenReserve)

    assert tokensBought >= _minTokens, "insufficient output amount"

    IERC20(self.tokenAddress).transfer(msg.sender, tokensBought)


@external
@payable
def tokenToEthSwap(_tokensSold: uint256, _minEth: uint256):
    tokenReserve: uint256 = Exchange(self).getReserve()
    ethBought: uint256 = Exchange(self).getAmount(_tokensSold, tokenReserve, self.balance)

    assert ethBought >= _minEth, "Insufficient output amount"

    IERC20(self.tokenAddress).transferFrom(msg.sender, self, _tokensSold)
    send(msg.sender, ethBought)
