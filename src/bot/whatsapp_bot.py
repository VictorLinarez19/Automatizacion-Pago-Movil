import re
import os
import logging

from dotenv import load_dotenv
from whatsapp_api_client_python import API

from src.database.operations import buscar_pago

load_dotenv()
logger = logging.getLogger(__name__)

ID_INSTANCE = os.getenv("ID_INSTANCE")
API_TOKEN_INSTANCE = os.getenv("API_TOKEN_INSTANCE")

RE_REFERENCIA = re.compile(r"(\d{6,12})")

greenAPI = API.GreenAPI(ID_INSTANCE, API_TOKEN_INSTANCE)


def _construir_respuesta(referencia: str) -> str:
    pago = buscar_pago(referencia)

    if pago:
        return (
            f"✅ ¡Pago Verificado!\n"
            f"💰 Monto: {pago['monto']:.2f} Bs.\n"
            f"👤 Emisor: {pago['emisor']}."
        )

    return (
        f"❌ No encontramos la referencia {referencia}. "
        f"Intenta de nuevo en unos minutos o verifica los datos."
    )


def _procesar_mensaje(body: dict) -> None:
    message_data = body.get("messageData", {})
    tipo = message_data.get("typeMessage", "")

    if tipo == "textMessage":
        texto = message_data.get("textMessageData", {}).get("textMessage", "")
    elif tipo == "extendedTextMessage":
        texto = message_data.get("extendedTextMessageData", {}).get("text", "")
    else:
        return

    chat_id = body.get("senderData", {}).get("chatId", "")
    logger.info("Mensaje recibido de %s — tipo: %s — texto: '%s'", chat_id, tipo, texto)

    if not chat_id or not texto:
        return

    match = RE_REFERENCIA.search(texto)
    if not match:
        logger.info("No se encontró referencia numérica en el mensaje")
        return

    referencia = match.group(1)
    logger.info("Referencia extraída: %s — buscando en BD...", referencia)

    respuesta = _construir_respuesta(referencia)
    greenAPI.sending.sendMessage(chat_id, respuesta)
    logger.info("Respuesta enviada a %s", chat_id)


def handler(type_webhook: str, body: dict) -> None:
    logger.info("Webhook recibido — tipo: %s", type_webhook)
    if type_webhook == "incomingMessageReceived":
        try:
            _procesar_mensaje(body)
        except Exception:
            logger.exception("Error procesando mensaje entrante")


def iniciar_bot():
    if not all([ID_INSTANCE, API_TOKEN_INSTANCE]):
        logger.error("Faltan variables de entorno ID_INSTANCE o API_TOKEN_INSTANCE")
        return

    logger.info("Bot de WhatsApp iniciado. Escuchando mensajes...")
    greenAPI.webhooks.startReceivingNotifications(handler)
