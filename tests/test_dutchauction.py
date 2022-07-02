import pytest

from brownie import accounts, ERC721, DutchAuction


one_ETH = 1 * 1e18
discount_rate = 0.001


@pytest.fixture
def nft():
    return accounts[0].deploy(ERC721, "Tubby Cats", "TUBBY", "ipfs://tubby-cats-home/", 0)


@pytest.fixture
def dutch_auction(nft):
    return accounts[0].deploy(DutchAuction, one_ETH, discount_rate, nft.address)


def test_init(dutch_auction):
    assert dutch_auction.seller() == accounts[0]


def test_getPrice(dutch_auction, chain):
    assert dutch_auction.getPrice() == one_ETH
    # todo: implements time travel and test the price


def test_buy(nft, dutch_auction):
    assert nft.balanceOf(accounts[1]) == 0
    nft.mint(accounts[0])
    nft.approve(dutch_auction.address, 0)
    dutch_auction.buy(0, {"value": "1 ether", "from": accounts[1]})
    assert nft.balanceOf(accounts[1]) == 1
