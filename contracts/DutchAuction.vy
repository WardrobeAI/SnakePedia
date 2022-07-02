# @version ^0.3.3
# @dev Implementation of Ducth Auction.
# @author Arjuna Sky Kok (@arjunaskykok)
# Based on https://solidity-by-example.org/app/dutch-auction/

from vyper.interfaces import ERC721 as IERC721


interface DutchAuction:
    def getPrice() -> uint256: view


DURATION: constant(uint256) = 7 * 24 * 3600 # 7 days

nft: public(IERC721)

seller: public(address)

startingPrice: public(uint256)

startAt: public(uint256)

expiresAt: public(uint256)

discountRate: public(uint256)

@external
def __init__(_startingPrice: uint256,
             _discountRate: uint256,
             _nft: address):
    assert _startingPrice >= _discountRate * DURATION, "Starting price is too low"

    self.seller = msg.sender
    self.startingPrice = _startingPrice
    self.startAt = block.timestamp
    self.expiresAt = block.timestamp + DURATION
    self.discountRate = _discountRate

    self.nft = IERC721(_nft)

@external
@view
def getPrice() -> uint256:
    timeElapsed: uint256 = block.timestamp - self.startAt
    discount: uint256 = self.discountRate * timeElapsed
    return self.startingPrice - discount


@external
@payable
def buy(nftId: uint256):
    assert block.timestamp < self.expiresAt, "Auction has expired"

    price: uint256 = DutchAuction(self).getPrice()
    assert msg.value >= price, "Not enough ETH"

    self.nft.transferFrom(self.seller, msg.sender, nftId)
    refund: uint256 = msg.value - price
    if refund > 0:
        send(msg.sender, refund)
    selfdestruct(self.seller)
