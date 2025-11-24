import requests
import os

class RobleClient:
    def __init__(self):
        self.BASE = os.getenv("ROBLE_URL", "https://roble-api.openlab.uninorte.edu.co")
        self.CONTRACT = os.getenv("ROBLE_CONTRACT", "pc2_394e10a6d2")

    # ============================================================
    # ========================= SIGNUP ============================
    # ============================================================

    def signup_direct(self, email, password, name):
        url = f"{self.BASE}/auth/{self.CONTRACT}/signup-direct"
        resp = requests.post(url, json={
            "email": email,
            "password": password,
            "name": name
        })
        resp.raise_for_status()
        return resp.json()

    # ============================================================
    # ========================= LOGIN =============================
    # ============================================================

    def login(self, email, password):
        url = f"{self.BASE}/auth/{self.CONTRACT}/login"
        response = requests.post(url, json={"email": email, "password": password})
        response.raise_for_status()
        return response.json()

    # ============================================================
    # ======================= VALIDAR TOKEN ========================
    # ============================================================

    def verify_token(self, access_token):
        """Roble usa /auth/me, NO usa contrato."""
        url = f"{self.BASE}/auth/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()["user"]

    # ============================================================
    # ==================== READ RECORDS ===========================
    # ============================================================

    def read_records(self, table, filters, access_token):
        url = f"{self.BASE}/db/{self.CONTRACT}/{table}/read"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.post(url, json={"filters": filters}, headers=headers)
        resp.raise_for_status()
        return resp.json()["results"]

    # ============================================================
    # =================== GET USER PROJECTS =======================
    # ============================================================

    def get_user_projects(self, user_id, access_token):
        """Filtra por user_id dentro de la tabla proyectos."""
        return self.read_records(
            "proyectos",
            filters={"user_id": user_id},
            access_token=access_token
        )

    # ============================================================
    # =================== CREATE PROJECT ==========================
    # ============================================================

    def create_project(self, user_id, name, repo_url, access_token):
        url = f"{self.BASE}/db/{self.CONTRACT}/proyectos/create"
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.post(url, json={
            "user_id": user_id,
            "name": name,
            "repo_url": repo_url,
            "status": "created"
        }, headers=headers)
        resp.raise_for_status()
        return resp.json()

    # ============================================================
    # =================== UPDATE PROJECT STATUS ===================
    # ============================================================

    def update_project_status(self, project_id, status, container_id=None, access_token=None):
        url = f"{self.BASE}/db/{self.CONTRACT}/proyectos/update"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"_id": project_id, "status": status}

        if container_id:
            data["container_id"] = container_id

        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()
