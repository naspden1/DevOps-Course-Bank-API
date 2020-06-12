"""Unit tests for bank.py"""

import pytest
from hypothesis import given
from hypothesis.strategies import integers, floats

from bank_api.bank import Bank, Account


@pytest.fixture
def bank() -> Bank:
    return Bank()


def test_accounts_are_immutable():
    account = Account('Immutable')
    with pytest.raises(Exception):
        # This operation should raise an exception
        account.name = 'Mutable'


def test_bank_creates_empty(bank):
    assert len(bank.accounts) == 0
    assert len(bank.transactions) == 0


def test_can_create_and_get_account(bank):
    bank.create_account('Test')
    account = bank.get_account('Test')

    assert len(bank.accounts) == 1
    assert account.name == 'Test'


def test_cannot_duplicate_accounts(bank):
    bank.create_account('duplicate')
    bank.create_account('duplicate')

    assert len(bank.accounts) == 1


def test_cannot_modify_accounts_set(bank):
    accounts = bank.accounts
    accounts.add(Account('New Account'))

    assert len(bank.accounts) == 0


@given(amount=integers())
def test_add_funds(amount):
    bank = Bank()
    bank.create_account('Test')
    bank.add_funds('Test', amount)
    transactions = bank.transactions

    assert len(transactions) == 1
    assert transactions.pop().amount == amount


def test_add_funds_no_account(bank):
    with pytest.raises(ValueError):
        bank.add_funds('no-account', 3)


def test_add_multiple_funds(bank):
    bank.create_account('Test')
    bank.add_funds('Test', 50)
    bank.add_funds('Test', 25)

    transactions = bank.transactions
    assert len(transactions) == 2
    assert {t.amount for t in transactions} == {25, 50}


@given(amount=floats())
def test_add_fractional_funds(amount):
    bank = Bank()
    bank.create_account('Test')
    with pytest.raises(TypeError):
        bank.add_funds('Test', amount)


def test_move_funds(bank):
    bank.create_account('A')
    bank.create_account('B')
    bank.move_funds('A', 'B', 25)

    assert len(bank.transactions) == 2

    for t in bank.transactions:
        if t.account.name == 'A':
            assert t.amount == -25
        if t.account.name == 'B':
            assert t.amount == 25

    transaction0, transaction1 = bank.transactions
    assert transaction0.date == transaction1.date


def test_move_funds_to_non_account(bank):
    bank.create_account('A')
    with pytest.raises(ValueError):
        bank.move_funds('A', 'DoesntExist', 25)


def test_move_funds_from_non_account(bank):
    bank.create_account('A')
    with pytest.raises(ValueError):
        bank.move_funds('DoesntExist', 'A', 25)


@given(amount=floats())
def test_move_fractional_funds(amount):
    bank = Bank()
    bank.create_account('A')
    bank.create_account('B')
    with pytest.raises(TypeError):
        bank.move_funds('A', 'B', amount)


def test_account_cant_go_overdrawn_via_withdrawal(bank):
    bank.create_account('Test')
    bank.add_funds('Test', 5)
    with pytest.raises(OverdrawnError):
        bank.add_funds('Test', -10)


def test_account_cant_go_overdrawn_via_transfer(bank):
    bank.create_account('A')
    bank.create_account('B')
    bank.add_funds('A', 5)
    with pytest.raises(OverdrawnError):
        bank.move_funds('A', 'B', 10)
