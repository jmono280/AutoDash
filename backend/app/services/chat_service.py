from __future__ import annotations

import json
from calendar import monthrange
from collections.abc import AsyncGenerator
from datetime import date, datetime, timezone

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.call_analytics_repo import CallAnalyticsRepository
from app.repositories.payment_repo import PaymentRepository
from app.schemas.chat import ChatChunk, ChatMessage, ChatRequest, ChatResponse
from app.services.hours_service import HoursService
from app.services.sales_service import SalesService
from app.services.technician_service import TechnicianService
from app.services.wip_service import WipService


class ChatService:
    _SYSTEM_BASE = (
        "Eres un asistente de análisis para Automania, taller mecánico. "
        "Ayudas a interpretar métricas operativas y financieras. "
        "Responde de forma concisa y práctica en español."
    )

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

    async def _build_db_context(self, db: AsyncSession) -> str:
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day=monthrange(today.year, today.month)[1])
        lines: list[str] = [f"Período analizado: {start} → {end}"]

        try:
            kpis = await SalesService().get_kpis(db, start, end)
            lines.append(
                f"VENTAS: {kpis.total_cars} autos | Gross ${float(kpis.total_gross):,.0f} | "
                f"Profit ${float(kpis.total_profit):,.0f} ({float(kpis.profit_pct):.1f}%) | "
                f"Ticket prom ${float(kpis.avg_ticket):,.0f}"
            )
            trend = await SalesService().get_trend(db, start, end)
            if trend:
                lines.append("Trend ventas (últimos 7 días): " + " | ".join(
                    f"{str(t.date)[5:]}:${float(t.gross_sales):,.0f}" for t in trend[-7:]
                ))
        except Exception:
            pass

        try:
            hkpis = await HoursService().get_kpis(db, start, end)
            lines.append(
                f"HORAS: Labor ${float(hkpis.labor_dollars):,.0f} | "
                f"Vendidas {float(hkpis.hours_sold):.1f}h | Pagadas {float(hkpis.hours_paid):.1f}h | "
                f"Advisor Eff {float(hkpis.advisor_efficiency):.1f}% | "
                f"Tech Proficiency {float(hkpis.technician_proficiency):.1f}%"
            )
        except Exception:
            pass

        try:
            ranking = await TechnicianService().get_ranking(db, start, end, "hours_sold")
            top = []
            for i, t in enumerate(ranking[:8]):
                prof = f" Prof {float(t.technician_proficiency):.0f}%" if t.technician_proficiency else ""
                top.append(
                    f"{i+1}.{t.technician_name} {float(t.hours_sold):.1f}h "
                    f"${float(t.labor_dollars):,.0f}{prof}"
                )
            if top:
                lines.append("TÉCNICOS (ranking por horas): " + " | ".join(top))
        except Exception:
            pass

        try:
            wkpis = await WipService().get_kpis(db)
            lines.append(
                f"WIP: {wkpis.total_ros} ROs abiertos | Avg {float(wkpis.avg_days_open):.1f} días | "
                f"Más antiguo {wkpis.oldest_ro_days}d | Est total ${float(wkpis.total_estimated):,.0f}"
            )
            aging = await WipService().get_aging(db)
            if aging:
                lines.append("Aging WIP: " + " | ".join(f"{b.bucket}:{b.count}" for b in aging))
            by_cat = await WipService().get_by_category(db)
            if by_cat:
                lines.append("WIP por categoría: " + " | ".join(
                    f"{c.category}:{c.count}" for c in by_cat[:8]
                ))
            by_adv = await WipService().get_by_advisor(db)
            if by_adv:
                lines.append("WIP por asesor: " + " | ".join(
                    f"{a.advisor or 'Sin asignar'}:{a.count}" for a in by_adv[:6]
                ))
        except Exception:
            pass

        try:
            pkpis = await PaymentRepository().get_kpis(db, from_date=start, to_date=end)
            lines.append(
                f"PAGOS: {pkpis['total_payments']} transacciones | "
                f"${float(pkpis['total_amount']):,.0f} total | "
                f"Fees ${float(pkpis['total_fees']):,.0f} | "
                f"Refunds ${float(pkpis['total_refunds']):,.0f}"
            )
            by_col = await PaymentRepository().get_by_collector(db, from_date=start, to_date=end)
            if by_col:
                lines.append("Pagos por cobrador: " + " | ".join(
                    f"{c['collector']}:{c['count']} ${float(c['total_amount']):,.0f}"
                    for c in by_col[:5]
                ))
            by_met = await PaymentRepository().get_by_method(db, from_date=start, to_date=end)
            if by_met:
                lines.append("Pagos por método: " + " | ".join(
                    f"{m['payment_method']}:{m['count']}" for m in by_met[:5]
                ))
        except Exception:
            pass

        try:
            dt_from = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
            dt_to = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=timezone.utc)
            ckpis = await CallAnalyticsRepository().get_kpis(db, dt_from, dt_to)
            total_calls = ckpis["total_calls"]
            answered = ckpis["total_answered"]
            pct = f"{answered/total_calls*100:.0f}%" if total_calls else "0%"
            lines.append(
                f"LLAMADAS: {total_calls} total | "
                f"Inbound:{ckpis['total_inbound']} | Outbound:{ckpis['total_outbound']} | "
                f"Contestadas:{answered} ({pct}) | Abandonadas:{ckpis['total_abandoned']} | "
                f"Duración total:{ckpis['total_duration_seconds']//60}min"
            )
        except Exception:
            pass

        context = "\n".join(lines)
        return context[: settings.OPENROUTER_MAX_CONTEXT_CHARS]

    def _build_messages(
        self, messages: list[ChatMessage], context: str
    ) -> list[dict[str, str]]:
        if len(messages) > settings.OPENROUTER_MAX_HISTORY:
            messages = messages[-settings.OPENROUTER_MAX_HISTORY :]

        system = self._SYSTEM_BASE + f"\n\nDatos actuales del negocio:\n{context}"

        return [{"role": "system", "content": system}] + [
            {"role": m.role, "content": m.content} for m in messages
        ]

    async def complete(self, req: ChatRequest, db: AsyncSession) -> ChatResponse:
        context = await self._build_db_context(db)
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=self._build_messages(req.messages, context),
                max_tokens=settings.OPENROUTER_MAX_TOKENS_OUT,
                stream=False,
            )
        except RateLimitError as exc:
            raise _http_error(429, "Rate limit exceeded") from exc
        except APITimeoutError as exc:
            raise _http_error(504, "OpenRouter timeout") from exc
        except APIStatusError as exc:
            raise _http_error(exc.status_code, exc.message) from exc
        except APIConnectionError as exc:
            raise _http_error(503, "OpenRouter unreachable") from exc

        choice = response.choices[0]
        return ChatResponse(
            message=ChatMessage(role="assistant", content=choice.message.content or ""),
            model=response.model,
        )

    async def stream(self, req: ChatRequest, db: AsyncSession) -> AsyncGenerator[str, None]:
        context = await self._build_db_context(db)
        try:
            async with await self._client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=self._build_messages(req.messages, context),
                max_tokens=settings.OPENROUTER_MAX_TOKENS_OUT,
                stream=True,
            ) as stream_response:
                async for chunk in stream_response:
                    delta = chunk.choices[0].delta.content
                    if delta is not None:
                        yield f"data: {ChatChunk(delta=delta).model_dump_json()}\n\n"
        except RateLimitError as exc:
            yield f"data: {json.dumps({'error': 'rate_limit', 'detail': str(exc)})}\n\n"
        except APIStatusError as exc:
            yield f"data: {json.dumps({'error': 'api_error', 'status': exc.status_code, 'detail': exc.message})}\n\n"
        except (APIConnectionError, APITimeoutError) as exc:
            yield f"data: {json.dumps({'error': 'connection_error', 'detail': str(exc)})}\n\n"
        finally:
            yield f"data: {ChatChunk(delta='', done=True).model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"


def _http_error(status_code: int, detail: str) -> Exception:
    from fastapi import HTTPException
    return HTTPException(status_code=status_code, detail=f"OpenRouter: {detail}")
