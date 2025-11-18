import time
import threading
from roble_client import RobleClient
import subprocess

class ActivityMonitor:
    def __init__(self):
        self.token = None
        self.running = False
        self.client = RobleClient()

    # ======================================================
    # ======== TOKEN enviado desde FRONTEND ================
    # ======================================================

    def set_token(self, token):
        print("🔐 Monitor recibió token válido.")
        self.token = token
        if not self.running:
            self.start()

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
                self.client.verify_token(self.token)
            except:
                print("❌ Token inválido. Monitor pausado.")
                self.token = None
                continue

            time.sleep(5)


monitor = ActivityMonitor()
