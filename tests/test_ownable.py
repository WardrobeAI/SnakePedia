import pytest

from brownie import accounts, Ownable
import brownie


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture
def ownable():
    return accounts[0].deploy(Ownable)


def test_init(ownable):
    assert ownable.owner() == accounts[0]


def test_transfer_ownership_and_only_owner(ownable):
    assert ownable.owner() == accounts[0]
    with brownie.reverts():
        ownable.transferOwnership(ZERO_ADDRESS)
    txn = ownable.transferOwnership(accounts[1])

    event = txn.events["OwnershipTransferred"]
    assert event["previousOwner"] == accounts[0]
    assert event["newOwner"] == accounts[1]

    assert ownable.owner() == accounts[1]
    with brownie.reverts():
        ownable.transferOwnership(accounts[0])


def test_renounce_ownership(ownable):
    assert ownable.owner() == accounts[0]
    txn = ownable.renounceOwnership()

    event = txn.events["OwnershipTransferred"]
    assert event["previousOwner"] == accounts[0]
    assert event["newOwner"] == ZERO_ADDRESS

    assert ownable.owner() == ZERO_ADDRESS