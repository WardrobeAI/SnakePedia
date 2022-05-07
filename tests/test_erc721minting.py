import pytest

from brownie import accounts, ERC721Minting
import brownie


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
price = 3 * 10 ** 16

@pytest.fixture
def nft():
    return accounts[0].deploy(ERC721Minting, 5, price)


def test_mint(nft):
    assert nft.balanceOf(accounts[0]) == 0
    nft.mint(accounts[0], {"value": "0.03 ether"})
    assert nft.balanceOf(accounts[0]) == 1
    assert nft.ownerOf(0) == accounts[0]
    nft.mint(accounts[0], {"value": "0.03 ether"})
    assert nft.balanceOf(accounts[0]) == 2
    assert nft.ownerOf(0) == accounts[0]
    assert nft.ownerOf(1) == accounts[0]
    nft.mint(accounts[1], {"value": "0.03 ether"})
    assert nft.balanceOf(accounts[0]) == 2
    assert nft.balanceOf(accounts[1]) == 1
    assert nft.ownerOf(0) == accounts[0]
    assert nft.ownerOf(1) == accounts[0]
    assert nft.ownerOf(2) == accounts[1]
    with brownie.reverts():
        nft.mint(accounts[1], {"value": "0.01 ether"})


def test_mint_fail_maximum_nfts(nft):
    for i in range(5):
        nft.mint(accounts[0], {"value": "0.03 ether"})
    with brownie.reverts():
        nft.mint(accounts[0], {"value": "0.03 ether"})