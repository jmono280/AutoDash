import json
from contextlib import asynccontextmanager
from datetime import date
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from mcp import Client

from app.mcp import server as mcp_module
from app.schemas.daily_sales import SalesKpisOut


@asynccontextmanager
async def _fake_session():
    yield object()


@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    monkeypatch.setattr(mcp_module, "AsyncSessionLocal", _fake_session)


@pytest.mark.anyio
async def test_lists_read_only_tools_for_every_domain():
    async with Client(mcp_module.server) as client:
        names = {t.name for t in (await client.list_tools()).tools}

    assert {
        "get_data_coverage",
        "get_sales_kpis",
        "get_hours_kpis",
        "get_technician_ranking",
        "get_wip_kpis",
        "list_wip",
        "get_payment_kpis",
        "get_call_kpis",
        "get_idms_chargeoff_kpis",
        "get_idms_sales_kpis",
        "get_idms_inventory_kpis",
    } <= names
    assert not any(word in n for n in names for word in ("sync", "import", "login", "export"))


@pytest.mark.anyio
async def test_sales_kpis_passes_requested_period_and_returns_json(monkeypatch):
    kpis = SalesKpisOut(
        total_cars=91, total_gross="71740.61", total_net="71740.61", avg_ticket="396.89",
        total_cogs="26292.88", total_profit="45447.73", profit_pct="63.35", cogs_pct="36.65",
    )
    get_kpis = AsyncMock(return_value=kpis)
    monkeypatch.setattr(mcp_module.SalesService, "get_kpis", get_kpis)

    async with Client(mcp_module.server) as client:
        result = await client.call_tool(
            "get_sales_kpis", {"from_date": "2026-04-01", "to_date": "2026-04-28"}
        )

    assert not result.is_error
    payload = json.loads(result.content[0].text)
    assert payload["total_cars"] == 91
    assert payload["total_gross"] == "71740.61"
    _db, start, end = get_kpis.await_args.args
    assert (start, end) == (date(2026, 4, 1), date(2026, 4, 28))


@pytest.mark.anyio
async def test_sales_kpis_defaults_to_current_month(monkeypatch):
    get_kpis = AsyncMock(return_value=SalesKpisOut(
        total_cars=0, total_gross=0, total_net=0, avg_ticket=0,
        total_cogs=0, total_profit=0, profit_pct=0, cogs_pct=0,
    ))
    monkeypatch.setattr(mcp_module.SalesService, "get_kpis", get_kpis)

    async with Client(mcp_module.server) as client:
        await client.call_tool("get_sales_kpis", {})

    _db, start, end = get_kpis.await_args.args
    today = date.today()
    assert start == today.replace(day=1)
    assert end.month == today.month and end >= today


@pytest.mark.anyio
async def test_inverted_period_is_reported_as_tool_error():
    async with Client(mcp_module.server) as client:
        result = await client.call_tool(
            "get_sales_kpis", {"from_date": "2026-05-01", "to_date": "2026-04-01"}
        )

    assert result.is_error
    assert "from_date must be before" in result.content[0].text


@pytest.mark.anyio
async def test_service_http_errors_become_readable_tool_errors(monkeypatch):
    monkeypatch.setattr(
        mcp_module.TechnicianService,
        "get_detail",
        AsyncMock(side_effect=HTTPException(404, "Technician 'Nobody' not found in the given period")),
    )

    async with Client(mcp_module.server) as client:
        result = await client.call_tool("get_technician_detail", {"name": "Nobody"})

    assert result.is_error
    assert "Technician 'Nobody' not found" in result.content[0].text


def _inventory_row(stock, make, dol, price):
    return {
        "id": "00000000-0000-0000-0000-000000000001", "snapshot_date": "2026-10-01",
        "inventory_id": stock, "dealer_id": None, "stock_number": stock, "vehicle_year": "2020",
        "vin_last6": "123456", "inventory_flags": None, "make": make, "model_trim": "Base",
        "exterior_color": None, "acq_date": None, "dol": dol, "status": "Available",
        "alternate_lot": None, "price": price, "wholesale_price": 0, "mileage": 1000,
        "imported_at": "2026-10-01T00:00:00Z", "created_at": "2026-10-01T00:00:00Z",
        "updated_at": "2026-10-01T00:00:00Z", "deleted_at": None,
    }


@pytest.mark.anyio
async def test_lists_every_idms_tab_tool():
    async with Client(mcp_module.server) as client:
        names = {t.name for t in (await client.list_tools()).tools}

    assert {
        "get_idms_chargeoff_overview", "get_idms_chargeoff_monthly_detail", "list_idms_charge_offs",
        "get_idms_sales_by_vehicle", "list_idms_sales", "list_idms_inventory",
    } <= names


@pytest.mark.anyio
async def test_list_inventory_filters_sorts_limits_and_trims_fields(monkeypatch):
    rows = [
        _inventory_row("A1", "Toyota", 10, 15000),
        _inventory_row("A2", "Toyota", 120, 9000),
        _inventory_row("A3", "Honda", 200, 12000),
        _inventory_row("A4", "toyota", 95, 11000),
    ]
    monkeypatch.setattr(mcp_module.IdmsService, "get_inventory", AsyncMock(return_value=rows))

    async with Client(mcp_module.server) as client:
        result = await client.call_tool(
            "list_idms_inventory", {"make": "TOYOTA", "min_days": 90, "limit": 1}
        )

    payload = json.loads(result.content[0].text)
    assert payload["total"] == 2
    assert payload["returned"] == 1
    assert [i["stock_number"] for i in payload["items"]] == ["A2"]
    assert "id" not in payload["items"][0] and "created_at" not in payload["items"][0]


@pytest.mark.anyio
async def test_list_charge_offs_filters_by_month_and_sorts_by_balance(monkeypatch):
    def row(acct, month, balance):
        return {
            "report_year": 2026, "acct_id": acct, "borrower": "Doe", "date_sold": None,
            "charge_off_date": f"2026-{month:02d}-15", "vin": None, "year": None, "make": None,
            "model": None, "original_balance": balance, "original_total_balance": balance,
            "total_recovery": 0, "current_balance": balance, "total_adjusted": 0,
            "repo_method": None, "status": None, "acct_flags": None,
            "imported_at": "2026-10-01T00:00:00Z", "id": "00000000-0000-0000-0000-000000000002",
            "created_at": "2026-10-01T00:00:00Z", "updated_at": "2026-10-01T00:00:00Z",
            "deleted_at": None,
        }

    get_charge_offs = AsyncMock(return_value=[row("1", 3, 500), row("2", 3, 900), row("3", 4, 5000)])
    monkeypatch.setattr(mcp_module.IdmsService, "get_charge_offs", get_charge_offs)

    async with Client(mcp_module.server) as client:
        result = await client.call_tool("list_idms_charge_offs", {"year": 2026, "month": 3})

    payload = json.loads(result.content[0].text)
    assert [i["acct_id"] for i in payload["items"]] == ["2", "1"]
    assert payload["total"] == 2
    assert get_charge_offs.await_args.kwargs == {"year": 2026}
