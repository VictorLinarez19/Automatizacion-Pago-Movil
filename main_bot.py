import logging

from src.database.operations import setup_db
from src.bot.whatsapp_bot import iniciar_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    setup_db()
    logger.info("Base de datos inicializada. Iniciando bot de WhatsApp...")
    iniciar_bot()


if __name__ == "__main__":
    main()
