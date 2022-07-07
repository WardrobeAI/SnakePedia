import pytest

from brownie import accounts, ERC20, uniswap_v1_part_1 as Exchange


one_ETH = 1 * 1e18


@pytest.fixture
def token():
    return accounts[0].deploy(ERC20, "GCP", "Good Cool Poll", 0, 10000)


@pytest.fixture
def exchange(token):
    return accounts[0].deploy(Exchange, token.address)


def test_add_liquidity(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    assert exchange.balance() == one_ETH
    reserve = exchange.getReserve()
    assert reserve == token_amount


def test_getPrice(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    tokenReserve = exchange.getReserve()
    etherReserve = exchange.balance()

    assert exchange.getPrice(etherReserve, tokenReserve) == (one_ETH / token_amount)
    assert exchange.getPrice(tokenReserve, etherReserve) == (token_amount / one_ETH)


def test_getTokenAmount(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    tokensOut = exchange.getTokenAmount(one_ETH / 1000)
    assert tokensOut == 0.9

    tokensOut = exchange.getTokenAmount(one_ETH / 100)
    assert tokensOut == 9

    tokensOut = exchange.getTokenAmount(one_ETH / 10)
    assert tokensOut == 90

    tokensOut = exchange.getTokenAmount(one_ETH / 2)
    assert tokensOut == 333


def test_getETHAmount(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    ethOut = exchange.getEthAmount(1)
    assert ethOut == 999000999000999 # 0.000999000999000999 ETH

    ethOut = exchange.getEthAmount(10)
    assert ethOut == 9900990099009900 # 0.0099009900990099 ETH

    ethOut = exchange.getEthAmount(100)
    assert ethOut == 90909090909090909 # 0.090909090909090909 ETH

    ethOut = exchange.getEthAmount(500)
    assert ethOut == 333333333333333333 # 0.3333333333333333 ETH


def test_ethToTokenSwap(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    exchange.ethToTokenSwap(1, {"value": 0.0011 * one_ETH, "from": accounts[1]})
    assert token.balanceOf(accounts[1]) == 1

    exchange.ethToTokenSwap(10, {"value": 0.011 * one_ETH, "from": accounts[2]})
    assert token.balanceOf(accounts[2]) == 10

    exchange.ethToTokenSwap(100, {"value": 0.12 * one_ETH, "from": accounts[3]})
    assert token.balanceOf(accounts[3]) == 104


def test_tokenToEthSwap(exchange, token):
    token.approve(exchange, 2000)
    token_amount = 1000
    exchange.addLiquidity(token_amount, { "value": one_ETH })

    token.mint(accounts[1], token_amount)
    token.mint(accounts[2], token_amount)
    token.mint(accounts[3], token_amount)

    initial_balance = accounts[1].balance()
    sold_token = 1
    token.approve(exchange, 2000, {"from": accounts[1]})
    exchange.tokenToEthSwap(sold_token, 0.0001 * one_ETH, {"from": accounts[1]})
    assert token.balanceOf(accounts[1]) == token_amount - sold_token
    assert accounts[1].balance() > initial_balance

    initial_balance = accounts[2].balance()
    sold_token = 10
    token.approve(exchange, 2000, {"from": accounts[2]})
    exchange.tokenToEthSwap(sold_token, 0.0001 * one_ETH, {"from": accounts[2]})
    assert token.balanceOf(accounts[2]) == token_amount - sold_token
    assert accounts[2].balance() > initial_balance
