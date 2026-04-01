import time
import logging

from src.database.operations import setup_db
from src.services.email_scraper import check_emails

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

INTERVALO_SEGUNDOS = 60


def main():
    setup_db()
    logger.info("Base de datos inicializada. Iniciando scraper de correos...")

    while True:
        try:
            check_emails()
        except Exception:
            logger.exception("Error durante la revisión de correos")

        logger.info("Esperando %d segundos para la próxima revisión...", INTERVALO_SEGUNDOS)
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    main()
