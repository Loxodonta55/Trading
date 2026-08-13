"""
Unit & Integration tests for Feature F1: IBKR Connection Layer
"""
import pytest
from unittest.mock import MagicMock, patch
from src.broker.ibkr_client import IBKRClient, get_ibkr_client


def test_ibkr_client_initialization():
    """Test IBKRClient initializes with custom or default configs."""
    client = IBKRClient(host="127.0.0.1", port=7497, client_id=99)
    assert client.host == "127.0.0.1"
    assert client.port == 7497
    assert client.client_id == 99


def test_ibkr_client_not_connected_default_responses():
    """Test default values when not connected to IBKR."""
    client = IBKRClient(host="127.0.0.1", port=7497)
    assert client.is_connected() is False

    account_summary = client.get_account_summary()
    assert account_summary["connected"] is False
    assert "error" in account_summary
    assert account_summary["net_liquidity"] == 0.0

    positions = client.get_positions()
    assert isinstance(positions, list)
    assert len(positions) == 0


def test_ibkr_client_mock_connection_summary():
    """Test get_account_summary parsing with mocked IB object."""
    client = IBKRClient(host="127.0.0.1", port=7497)

    # Create mock IB instance
    mock_ib = MagicMock()
    mock_ib.isConnected.return_value = True
    mock_ib.managedAccounts.return_value = ["U1234567"]

    # Mock TagValue account summary items
    item1 = MagicMock()
    item1.tag = "NetLiquidity"
    item1.value = "5000.00"
    item1.currency = "CHF"

    item2 = MagicMock()
    item2.tag = "AvailableFunds"
    item2.value = "4500.00"
    item2.currency = "CHF"

    item3 = MagicMock()
    item3.tag = "BuyingPower"
    item3.value = "18000.00"
    item3.currency = "CHF"

    mock_ib.accountSummary.return_value = [item1, item2, item3]
    client.ib = mock_ib

    summary = client.get_account_summary()
    assert summary["connected"] is True
    assert summary["account_id"] == "U1234567"
    assert summary["net_liquidity"] == 5000.0
    assert summary["available_funds"] == 4500.0
    assert summary["buying_power"] == 18000.0
    assert summary["currency"] == "CHF"


def test_ibkr_client_mock_positions():
    """Test get_positions parsing with mocked IB positions."""
    client = IBKRClient(host="127.0.0.1", port=7497)

    mock_ib = MagicMock()
    mock_ib.isConnected.return_value = True

    # Mock contract & position
    mock_contract = MagicMock()
    mock_contract.symbol = "TQQQ"
    mock_contract.secType = "STK"
    mock_contract.currency = "USD"
    mock_contract.exchange = "NASDAQ"

    mock_pos = MagicMock()
    mock_pos.account = "U1234567"
    mock_pos.contract = mock_contract
    mock_pos.position = 10.0
    mock_pos.avgCost = 55.20

    mock_ib.positions.return_value = [mock_pos]
    client.ib = mock_ib

    positions = client.get_positions()
    assert len(positions) == 1
    assert positions[0]["symbol"] == "TQQQ"
    assert positions[0]["position"] == 10.0
    assert positions[0]["avg_cost"] == 55.20


def test_singleton_client():
    """Test get_ibkr_client returns singleton instance."""
    c1 = get_ibkr_client()
    c2 = get_ibkr_client()
    assert c1 is c2
