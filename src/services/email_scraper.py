import re
import os
import sqlite3
import logging

from dotenv import load_dotenv
from imap_tools import MailBox, AND

from src.database.operations import guardar_pago

load_dotenv()
logger = logging.getLogger(__name__)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_SERVER = os.getenv("EMAIL_SERVER")

REMITENTE_BANCAMIGA = "no-reply@bancamiga.com"
ASUNTO_PAGO = "Notificación de BANCAMIGA en línea"

RE_REFERENCIA = re.compile(r"Ref\.\s*(\d{6,12})")
RE_MONTO = re.compile(r"por\s+([\d.,]+)")
RE_EMISOR = re.compile(r"Estimado\s+Sr\(a\)\.\s+(.+?)\s+El\b", re.IGNORECASE)


def _html_a_texto(html: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", texto).strip()


def _extraer_datos(cuerpo: str) -> dict | None:
    ref_match = RE_REFERENCIA.search(cuerpo)
    monto_match = RE_MONTO.search(cuerpo)
    emisor_match = RE_EMISOR.search(cuerpo)

    if not ref_match or not monto_match:
        return None

    referencia = ref_match.group(1)

    monto_str = monto_match.group(1).replace(".", "").replace(",", ".")
    try:
        monto = float(monto_str)
    except ValueError:
        return None

    emisor = emisor_match.group(1).strip() if emisor_match else "Desconocido"

    return {"referencia": referencia, "monto": monto, "emisor": emisor}


def check_emails():
    if not all([EMAIL_USER, EMAIL_PASS, EMAIL_SERVER]):
        logger.error("Faltan variables de entorno EMAIL_USER, EMAIL_PASS o EMAIL_SERVER")
        return

    logger.info("Conectando a %s como %s...", EMAIL_SERVER, EMAIL_USER)

    with MailBox(EMAIL_SERVER).login(EMAIL_USER, EMAIL_PASS) as mailbox:
        correos = mailbox.fetch(AND(from_=REMITENTE_BANCAMIGA))

        procesados = 0
        for msg in correos:
            if msg.subject != ASUNTO_PAGO:
                continue

            cuerpo = msg.text or ""
            if not cuerpo and msg.html:
                cuerpo = _html_a_texto(msg.html)

            if not cuerpo:
                logger.warning("Correo sin cuerpo: %s", msg.subject)
                continue

            if "Pago Móvil" not in cuerpo and "Pago M\u00f3vil" not in cuerpo:
                continue

            datos = _extraer_datos(cuerpo)

            if datos is None:
                logger.warning("No se pudo extraer datos del correo: '%s'", msg.subject)
                continue

            try:
                guardar_pago(datos["referencia"], datos["monto"], datos["emisor"])
                procesados += 1
                logger.info("Pago guardado — ref: %s, monto: %.2f, emisor: %s",
                            datos["referencia"], datos["monto"], datos["emisor"])
            except sqlite3.IntegrityError:
                logger.debug("Referencia %s ya existe, ignorada", datos["referencia"])

        logger.info("Ciclo finalizado: %d pago(s) nuevo(s) procesado(s)", procesados)
