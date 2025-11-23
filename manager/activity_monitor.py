import time
import threading
import os
import requests
import logging

logger = logging.getLogger(__name__)

class ActivityMonitor:
    def __init__(self):
        self.token = None
        self.running = False

        # Leemos SIEMPRE del .env
        self.base_url = os.getenv(
            "ROBLE_URL",
            "https://roble-api.openlab.uninorte.edu.co"
        )
        self.contract = os.getenv(
            "ROBLE_CONTRACT",
            "pc2_394e10a6d2"  # default: el contrato que dijiste
        )

    # ======================================================
    # ======== TOKEN enviado desde FRONTEND ================
    # ======================================================

    def set_token(self, token: str):
        """
        Recibe el accessToken desde el backend (/auth/use_token)
        y lo guarda en el monitor.
        """
        self.token = token
        logger.info(
            f"🔐 Monitor recibió token. Usando contrato '{self.contract}'."
        )

        if not self.running:
            self.start()

    # ======================================================
    # ==================== LOOP =============================
    # ======================================================

    def start(self):
        if self.running:
            return

        logger.info("▶ Monitor iniciado.")
        self.running = True

        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        while self.running:
            if not self.token:
                logger.warning("⚠ Monitor sin token, esperando login...")
                time.sleep(5)
                continue

            try:
                url = f"{self.base_url}/auth/{self.contract}/verify-token"
                resp = requests.get(
                    url,
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10,
                )

                if resp.status_code == 200:
                    logger.info("✅ Token válido (monitor).")
                else:
                    logger.error(
                        "❌ Token inválido en monitor. status=%s body=%s",
                        resp.status_code,
                        resp.text[:200],
                    )
                    # Dejamos el monitor sin token hasta que el usuario vuelva a loguearse
                    self.token = None

            except Exception as e:
                logger.error(f"❌ Error verificando token en monitor: {e}")
                self.token = None

            time.sleep(10)


# Instancia global
monitor = ActivityMonitor()
