import requests
import os
from datetime import datetime

class RobleClient:
    def __init__(self):
        self.BASE = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.CONTRACT = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")

    # ============================================================
    # ========================= LOGIN =============================
    # ============================================================

    def login(self, email, password):
        url = f"{self.BASE}/auth/{self.CONTRACT}/login"
        response = requests.post(url, json={"email": email, "password": password})
        response.raise_for_status()
        return response.json()

    # ============================================================
    # ======================= VALIDAR TOKEN =======================
    # ============================================================

    def verify_token(self, access_token):
        url = f"{self.BASE}/auth/{self.CONTRACT}/verify-token"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    # ============================================================
    # ===================== READ RECORDS ==========================
    # ============================================================

    def read_records(self, table_name, filters=None, access_token=None):
            """
            Lee registros usando table-data (API estándar de Roble)
            GET /database/{contract}/table-data
            """

            url = f"{self.BASE}/database/{self.CONTRACT}/table-data"
            headers = {"Authorization": f"Bearer {access_token}"}

            params = {
                "schema": "public",
                "table": table_name
            }

            # Roble NO soporta filtros a nivel API.
            # Filtramos después, en Python.
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()

            records = resp.json().get("records", [])

            # Filtrar en Python
            if filters:
                for key, value in filters.items():
                    records = [r for r in records if r.get(key) == value]

            return records


    # ============================================================
    # ==================== CREATE PROJECT =========================
    # ============================================================

    def create_project(self, user_id, name, rep_url, access_token):
        """
        Crea un proyecto usando exactamente los nombres de columnas
        de tu tabla Roble.
        """

        url = f"{self.BASE}/database/{self.CONTRACT}/insert"
        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {
            "tableName": "proyectos",
            "records": [{
                "user_id": user_id,
                "name": name,
                "rep_url": rep_url,
                "status": "created",
                "container_id": None,
                "created_at": datetime.utcnow().isoformat(),
                "last_access": datetime.utcnow().isoformat()
            }]
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        data = resp.json()
        if not data.get("inserted"):
            raise Exception(f"Error insertando proyecto en Roble: {data}")

        return data["inserted"][0]

    # ============================================================
    # ================= UPDATE PROJECT STATUS =====================
    # ============================================================

    def update_project_status(self, project_id, status, container_id=None, access_token=None):
        url = f"{self.BASE}/database/{self.CONTRACT}/update"
        headers = {"Authorization": f"Bearer {access_token}"}

        updates = {"status": status}

        if container_id:
            updates["container_"] = container_id

        payload = {
            "tableName": "proyectos",
            "idColumn": "_id",
            "idValue": project_id,
            "updates": updates
        }

        resp = requests.put(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()
