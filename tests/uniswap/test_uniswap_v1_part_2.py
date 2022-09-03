# Based on https://github.com/Jeiwan/zuniswap/blob/part_2/test/Exchange.test.js
import pytest

from brownie import accounts, ERC20, uniswap_v1_part_2 as Exchange
import brownie


@pytest.fixture
def token():
    return accounts[0].deploy(ERC20, "GCP", "Good Cool Poll", 0, 10000)


@pytest.fixture
def exchange(token):
    deployed_exchange = accounts[0].deploy(Exchange, token.address)
    token.approve(deployed_exchange, 4000)
    deployed_exchange.addLiquidity(2000, { "value": 1000 })
    return deployed_exchange


def test_addLiquidity_add_liquidity(exchange, token):
    assert exchange.balance() == 1000
    reserve = exchange.getReserve()
    assert reserve == 2000


def test_addLiquidity_mint_LP_tokens(exchange, token):
    assert exchange.balanceOf(accounts[0]) == 1000
    assert exchange.totalSupply() == 1000


@pytest.fixture
def exchange_with_zero_amounts(token):
    deployed_exchange = accounts[0].deploy(Exchange, token.address)
    token.approve(deployed_exchange, 0)
    deployed_exchange.addLiquidity(0, { "value": 0 })
    return deployed_exchange


def test_addLiquidity_zero_amounts(exchange_with_zero_amounts, token):
    assert exchange_with_zero_amounts.balance() == 0
    reserve = exchange_with_zero_amounts.getReserve()
    assert reserve == 0


@pytest.fixture
def exchange_existing_reserves(token):
    deployed_exchange = accounts[0].deploy(Exchange, token.address)
    token.approve(deployed_exchange, 300)
    deployed_exchange.addLiquidity(200, { "value": 100 })
    return deployed_exchange


def test_addLiquidity_preserves_exchange_rate(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves
    exchange.addLiquidity(200, { "value": 50 })
    assert exchange.balance() == 150
    reserve = exchange.getReserve()
    assert reserve == 300


def test_addLiquidity_existing_reserves_mint_LP_tokens(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves
    exchange.addLiquidity(200, { "value": 50 })
    assert exchange.balanceOf(accounts[0]) == 150
    assert exchange.totalSupply() == 150


def test_addLiquidity_existing_reserves_fails_when_not_enought_tokens(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves
    with brownie.reverts():
        exchange.addLiquidity(50, { "value": 50 })


def test_removeLiquidity_removes_some_liquidity(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves

    userEtherBalanceBefore = accounts[0].balance()
    userTokenBalanceBefore = token.balanceOf(accounts[0])

    exchange.removeLiquidity(25)

    assert exchange.getReserve() == 150
    assert exchange.balance() == 75

    userEtherBalanceAfter = accounts[0].balance()
    userTokenBalanceAfter = token.balanceOf(accounts[0])

    assert (userEtherBalanceAfter - userEtherBalanceBefore) == 25
    assert (userTokenBalanceAfter - userTokenBalanceBefore) == 50


def test_removeLiquidity_removes_all_liquidity(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves

    userEtherBalanceBefore = accounts[0].balance()
    userTokenBalanceBefore = token.balanceOf(accounts[0])

    exchange.removeLiquidity(100)

    assert exchange.getReserve() == 0
    assert exchange.balance() == 0

    userEtherBalanceAfter = accounts[0].balance()
    userTokenBalanceAfter = token.balanceOf(accounts[0])

    assert (userEtherBalanceAfter - userEtherBalanceBefore) == 100
    assert (userTokenBalanceAfter - userTokenBalanceBefore) == 200


def test_removeLiquidity_pays_for_provided_liquidity(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves

    userEtherBalanceBefore = accounts[0].balance()
    userTokenBalanceBefore = token.balanceOf(accounts[0])

    exchange.ethToTokenSwap(18, { "value": 10, "from": accounts[1] })

    exchange.removeLiquidity(100)

    assert exchange.getReserve() == 0
    assert exchange.balance() == 0
    assert token.balanceOf(accounts[1]) == 18

    userEtherBalanceAfter = accounts[0].balance()
    userTokenBalanceAfter = token.balanceOf(accounts[0])

    assert (userEtherBalanceAfter - userEtherBalanceBefore) == 110
    assert (userTokenBalanceAfter - userTokenBalanceBefore) == 182


def test_removeLiquidity_burns_LP_tokens(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves

    exchange.removeLiquidity(25)
    exchange.totalSupply() == 75


def test_removeLiquidity_allows_invalid_amount(exchange_existing_reserves, token):
    exchange = exchange_existing_reserves

    exchange.removeLiquidity(100.1)
    assert exchange.getReserve() == 0
    assert exchange.balance() == 0
    assert token.balanceOf(exchange) == 0


def test_getTokenAmount(exchange, token):
    tokensOut = exchange.getTokenAmount(1)
    assert tokensOut == 1.9

    tokensOut = exchange.getTokenAmount(100)
    assert tokensOut == 180

    tokensOut = exchange.getTokenAmount(1000)
    assert tokensOut == 994


def test_getEthAmount(exchange, token):
    ethOut = exchange.getEthAmount(1)
    assert ethOut == 0.98

    ethOut = exchange.getEthAmount(100)
    assert ethOut == 47

    ethOut = exchange.getEthAmount(2000)
    assert ethOut == 497


def test_ethToTokenSwap_transfer_at_least_min_amount_of_tokens(exchange, token):
    userBalanceBefore = accounts[1].balance()

    exchange.ethToTokenSwap(1.97, { "value": 1, "from": accounts[1] })

    userBalanceAfter = accounts[1].balance()

    assert (userBalanceAfter - userBalanceBefore) == -1

    userTokenBalance = token.balanceOf(accounts[1])
    assert userTokenBalance == 1.97

    exchangeEthBalance = token.balanceOf(exchange)
    assert exchangeEthBalance == 1999


def test_ethToTokenSwap_affects_exchange_rate(exchange, token):
    tokensOut = exchange.getTokenAmount(10)
    assert tokensOut == 19

    exchange.ethToTokenSwap(9, { "value": 10, "from": accounts[1] })

    tokensOut = exchange.getTokenAmount(10)
    assert tokensOut == 19


def test_ethToTokenSwap_fails_when_output_amount_is_less_than_min_amount(exchange, token):
    with brownie.reverts():
        exchange.ethToTokenSwap(2, { "value": 1, "from": accounts[1] })


def test_ethToTokenSwap_allows_zero_swaps(exchange, token):
    exchange.ethToTokenSwap(0, { "value": 0, "from": accounts[1] })

    userTokenBalance = token.balanceOf(accounts[1])
    assert userTokenBalance == 0

    exchangeEthBalance = exchange.balance()
    assert exchangeEthBalance == 1000

    exchangeTokenBalance = token.balanceOf(exchange)
    assert exchangeTokenBalance == 2000
    assert userTokenBalance == 0


@pytest.fixture
def exchange_swap(token):
    deployed_exchange = accounts[0].deploy(Exchange, token.address)
    token.transfer(accounts[1], 22)
    token.approve(deployed_exchange, 22, { "from": accounts[1] })
    token.approve(deployed_exchange, 2000)
    deployed_exchange.addLiquidity(2000, { "value": 1000 })
    return deployed_exchange


def test_tokenToEthSwap_transfer_at_least_min_amount_of_tokens(exchange_swap, token):
    exchange = exchange_swap

    userBalanceBefore = accounts[1].balance()
    exchangeBalanceBefore = exchange.balance()

    exchange.tokenToEthSwap(2, 0.9, { "from": accounts[1] })

    userBalanceAfter = accounts[1].balance()

    assert (userBalanceAfter - userBalanceBefore) == 0.98

    userTokenBalance = token.balanceOf(accounts[1])
    assert userTokenBalance == 20

    exchangeBalanceAfter = exchange.balance()
    assert (exchangeBalanceAfter - exchangeBalanceBefore) == -0.98

    exchangeTokenBalance = token.balanceOf(exchange)
    assert exchangeTokenBalance == 2002


def test_tokenToEthSwap_affect_exchange_rate(exchange_swap, token):
    exchange = exchange_swap

    ethOut = exchange.getEthAmount(20)
    assert ethOut == 9.8

    exchange.tokenToEthSwap(20, 9, { "from": accounts[1] })

    ethOut = exchange.getEthAmount(20)
    assert ethOut == 9.6


def test_tokenToEthSwap_fail_when_output_amount_is_less_than_min_amount(exchange_swap, token):
    exchange = exchange_swap

    with brownie.reverts():
        exchange.tokenToEthSwap(2, 1, { "from": accounts[1] })


def test_tokenToEthSwap_allow_zero_swap(exchange_swap, token):
    exchange = exchange_swap

    userBalanceBefore = accounts[1].balance()
    exchange.tokenToEthSwap(0, 0, { "from": accounts[1] })

    userBalanceAfter = accounts[1].balance()
    (userBalanceAfter - userBalanceBefore) == "0"

    userTokenBalance = token.balanceOf(accounts[1])
    assert userTokenBalance == 22

    exchangeEthBalance = exchange.balance()
    assert exchangeEthBalance == 1000

    exchangeTokenBalance = token.balanceOf(exchange)
    assert exchangeTokenBalance == 2000
