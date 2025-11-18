"""
Servicio encargado del despliegue de proyectos:
 - Clonar repositorio
 - Construir imagen Docker
 - Ejecutar contenedor
 - Actualizar estado en la base de datos Roble
"""

import os
import subprocess
import random
import shutil
import logging

from roble_client import RobleClient

logger = logging.getLogger(__name__)

class DeployService:

    def __init__(self):
        self.roble = RobleClient()
        self.workdir = "/tmp/hosting_repos"

        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

    # =============================================================
    # ====================== CLONAR REPO ==========================
    # =============================================================

    def clonar_repo(self, repo_url: str, project_id: str):
        """
        Clona el repositorio dentro de /tmp/hosting_repos.
        """
        target = f"{self.workdir}/{project_id}"

        # Eliminar si existe
        if os.path.exists(target):
            shutil.rmtree(target)

        logger.info(f"📥 Clonando repo: {repo_url}")

        try:
            subprocess.check_call(["git", "clone", repo_url, target])
            return target
        except subprocess.CalledProcessError:
            raise Exception("Error clonando el repositorio (¿URL inválida?)")

    # =============================================================
    # ==================== CONSTRUIR IMAGEN =======================
    # =============================================================

    def construir_imagen(self, repo_path: str, project_id: str):
        """
        Construye la imagen Docker del proyecto.
        """
        image_name = f"hosting_{project_id}"

        logger.info(f"📦 Construyendo imagen: {image_name}")

        try:
            subprocess.check_call([
                "docker", "build",
                "-t", image_name,
                repo_path
            ])
            return image_name
        except subprocess.CalledProcessError:
            raise Exception("Error construyendo la imagen Docker")

    # =============================================================
    # ====================== PUERTO SEGURO =========================
    # =============================================================

    def obtener_puerto(self):
        """
        Asigna un puerto aleatorio evitando colisiones.
        """
        while True:
            port = random.randint(3000, 9000)
            result = subprocess.run(
                ["lsof", "-i", f":{port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                return port

    # =============================================================
    # ===================== DESPLEGAR PROYECTO ====================
    # =============================================================

    def desplegar(self, project_id: str, repo_url: str, token: str):
        """
        Flujo completo de despliegue:
         1. Clonar repositorio
         2. Construir imagen Docker
         3. Asignar puerto
         4. Ejecutar contenedor
         5. Registrar en Roble DB
         6. Actualizar estado final
        """
        logger.info(f"🚀 Iniciando despliegue del proyecto {project_id}")

        # Actualizar estado a "building"
        self.roble.update_project_status(project_id, "building", access_token=token)

        try:
            # Clonar repositorio
            repo_path = self.clonar_repo(repo_url, project_id)

            # Construir imagen
            image = self.construir_imagen(repo_path, project_id)

            # Asignar puerto aleatorio
            port = self.obtener_puerto()

            container_name = f"project_{project_id}"

            logger.info(f"🐳 Iniciando contenedor {container_name} en puerto {port}")

            # Ejecutar contenedor
            subprocess.check_call([
                "docker", "run",
                "-d",
                "-p", f"{port}:3000",
                "--name", container_name,
                image
            ])

            # Obtener ID real del contenedor
            container_id = subprocess.check_output(
                ["docker", "ps", "-q", "--filter", f"name={container_name}"],
                text=True
            ).strip()

            if not container_id:
                raise Exception("No se pudo obtener el container_id después del run")

            # Guardar info del contenedor en DB Roble
            self.roble.create_container_info(
                project_id=project_id,
                port=port,
                image_name=image,
                access_token=token
            )

            # Actualizar estado final
            self.roble.update_project_status(
                project_id,
                status="running",
                container_id=container_id,
                access_token=token
            )

            logger.info(f"🎉 Proyecto {project_id} desplegado correctamente")

            return {
                "port": port,
                "image": image,
                "container_id": container_id
            }

        except Exception as e:
            logger.error(f"❌ Error durante el despliegue: {e}")

            # Fallback: detener contenedor y limpiar si falló
            try:
                subprocess.call(["docker", "rm", "-f", f"project_{project_id}"])
            except:
                pass

            # Estado en error
            self.roble.update_project_status(project_id, "error", access_token=token)

            raise Exception(f"Error desplegando proyecto: {e}")
