# 📋 Feature Spec: IBKR Connection Layer (F1)

---

## 📌 Status
- **Status**: In Development
- **Module**: `src/broker/`
- **Component**: `ibkr_client.py`
- **Dependencies**: `ib_insync`, `nest_asyncio`, `FastAPI` (`web/server.py`)

---

## 🎯 Zweck & Funktionalität
Stellt eine sichere, asynchrone und fehlertolerante Verbindung zu **Interactive Brokers (IBKR)** her über die Trader Workstation (TWS) oder den IB Gateway Socket API Client (`ib_insync`). 

Das Modul überwacht kontinuierlich den Verbindungsstatus, hält die Session aktiv und ermöglicht das Auslesen von Konto-Metriken (Cash, Net Liquidity, Buying Power) sowie offenen Depot-Positionen für das Live-Trading und das React Dashboard.

---

## 🏗️ Spezifizierte Komponenten & Schnittstellen

### 1. Broker Client Core (`src/broker/ibkr_client.py`)
- **Verbindungsaufbau (`connect`)**:
  - Verbindung zu Host (`127.0.0.1`), Port (`7496` für Live / `7497` für Paper / `4001` für IB Gateway) und Client-ID.
  - Asynchrone Anbindung mit automatischer Wiederverbindung (Auto-Reconnect bei Socket-Disconnect).
- **Verbindungsprüfung (`is_connected`)**:
  - Liefert `True` / `False` sowie Latenz- und Healthcheck-Status.
- **Konto-Metriken (`get_account_summary`)**:
  - Abrufen wichtiger Kontowerte: `NetLiquidity`, `AvailableFunds`, `BuyingPower`, `UnrealizedPnL`, `RealizedPnL`, `FullInitMarginReq`.
  - Unterscheidung von Kontowährungen (z.B. CHF, USD).
- **Positionen-Abfrage (`get_positions`)**:
  - Rückgabe aller aktuellen Depotpositionen mit: `Symbol`, `SecType` (STK/OPT/ETF), `Currency`, `PositionQuantity`, `AverageCost`, `MarketPrice`, `MarketValue`, `UnrealizedPnL`.

### 2. Konfiguration (`config.py` & `.env`)
- Konfigurierbare Parameter:
  - `IBKR_HOST`: IP-Adresse der TWS / Gateway (default: `127.0.0.1`)
  - `IBKR_PORT`: Socket-Port (default: `7496` Live / `7497` Paper)
  - `IBKR_CLIENT_ID`: Eindeutige Client-ID (default: `1`)
  - `IBKR_ACCOUNT`: Optionales Filtern nach spezifischer IBKR Account ID.

### 3. FastAPI REST Endpunkte (`web/server.py`)
- `GET /api/broker/status`: Status der IBKR TWS/Gateway-Verbindung.
- `GET /api/broker/account`: Zieldaten wie Cash, Liquidity & PnL.
- `GET /api/broker/positions`: Aktuelle offene Positionen für das React Dashboard.

---

## 🧪 Verifikation & Tests
- `tests/test_ibkr_connection.py`:
  - Unit Test mit Mocks für `ib_insync`.
  - Integrationstest für echten Connect (falls TWS/Gateway läuft).
