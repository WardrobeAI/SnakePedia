import pytest

from brownie import accounts, PiggyBank
import brownie


@pytest.fixture
def piggy_bank():
    return accounts[0].deploy(PiggyBank)


def test_receive_and_withdraw(piggy_bank):
    initial_balance = accounts[0].balance()
    piggy_bank.receive({"value": "1 ether", "from": accounts[1]})
    piggy_bank.receive({"value": "1 ether", "from": accounts[2]})
    piggy_bank.withdraw({"from": accounts[0]})
    assert accounts[0].balance() == initial_balance + 2 * 1e18


def test_cannot_withdraw(piggy_bank):
    with brownie.reverts():
        piggy_bank.withdraw({"from": accounts[1]})


# TODO: Add test checking wether the smart contract has been destroyed or not
