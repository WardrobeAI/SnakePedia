import pytest

from brownie import accounts, ERC20, Vault


@pytest.fixture
def token():
    return accounts[0].deploy(ERC20, "GCP", "Good Cool Poll", 0, 10000)


@pytest.fixture
def vault(token):
    return accounts[0].deploy(Vault, token.address)


def test_init(vault, token):
    assert vault.token() == token.address


def test_deposit(vault, token):
    token.approve(vault.address, 10000)
    vault.deposit(1000)
    assert vault.balanceOf(accounts[0]) == 1000
    assert vault.totalSupply() == 1000
    assert token.balanceOf(accounts[0]) == 9000
    assert token.balanceOf(vault.address) == 1000
    vault.deposit(1000)
    assert vault.balanceOf(accounts[0]) == 2000
    assert vault.totalSupply() == 2000
    assert token.balanceOf(accounts[0]) == 8000
    assert token.balanceOf(vault.address) == 2000

    token.mint(accounts[1], 2000)
    token.approve(vault.address, 2000, {"from": accounts[1]})
    assert token.balanceOf(accounts[1]) == 2000
    vault.deposit(1000, {"from": accounts[1]})
    assert vault.balanceOf(accounts[0]) == 2000
    assert vault.balanceOf(accounts[1]) == 1000
    assert vault.totalSupply() == 3000
    assert token.balanceOf(accounts[1]) == 1000
    assert token.balanceOf(vault.address) == 3000


def test_withdraw(vault, token):
    token.approve(vault.address, 10000)
    vault.deposit(2000)
    assert vault.balanceOf(accounts[0]) == 2000
    assert vault.totalSupply() == 2000
    assert token.balanceOf(accounts[0]) == 8000
    assert token.balanceOf(vault.address) == 2000
    vault.withdraw(1000)
    assert vault.balanceOf(accounts[0]) == 1000
    assert vault.totalSupply() == 1000
    assert token.balanceOf(accounts[0]) == 9000
    assert token.balanceOf(vault.address) == 1000
