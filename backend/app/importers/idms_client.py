"""Cliente de sesión/autenticación y extracción de reportes de IDMS."""

from __future__ import annotations

import html as htmlmod
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, urlparse

import requests

from app.core.config import settings
from .idms_session_store import IdmsSessionStore


class MfaRequired(Exception):
    """Se alcanzó el paso OTP; se requiere código de la app autenticadora."""

    def __init__(self, message: str):
        self.message = message


class IdmsClient:
    """Cliente HTTP para IDMS (DealerSocket) con sesión persistente."""

    def __init__(
        self,
        session_store: Optional[IdmsSessionStore] = None,
    ):
        self.session = requests.Session()
        self.ua = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        self.session.headers.update({"User-Agent": self.ua})
        parsed = urlparse(settings.idms_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"
        self.solera_base = "https://na.login.solera.com/soleranab2b.onmicrosoft.com/B2C_1A_HRDSignIn_NS"
        self.store = session_store or IdmsSessionStore()

    # ------------------------------------------------------------------
    # Config expuesta como property para compatibilidad
    # ------------------------------------------------------------------
    @property
    def settings(self):
        return settings

    # ------------------------------------------------------------------
    # Sesión
    # ------------------------------------------------------------------
    def load_session(self) -> bool:
        if not self.store:
            return False
        data = self.store.load()
        if not data or "cookies" not in data:
            return False
        for name, value in data["cookies"].items():
            self.session.cookies.set(name, value, domain="idms.dealersocket.com")
        return True

    def save_session(self) -> None:
        if not self.store:
            return
        cookies = {
            c.name: c.value
            for c in self.session.cookies
            if "dealersocket" in (c.domain or "")
        }
        self.store.save(cookies, ttl_days=30)

    def is_authenticated(self) -> bool:
        """Verifica rápidamente si la sesión guardada sigue viva."""
        r = self.session.get(
            f"{self.base_url}/LaunchPad/Main/Home", allow_redirects=False, timeout=20
        )
        return r.status_code == 200 and "LoginFormElement" not in r.text

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    def login(self, otp_code: Optional[str] = None) -> bool:
        """
        Inicia sesión en IDMS. Si ya hay sesión válida la reutiliza.
        Si se necesita MFA y no se pasa otp_code se lanza MfaRequired.
        """
        if self.load_session() and self.is_authenticated():
            return True

        # Limpiar cookies previas para un login limpio
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.ua})

        try:
            self._do_login(otp_code)
        except MfaRequired:
            raise
        except Exception as exc:
            raise RuntimeError(f"Error en login IDMS: {exc}") from exc

        self.save_session()
        return True

    def _do_login(self, otp_code: Optional[str] = None):
        def _extract_url(text):
            """Busca una URL http/https en el HTML, o devuelve None."""
            m = re.search(r"https?://[^\s\"\'<>]+", text)
            return m.group(0) if m else None

        # 1. CSRF de IDMS
        r1 = self.session.get(f"{self.base_url}/", timeout=30)
        csrf_match = re.search(
            r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', r1.text
        )
        if not csrf_match:
            raise RuntimeError("No se pudo obtener el token CSRF de IDMS")
        idms_csrf = csrf_match.group(1)

        # 2. POST credenciales
        r2 = self.session.post(
            f"{self.base_url}/",
            data={
                "UserName": settings.IDMS_USERNAME,
                "Password": settings.IDMS_PASSWORD,
                "RememberMe": "true",
                "__RequestVerificationToken": idms_csrf,
            },
            allow_redirects=False,
            timeout=30,
        )
        authorize_url = r2.headers.get("Location")

        if not authorize_url or not authorize_url.startswith("http"):
            extracted = _extract_url(r2.text)
            if extracted:
                authorize_url = extracted
            else:
                raise RuntimeError(
                    "IDMS no redirigió a una URL válida después del POST de login"
                )

        # El comportamiento de IDMS es inconsistente: a veces redirige directo a
        # Solera, a veces a /Security/Login. Si es /Security/Login, obtenemos CSRF
        # y posteamos de nuevo para llegar a Solera.
        if "Security/Login" in authorize_url:
            r2b = self.session.get(authorize_url, timeout=30)
            csrf_match2 = re.search(
                r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', r2b.text
            )
            if not csrf_match2:
                raise RuntimeError("No se pudo obtener el token CSRF de /Security/Login")
            security_csrf = csrf_match2.group(1)
            r2c = self.session.post(
                r2b.url,
                data={
                    "UserName": settings.IDMS_USERNAME,
                    "Password": settings.IDMS_PASSWORD,
                    "RememberMe": "true",
                    "__RequestVerificationToken": security_csrf,
                },
                allow_redirects=False,
                timeout=30,
            )
            authorize_url = r2c.headers.get("Location")
            if not authorize_url or not authorize_url.startswith("http"):
                extracted = _extract_url(r2c.text)
                if extracted:
                    authorize_url = extracted
                else:
                    raise RuntimeError(
                        "IDMS no redirigió a Solera B2C desde /Security/Login"
                    )

        # 3. Página de autorización Solera
        r3 = self.session.get(authorize_url, timeout=30)
        trans, csrf = self._parse_b2c_page(r3.text)
        referer = r3.url

        # 4. SelfAsserted: credenciales
        self._b2c_self_asserted(trans, csrf, referer, {
            "signInName": settings.IDMS_USERNAME,
            "password": settings.IDMS_PASSWORD,
        })

        # 5. confirmed → página de device
        r5 = self._b2c_confirmed(trans, csrf, referer)
        trans2, csrf2 = self._parse_b2c_page(r5.text)

        # 6. SelfAsserted: device key
        device_key = settings.IDMS_DEVICE_KEY
        client_key_api = settings.IDMS_CLIENT_KEY_API
        payload = {"userAgent": self.ua}
        if device_key:
            payload["clientKeyFromDevice"] = device_key
        self._b2c_self_asserted(trans2, csrf2, referer, payload)

        # 7. confirmed → página OTP
        r7 = self._b2c_confirmed(trans2, csrf2, referer)
        if "otpCode" not in r7.text:
            # No requiere OTP (dispositivo reconocido)
            trans3, csrf3 = self._parse_b2c_page(r7.text)
            self._finish_login(trans3, csrf3, referer)
            return

        if not otp_code:
            raise MfaRequired("Se requiere código MFA de la app autenticadora")

        trans3, csrf3 = self._parse_b2c_page(r7.text)

        # 8. SelfAsserted: OTP
        otp_payload = {
            "otpCode": otp_code,
            "rememberDeviceInformation": "True",
        }
        if client_key_api:
            otp_payload["clientKeyFromApi"] = client_key_api
        self._b2c_self_asserted(trans3, csrf3, referer, otp_payload)

        # 9. confirmed final → form POST a IDMS
        self._finish_login(trans3, csrf3, referer)

    def _b2c_self_asserted(self, trans: str, csrf: str, referer: str, data: dict):
        r = self.session.post(
            f"{self.solera_base}/SelfAsserted",
            params={"tx": trans, "p": "B2C_1A_HRDSignIn_NS"},
            headers={"X-CSRF-TOKEN": csrf, "Referer": referer},
            data={"request": "", **data},
            timeout=30,
        )
        if '"status":"200"' not in r.text:
            raise RuntimeError(f"SelfAsserted falló: {r.text[:400]}")
        return r

    def _b2c_confirmed(self, trans: str, csrf: str, referer: str):
        return self.session.get(
            f"{self.solera_base}/api/CombinedSigninAndSignup/confirmed",
            params={
                "rememberMe": "true",
                "csrf_token": csrf,
                "tx": trans,
                "p": "B2C_1A_HRDSignIn_NS",
            },
            headers={"Referer": referer},
            timeout=30,
        )

    def _finish_login(self, trans: str, csrf: str, referer: str):
        r = self._b2c_confirmed(trans, csrf, referer)
        # Busca form de auto-submit a /Security/SignInWithMFA
        m = re.search(r'<form[^>]*action=[\'"]([^\'"]+)[\'"]', r.text, re.I)
        if not m:
            raise RuntimeError("No se encontró el form de callback a IDMS")
        action = m.group(1)
        if not action.startswith("http"):
            raise RuntimeError(f"El form de callback a IDMS no tiene URL válida: {action}")
        fields = {}
        for tag in re.findall(r'<input[^>]*>', r.text):
            name = re.search(r'name=[\'"]([^\'"]+)[\'"]', tag)
            value = re.search(r'value=[\'"]([^\'"]*)[\'"]', tag)
            if name:
                fields[name.group(1)] = value.group(1) if value else ""
        r_final = self.session.post(action, data=fields, timeout=30, allow_redirects=True)
        if "LoginFormElement" in r_final.text:
            raise RuntimeError("No se pudo completar el login en IDMS")

    @staticmethod
    def _parse_b2c_page(html: str) -> Tuple[str, str]:
        trans = re.search(r'"transId"\s*:\s*"([^"]+)"', html)
        csrf = re.search(r'"csrf"\s*:\s*"([^"]+)"', html)
        if not trans or not csrf:
            raise RuntimeError("No se pudo parsear la página B2C")
        return trans.group(1), csrf.group(1)

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def list_reports(self) -> List[Dict[str, str]]:
        """Devuelve lista de reportes personalizados de IDMS."""
        r = self.session.get(
            f"{self.base_url}/pages/report/_report_list_reports.aspx",
            params={
                "qreporttype_id": "1",
                "qowner_id": "0",
                "qcatagory_id": "-1",
                "qreportname": "",
            },
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{self.base_url}/Reports/Main?reportType=1",
            },
            timeout=30,
        )
        reports = re.findall(r"rpt_executereport\((\d+),\s*'([^']+)'", r.text)
        seen = set()
        out = []
        for rid, name in reports:
            if rid not in seen:
                seen.add(rid)
                out.append({"id": rid, "name": name})
        return out

    def execute_report(self, report_id: str) -> dict:
        """Genera un reporte y devuelve el efile_guid junto con URLs de visor."""
        # 1. GET form de ejecución
        url = f"{self.base_url}/pages/report/_report_execute.aspx"
        r1 = self.session.get(url, params={"qreport_id": report_id}, timeout=30)

        fields = self._extract_execute_form(r1.text)
        if not fields:
            raise RuntimeError("No se pudo extraer el formulario de ejecución")

        # Algunos reportes (especialmente MySQL/AutoAnalytix) no rellenan
        # el campo txtReport_ID__report_execute en el HTML del GET.
        fields["txtReport_ID__report_execute"] = report_id

        # 2. POST para generar request
        r2 = self.session.post(f"{url}?qreport_id={report_id}", data=fields, timeout=120)

        request_id = self._extract_request_id(r2.text)
        if not request_id:
            raise RuntimeError("No se generó request_id para el reporte")

        # 3. Monitorear hasta obtener efile_guid
        efile_guid = self._wait_for_efile_guid(request_id)
        if not efile_guid:
            raise RuntimeError("El reporte no terminó de generarse")

        return {
            "request_id": request_id,
            "efile_guid": efile_guid,
            "viewer_urls": self.viewer_urls(efile_guid),
        }

    def viewer_urls(self, efile_guid: str) -> Dict[str, str]:
        """URLs útiles para ver el reporte generado."""
        rdlc = (
            f"{self.base_url}/reportviewer_v11/report11/report_viewer_rdlc.aspx"
            f"?qstandalone=1&qefile_guid={efile_guid}&qexport_id=0&qdebug=0"
        )
        r2 = (
            f"{self.base_url}/reportviewer_v11/report11/report_viewer_r2.aspx"
            f"?qstandalone=1&qefile_guid={efile_guid}&qexport_id=0&qdebug=0"
        )
        exago = (
            f"{self.base_url}/pages/report/_report_viewer_exago2.aspx"
            f"?qstandalone=1&qefile_guid={efile_guid}&qexport_id=0&qdebug=0"
        )
        grid = f"{self.base_url}/pages/report/_report_viewer_grid.aspx?qEFile_GUID={efile_guid}"
        return {
            "rdlc": rdlc,
            "r2": r2,
            "exago": exago,
            "grid": grid,
            "rdlc_proxy": f"/api/proxy/?target={quote(rdlc, safe='')}",
            "exago_proxy": f"/api/proxy/?target={quote(exago, safe='')}",
        }

    def export_csv(self, report_id: str, export_type: str = "csv") -> bytes:
        """Exporta un reporte IDMS vía el visor Exago (wrajax) a CSV/Excel."""
        result = self.execute_report(report_id)
        r = self.session.get(result["viewer_urls"]["exago"], timeout=60)

        m = re.search(r"https://idms\.dealersocket\.com/exago/dshome\.aspx\?[^'\" ]+", r.text)
        if not m:
            raise RuntimeError("No se encontró la URL de Exago dshome")
        dshome_url = m.group(0).replace("&amp;", "&")

        r2 = self.session.get(dshome_url, timeout=60)
        m2 = re.search(r'name="WebReportsCtrl\$wrSettings"[^>]*value="([^"]+)"', r2.text)
        if not m2:
            raise RuntimeError("No se encontró wrSettings en Exago")
        exago_settings = json.loads(htmlmod.unescape(m2.group(1)))

        temp_path = exago_settings.get("TempPath") or exago_settings.get("EncryptedTempPath")
        ajax_settings = {
            k: exago_settings[k]
            for k in ["Language", "SessionNum", "ShowErrorDetail", "IsAdmin", "CultureInfo"]
            if k in exago_settings
        }

        def post(method: str, args: list) -> dict:
            url = f"https://idms.dealersocket.com/exago/wrajax/{method}.ashx?t={temp_path}"
            body = {
                "args": args + [{"className": "Settings", "value": json.dumps(ajax_settings)}]
            }
            resp = self.session.post(
                url,
                data=json.dumps(body),
                headers={
                    "Content-Type": "text/plain; charset=utf-8",
                    "X-Requested-With": "XMLHttpRequest",
                },
                timeout=60,
            )
            return resp.json()

        load_resp = post(
            "Client.BaseExecuteCtrl.LoadCallback",
            [
                {"className": "", "value": exago_settings["ApiReportId"]},
                {"className": "", "value": export_type},
                {"className": "", "value": True},
                {"className": "", "value": True},
                {"className": "", "value": ""},
            ],
        )
        report_data = load_resp["value"]["Data"]["ReportData"]

        start_resp = post(
            "Callbacks.Execute.StartExecute",
            [
                {"className": "", "value": report_data},
                {"className": "", "value": ""},
                {"className": "", "value": None},
                {"className": "Client.ClientParameterValueList", "value": "null"},
                {"className": "", "value": export_type},
                {"className": "", "value": True},
                {"className": "Client.ClientReportAdjustments", "value": "null"},
                {"className": "Client.ClientJsApiExecuteReportFiltersList", "value": "null"},
                {"className": "Client.ClientJsApiPromptingFilterValueList", "value": "null"},
                {"className": "Client.ClientJsApiPromptingFilterValueList", "value": "null"},
            ],
        )
        execution_id = start_resp["value"]["ExecutionId"]

        # Esperar a que termine (phase=4 = Success)
        for _ in range(30):
            status_resp = post(
                "Callbacks.Execute.GetStatus",
                [
                    {"className": "", "value": temp_path},
                    {"className": "", "value": execution_id},
                    {"className": "", "value": True},
                ],
            )
            val = status_resp.get("value", {})
            if val.get("phase") == 4 or val.get("jobStatus") == 2:
                break
            if val.get("jobStatus") == 5:
                raise RuntimeError(f"Error ejecutando reporte Exago: {val.get('statusMessage')}")
            time.sleep(1)
        else:
            raise RuntimeError("Timeout esperando reporte Exago")

        download_url = (
            f"https://idms.dealersocket.com/exago/ExecuteExport.aspx"
            f"?eid={execution_id}&bt=Chrome&l={exago_settings['Language']}"
            f"&sn={exago_settings['SessionNum']}&t={temp_path}"
        )
        r3 = self.session.get(download_url, timeout=120)
        r3.raise_for_status()
        return r3.content

    def _extract_execute_form(self, html: str) -> Optional[Dict[str, str]]:
        fields: Dict[str, str] = {}
        for tag in re.findall(r'<input[^>]*>', html):
            name = re.search(r'name="([^"]+)"', tag)
            value = re.search(r'value="([^"]*)"', tag)
            if name:
                val = value.group(1) if value else ""
                if name.group(1) == "txtReportXML__report_execute":
                    val = htmlmod.unescape(val)
                fields[name.group(1)] = val
        for tag in re.findall(r'<textarea[^>]*name="([^"]+)"[^>]*>(.*?)</textarea>', html, re.S):
            fields[tag[0]] = htmlmod.unescape(tag[1])
        if "txtReportXML__report_execute" not in fields:
            return None
        return fields

    @staticmethod
    def _extract_request_id(html: str) -> Optional[str]:
        m = re.search(r'rpt_loadviewer\s*\(\s*2\s*,\s*(\d+)\s*\)', html)
        return m.group(1) if m else None

    def _wait_for_efile_guid(self, request_id: str, max_wait: int = 120) -> Optional[str]:
        url = f"{self.base_url}/pages/report/_report_monitor.aspx"
        deadline = time.time() + max_wait
        while time.time() < deadline:
            r = self.session.get(url, params={"qrequest_id": request_id}, timeout=30)
            m = re.search(r"rpt_loadviewer\s*\(\s*3\s*,\s*['\"]([0-9a-f-]+)['\"]\s*\)", r.text)
            if m:
                return m.group(1)
            lower = r.text.lower()
            if any(phrase in lower for phrase in ["an error occurred", "failed to generate", "unable to process"]):
                raise RuntimeError("Error en la generación del reporte")
            time.sleep(2)
        return None
