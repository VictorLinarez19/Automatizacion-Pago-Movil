from datetime import datetime

from src.database.connection import DatabaseConnection


def setup_db():
    conn = DatabaseConnection().connection
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            referencia TEXT PRIMARY KEY,
            monto      REAL,
            emisor     TEXT,
            fecha_proceso TIMESTAMP
        )
    """)
    conn.commit()


def guardar_pago(referencia: str, monto: float, emisor: str):
    conn = DatabaseConnection().connection
    conn.execute(
        "INSERT INTO pagos (referencia, monto, emisor, fecha_proceso) VALUES (?, ?, ?, ?)",
        (referencia, monto, emisor, datetime.now()),
    )
    conn.commit()


def buscar_pago(referencia: str) -> dict | None:
    conn = DatabaseConnection().connection
    row = conn.execute(
        "SELECT referencia, monto, emisor, fecha_proceso FROM pagos WHERE referencia = ?",
        (referencia,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)
