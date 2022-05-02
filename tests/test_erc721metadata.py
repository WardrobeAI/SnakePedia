import pytest

from brownie import accounts, ERC721Metadata


@pytest.fixture
def nft():
    return accounts[0].deploy(ERC721Metadata, "Milady", "MLD", "ipfs://yadda_yadda/")


def test_init(nft):
    assert nft.name() == "Milady"
    assert nft.symbol() == "MLD"
    assert nft.baseURI() == "ipfs://yadda_yadda/"


def test_tokenURI(nft):
    assert nft.tokenURI(3) == "ipfs://yadda_yadda/3"
    assert nft.tokenURI(88) == "ipfs://yadda_yadda/88"