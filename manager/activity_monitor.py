import time
import threading
import requests
import os
from roble_client import RobleClient

class ActivityMonitor:
    def __init__(self):
        self.token = None
        self.running = False
        self.client = RobleClient()

        # Cargar contrato y base URL desde variables de entorno
        self.ROBLE_URL = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.CONTRACT = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")

        # Endpoint correcto
        self.verify_url = f"{self.ROBLE_URL}/auth/{self.CONTRACT}/verify-token"

    # ======================================================
    # =============== TOKEN DESDE FRONTEND =================
    # ======================================================
    
    def set_token(self, token):
        print("🔐 Monitor recibió token válido.")
        self.token = token

        if not self.running:
            self.start()

        print("🔐 Token aplicado correctamente al Monitor.")

    # ======================================================
    # ==================== LOOP =============================
    # ======================================================

    def start(self):
        if self.running:
            return
        
        print("▶ Monitor iniciado.")
        self.running = True

        thread = threading.Thread(target=self.loop, daemon=True)
        thread.start()

    def loop(self):
        while self.running:
            if not self.token:
                print("⚠ Monitor sin token, esperando login...")
                time.sleep(3)
                continue

            try:
                r = requests.get(
                    self.verify_url,
                    headers={"Authorization": f"Bearer {self.token}"}
                )

                if r.status_code != 200:
                    print(f"❌ Token inválido ({r.status_code}). Monitor pausado.")
                    self.token = None
                    continue

            except Exception as e:
                print(f"❌ Error verificando token: {e}")
                self.token = None
                continue

            time.sleep(5)


monitor = ActivityMonitor()
