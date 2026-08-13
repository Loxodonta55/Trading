"""
IBKR Client Connection Layer (Feature F1)
Provides async/sync connection handling to Interactive Brokers TWS or IB Gateway via ib_insync.
"""
import logging
import asyncio
from typing import Dict, List, Any, Optional
import config

logger = logging.getLogger(__name__)

# Apply nest_asyncio to allow nested event loops in FastAPI / Jupyter / Async environments
try:
    import nest_asyncio
    nest_asyncio.apply()
except Exception as e:
    logger.debug(f"nest_asyncio apply status: {e}")



try:
    from ib_insync import IB, Stock, ETF, Contract, Position, AccountValue
    IB_INSYNC_AVAILABLE = True
except ImportError:
    IB_INSYNC_AVAILABLE = False
    logger.warning("ib_insync is not installed. IBKR connection features will run in mock mode.")


class IBKRClient:
    """
    Client for Interactive Brokers API via ib_insync.
    Manages connection, health checks, account summary, and open positions.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        client_id: Optional[int] = None,
        account: Optional[str] = None,
    ):
        self.host = host or config.IBKR_HOST
        self.port = port or config.IBKR_PORT
        self.client_id = client_id or config.IBKR_CLIENT_ID
        self.account = account or config.IBKR_ACCOUNT
        self.ib: Optional[Any] = None
        if IB_INSYNC_AVAILABLE:
            self.ib = IB()

    def connect(self, timeout: int = 10) -> bool:
        """
        Establishes connection to IBKR TWS or IB Gateway.
        Returns True if successful, False otherwise.
        """
        if not IB_INSYNC_AVAILABLE or self.ib is None:
            logger.error("Cannot connect: ib_insync package is missing.")
            return False

        if self.ib.isConnected():
            logger.info("IBKR client is already connected.")
            return True

        try:
            logger.info(f"Connecting to IBKR TWS/Gateway at {self.host}:{self.port} (ClientID: {self.client_id})...")
            self.ib.connect(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=timeout,
                readonly=False
            )
            logger.info(f"Successfully connected to IBKR. Account: {self.ib.managedAccounts()}")
            return True
        except Exception as err:
            logger.warning(f"Failed to connect to IBKR: {err}")
            return False

    def disconnect(self) -> None:
        """Disconnects cleanly from IBKR."""
        if self.ib and self.ib.isConnected():
            try:
                self.ib.disconnect()
                logger.info("Disconnected from IBKR.")
            except Exception as e:
                logger.error(f"Error while disconnecting from IBKR: {e}")

    def is_connected(self) -> bool:
        """Checks if active socket connection exists."""
        return bool(self.ib and self.ib.isConnected())

    def get_account_summary(self) -> Dict[str, Any]:
        """
        Retrieves account summary metrics (NetLiquidity, AvailableFunds, BuyingPower, Cash).
        """
        if not self.is_connected():
            return {
                "connected": False,
                "error": "Not connected to IBKR TWS/Gateway",
                "net_liquidity": 0.0,
                "available_funds": 0.0,
                "buying_power": 0.0,
                "currency": "CHF",
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
            }

        try:
            account_values = self.ib.accountSummary()
            summary_dict: Dict[str, Any] = {
                "connected": True,
                "account_id": self.ib.managedAccounts()[0] if self.ib.managedAccounts() else "",
                "net_liquidity": 0.0,
                "available_funds": 0.0,
                "buying_power": 0.0,
                "total_cash": 0.0,
                "unrealized_pnl": 0.0,
                "realized_pnl": 0.0,
                "currency": "USD"
            }

            for item in account_values:
                # Target primary currency values or overall account tags
                if item.tag == "NetLiquidity":
                    summary_dict["net_liquidity"] = float(item.value)
                    summary_dict["currency"] = item.currency or "USD"
                elif item.tag == "AvailableFunds":
                    summary_dict["available_funds"] = float(item.value)
                elif item.tag == "BuyingPower":
                    summary_dict["buying_power"] = float(item.value)
                elif item.tag == "TotalCashValue":
                    summary_dict["total_cash"] = float(item.value)
                elif item.tag == "UnrealizedPnL":
                    summary_dict["unrealized_pnl"] = float(item.value)
                elif item.tag == "RealizedPnL":
                    summary_dict["realized_pnl"] = float(item.value)

            return summary_dict
        except Exception as err:
            logger.error(f"Error fetching account summary: {err}")
            return {
                "connected": True,
                "error": str(err),
                "net_liquidity": 0.0,
                "available_funds": 0.0
            }

    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Retrieves active open positions from IBKR portfolio.
        """
        if not self.is_connected():
            return []

        positions_list: List[Dict[str, Any]] = []
        try:
            raw_positions = self.ib.positions()
            for pos in raw_positions:
                contract = pos.contract
                positions_list.append({
                    "account": pos.account,
                    "symbol": contract.symbol,
                    "sec_type": contract.secType,
                    "currency": contract.currency,
                    "exchange": contract.exchange or contract.primaryExchange,
                    "position": float(pos.position),
                    "avg_cost": float(pos.avgCost),
                })
            return positions_list
        except Exception as err:
            logger.error(f"Error fetching positions: {err}")
            return []


# Global singleton instance helper
_ibkr_client_instance: Optional[IBKRClient] = None

def get_ibkr_client() -> IBKRClient:
    """Returns global singleton IBKRClient instance."""
    global _ibkr_client_instance
    if _ibkr_client_instance is None:
        _ibkr_client_instance = IBKRClient()
    return _ibkr_client_instance
