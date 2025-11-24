import requests
import os
from datetime import datetime


class RobleClient:

    def __init__(self):
        self.BASE = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.CONTRACT = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")

    # SIGNUP
    def signup_direct(self, email, password, name):
        url = f"{self.BASE}/auth/{self.CONTRACT}/signup-direct"
        resp = requests.post(url, json={
            "email": email,
            "password": password,
            "name": name
        })
        resp.raise_for_status()
        return resp.json()
    # LOGIN
    def login(self, email, password):
        url = f"{self.BASE}/auth/{self.CONTRACT}/login"
        resp = requests.post(url, json={"email": email, "password": password})
        resp.raise_for_status()
        return resp.json()

    # VERIFY TOKEN
    def verify_token(self, token):
        url = f"{self.BASE}/auth/{self.CONTRACT}/verify-token"
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        resp.raise_for_status()
        return resp.json()

    # READ (FORMA CORRECTA)
    def read_records(self, table_name, filters=None, access_token=None):
        url = f"{self.BASE}/database/{self.CONTRACT}/read"

        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        resp = requests.get(url, headers=headers, params={"tableName": table_name})
        resp.raise_for_status()

        data = resp.json()

        # Filtrar manualmente (Roble no admite filtros aquí)
        if filters:
            filtered = []
            for row in data:
                if all(row.get(k) == v for k, v in filters.items()):
                    filtered.append(row)
            return filtered

        return data

    # CREATE PROJECT
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
