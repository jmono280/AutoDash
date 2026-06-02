from ringcentral import SDK
import asyncio
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

load_dotenv()

# Importar settings y repo solo si el paquete de la app está disponible
try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from app.core.config import settings
    from app.repositories.call_analytics_repo import CallAnalyticsRepository
    _DB_AVAILABLE = True
except ImportError:
    _DB_AVAILABLE = False

console = Console()
TZ_NY = ZoneInfo("America/New_York")

_rows_to_save: list[dict] = []

parser = argparse.ArgumentParser()
parser.add_argument("--from", dest="date_from", default="", help='Ej: "05/13/2026 12:00 AM"')
parser.add_argument("--to",   dest="date_to",   default="", help='Ej: "05/13/2026 11:59 PM"')
args = parser.parse_args()

def parse_ny(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%m/%d/%Y %I:%M %p").replace(tzinfo=TZ_NY)

if args.date_from and args.date_to:
    TIME_FROM = parse_ny(args.date_from).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    TIME_TO   = parse_ny(args.date_to).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
else:
    yesterday = datetime.now(TZ_NY) - timedelta(days=1)
    TIME_FROM = yesterday.replace(hour=0,  minute=0,  second=0,  microsecond=0).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    TIME_TO   = yesterday.replace(hour=23, minute=59, second=59, microsecond=0).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

console.print(f"[dim]Rango consultado → {TIME_FROM}  /  {TIME_TO}[/dim]")

def read_analytics_aggregate_data():
  # RC_EXTENSION_IDS: comma-separated list of RingCentral extension IDs, e.g. "123,456,789"
  extension_ids = [e.strip() for e in os.environ.get('RC_EXTENSION_IDS', '').split(',') if e.strip()]

  try:
    bodyParams = {
      'grouping': {
        'groupBy': "Users",
        'keys': extension_ids
      },
      'timeSettings': {
        'timeZone': "America/New_York",
        'timeRange': {
          'timeFrom': TIME_FROM,
          'timeTo':   TIME_TO
        }
      },
      'callFilters': {
        'directions': ["Inbound", "Outbound"],
        'origins': ["Internal", "External"],
      },
      'responseOptions': {
        'counters': {
          'allCalls':        {'aggregationType': "Sum"},
          'callsByDirection': {'aggregationType': "Sum"},
          'callsByType':     {'aggregationType': "Sum"},
          'callsByOrigin':   {'aggregationType': "Sum"},
          'callsByResponse': {'aggregationType': "Sum"},
          'callsByResult':   {'aggregationType': "Sum"},
        },
        'timers': {
          'allCallsDuration': {'aggregationType': "Sum"},
        }
      }
    }

    queryParams = {
      'perPage': 100
    }

    endpoint = '/analytics/calls/v1/accounts/~/aggregation/fetch'
    resp = platform.post(endpoint, bodyParams, queryParams)
    records = resp.json_dict().get('data', {}).get('records', [])

    # Tabla 1 — resumen por dirección y tipo
    t1 = Table(title="Resumen — Dirección y tipo de llamada", box=box.ROUNDED)
    t1.add_column("Ext.", style="cyan", justify="center")
    t1.add_column("Nombre", style="bold white")
    t1.add_column("Total", justify="right", style="bold white")
    t1.add_column("Entrantes", justify="right", style="green")
    t1.add_column("Salientes", justify="right", style="blue")
    t1.add_column("Directas", justify="right", style="dim green")
    t1.add_column("Cola", justify="right", style="dim cyan")
    t1.add_column("Transfer.", justify="right", style="dim yellow")
    t1.add_column("≈ Portal", justify="right", style="bold magenta")
    t1.add_column("Duración", justify="right", style="yellow")

    # Tabla 2 — desglose de entrantes por origen y resultado
    t2 = Table(title="Desglose entrantes — Origen y resultado", box=box.ROUNDED)
    t2.add_column("Ext.", style="cyan", justify="center")
    t2.add_column("Nombre", style="bold white")
    t2.add_column("Externas", justify="right", style="green")
    t2.add_column("Internas", justify="right", style="dim green")
    t2.add_column("Contestadas", justify="right", style="green")
    t2.add_column("No contest.", justify="right", style="red")
    t2.add_column("Completadas", justify="right", style="green")
    t2.add_column("Abandonadas", justify="right", style="red")
    t2.add_column("Buzón voz", justify="right", style="yellow")

    for row in records:
        info     = row.get('info', {})
        counters = row.get('counters', {})
        timers   = row.get('timers', {})

        ext_num = info.get('extensionNumber', '-')
        name    = info.get('name', '-')

        total   = int(counters.get('allCalls', {}).get('values', 0))
        by_dir  = counters.get('callsByDirection', {}).get('values', {})
        inbound = int(by_dir.get('inbound', 0))
        outbound= int(by_dir.get('outbound', 0))

        by_type   = counters.get('callsByType', {}).get('values', {})
        direct    = int(by_type.get('direct', 0))
        from_queue= int(by_type.get('fromQueue', 0))
        transferred=int(by_type.get('transferred', 0))

        by_origin = counters.get('callsByOrigin', {}).get('values', {})
        external  = int(by_origin.get('external', 0))
        internal  = int(by_origin.get('internal', 0))

        by_resp   = counters.get('callsByResponse', {}).get('values', {})
        answered  = int(by_resp.get('answered', 0))
        not_ans   = int(by_resp.get('notAnswered', 0))

        by_result       = counters.get('callsByResult', {}).get('values', {})
        completed       = int(by_result.get('completed', 0))
        abandoned       = int(by_result.get('abandoned', 0))
        voicemail       = int(by_result.get('voicemail', 0))
        answered_else   = int(by_result.get('answeredElsewhere', 0))
        missed          = int(by_result.get('missed', 0))
        unknown         = int(by_result.get('unknown', 0))
        forwarded       = int(by_result.get('forwarded', 0))
        accepted        = int(by_result.get('accepted', 0))
        transferred_out = int(by_result.get('transferred', 0))
        picked_up       = int(by_result.get('pickedUp', 0))

        accounted = completed + abandoned + voicemail + answered_else + missed + unknown + forwarded + accepted + transferred_out + picked_up

        # Portal subtracts max(ae, xfer) — whichever routing category dominates
        # then subtracts unknown (vm>0) or missed (vm==0) for unresolved calls
        exclusion     = max(answered_else, transferred_out)
        portal_equiv  = total - exclusion - (unknown if voicemail > 0 else missed)

        secs     = int(timers.get('allCalls', {}).get('values', 0))
        duration = f"{secs // 3600}h {(secs % 3600) // 60}m {secs % 60}s" if secs else "0s"

        console.print(
            f"[dim]  {name}: total={total} acc={accounted} gap={total-accounted} "
            f"ae={answered_else} xfer={transferred_out} excl={exclusion} "
            f"missed={missed} vm={voicemail} unk={unknown} → ≈portal={portal_equiv}[/dim]"
        )

        _rows_to_save.append({
            "time_from":        datetime.fromisoformat(TIME_FROM.replace("Z", "+00:00")),
            "time_to":          datetime.fromisoformat(TIME_TO.replace("Z", "+00:00")),
            "extension_number": ext_num,
            "extension_name":   name,
            "total_calls":      total,
            "inbound":          inbound,
            "outbound":         outbound,
            "direct":           direct,
            "from_queue":       from_queue,
            "transferred":      transferred,
            "portal_equiv":     portal_equiv,
            "duration_seconds": secs,
            "external":         external,
            "internal":         internal,
            "answered":         answered,
            "not_answered":     not_ans,
            "completed":        completed,
            "abandoned":        abandoned,
            "voicemail":        voicemail,
        })
        t1.add_row(ext_num, name, str(total), str(inbound), str(outbound),
                   str(direct), str(from_queue), str(transferred), str(portal_equiv), duration)
        t2.add_row(ext_num, name, str(external), str(internal),
                   str(answered), str(not_ans),
                   str(completed), str(abandoned), str(voicemail))

    console.print()
    console.print(t1)
    console.print()
    console.print(t2)
  except Exception as err:
    sys.exit(f"Unable to read analytics aggregation {err}")

async def _save_to_db(rows: list[dict], time_from: datetime, time_to: datetime) -> None:
    if not _DB_AVAILABLE:
        console.print("[yellow]DB no disponible — omitiendo guardado[/yellow]")
        return
    engine = create_async_engine(settings.DATABASE_URL, future=True)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    repo = CallAnalyticsRepository()
    async with factory() as session:
        await repo.upsert_run(session, rows, time_from, time_to)
    await engine.dispose()
    console.print(f"[green]Guardados {len(rows)} registros en call_analytics[/green]")


# Instantiate the SDK and get the platform instance
rcsdk = SDK( os.environ.get('RC_APP_CLIENT_ID'),
             os.environ.get('RC_APP_CLIENT_SECRET'),
             os.environ.get('RC_SERVER_URL') )
platform = rcsdk.platform()

# Authenticate a user using a personal JWT token
def login():
    try:
        platform.login(jwt=os.environ.get('RC_USER_JWT'))
        read_analytics_aggregate_data()
        if _rows_to_save:
            tf = datetime.fromisoformat(TIME_FROM.replace("Z", "+00:00"))
            tt = datetime.fromisoformat(TIME_TO.replace("Z", "+00:00"))
            asyncio.run(_save_to_db(_rows_to_save, tf, tt))
    except Exception as e:
        sys.exit("Unable to authenticate to platform. Check credentials." + str(e))

login()