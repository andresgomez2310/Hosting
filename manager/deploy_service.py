"""
Servicio encargado del despliegue de proyectos:
 - Clonar repositorio del usuario
 - Construir imagen Docker
 - Ejecutar contenedor en la red de Docker-Compose
 - Actualizar el estado del proyecto (vía Roble)
 - Actualizar el proxy (subdominio → contenedor)
"""

import os
import subprocess
import random
import shutil
import logging

from roble_client import RobleClient

logger = logging.getLogger(__name__)


class DeployService:
    """
    Clase de alto nivel para desplegar proyectos de hosting.
    """

    def __init__(self):
        self.roble = RobleClient()

        # Carpeta temporal donde se clonan los repos
        self.base_tmp_dir = os.getenv("DEPLOY_TMP_DIR", "/tmp/hosting_proyectos")

        # Nombre de la red de Docker-Compose (debe existir)
        self.docker_network = os.getenv("DOCKER_NETWORK", "hosting_net")

        # Nombre del contenedor del proxy (para hacer docker exec y recargar nginx)
        self.proxy_container_name = os.getenv("PROXY_CONTAINER_NAME", "proxy")

        # Archivo compartido proxy/manager con el mapa de subdominios
        self.nginx_map_file = os.getenv(
            "NGINX_MAP_FILE",
            "/etc/nginx/conf.d/projects-map.conf"
        )

        os.makedirs(self.base_tmp_dir, exist_ok=True)

    # ---------------------------------------------------------
    # Helpers internos
    # ---------------------------------------------------------

    def _ruta_repo(self, project_id: str) -> str:
        """
        Devuelve la ruta local donde se clonará el repo de este proyecto.
        """
        return os.path.join(self.base_tmp_dir, f"project_{project_id}")

    def clonar_repo(self, repo_url: str, project_id: str) -> str:
        """
        Clona el repositorio del usuario en una carpeta temporal.
        """
        target = self._ruta_repo(project_id)

        logger.info(f"📁 Clonando repo '{repo_url}' en {target}")

        # Eliminar si existe
        if os.path.exists(target):
            shutil.rmtree(target)

        try:
            subprocess.check_call(["git", "clone", repo_url, target])
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error clonando repositorio: {e}")

        return target

    def construir_imagen(self, project_id: str, repo_path: str) -> str:
        """
        Construye la imagen Docker usando el Dockerfile del repo.
        """
        image_name = f"project_{project_id}".lower()

        logger.info(f"🧱 Construyendo imagen Docker '{image_name}' desde {repo_path}")

        try:
            subprocess.check_call([
                "docker", "build",
                "-t", image_name,
                repo_path
            ])
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error construyendo la imagen: {e}")

        return image_name

    def ejecutar_contenedor(self, project_id: str, image_name: str) -> str:
        """
        Ejecuta el contenedor del proyecto en la red de docker-compose.
        No publica puerto al host, se accederá solo por el proxy.
        """
        container_name = f"project_{project_id}".lower()

        logger.info(f"🐳 Ejecutando contenedor '{container_name}' en red '{self.docker_network}'")

        # Por si ya existe un contenedor con el mismo nombre
        subprocess.call(["docker", "rm", "-f", container_name])

        cmd = [
            "docker", "run",
            "-d",
            "--name", container_name,
            "--network", self.docker_network,
            "--cpus", "0.5",
            "--memory", "256m",
            image_name
        ]

        try:
            container_id = subprocess.check_output(cmd, text=True).strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error ejecutando el contenedor: {e}")

        return container_name, container_id

    def actualizar_mapa_nginx(self, nombre: str, username: str, container_name: str):
        """
        Añade/actualiza la entrada correspondiente en el archivo de mapa de Nginx:
            nombre.username.localhost  http://container_name:3000;
        y recarga la configuración del proxy.
        """
        os.makedirs(os.path.dirname(self.nginx_map_file), exist_ok=True)

        host = f"{nombre}.{username}.localhost"
        linea = f"{host} http://{container_name}:3000;\n"

        logger.info(f"📝 Actualizando mapa de Nginx en {self.nginx_map_file}")
        logger.info(f"    {host}  →  http://{container_name}:3000")

        
        with open(self.nginx_map_file, "a") as f:
            f.write(linea)

        # Recargar Nginx dentro del contenedor "proxy"
        logger.info("🔁 Recargando Nginx dentro del contenedor del proxy")
        subprocess.call([
            "docker", "exec",
            self.proxy_container_name,
            "nginx", "-s", "reload"
        ])

    # ---------------------------------------------------------
    # Método principal
    # ---------------------------------------------------------

    def desplegar(self, project_id: str, repo_url: str, token: str,
                  nombre: str, username: str) -> dict:
        """
        Orquesta todos los pasos del despliegue:

         1. Marcar proyecto como "building" en Roble (si tienes ese método)
         2. Clonar repositorio
         3. Construir imagen
         4. Ejecutar contenedor
         5. Actualizar mapa de Nginx
         6. Marcar proyecto como "running"
        """

        logger.info(f"🚀 Iniciando despliegue del proyecto {project_id}")

    
        try:
            if hasattr(self.roble, "update_project_status"):
                self.roble.update_project_status(
                    project_id=project_id,
                    status="building",
                    access_token=token
                )
        except Exception as e:
            logger.warning(f"⚠️ No se pudo actualizar estado a 'building' en Roble: {e}")

        try:
            # 1. Clonar repositorio
            repo_path = self.clonar_repo(repo_url, project_id)

            # 2. Construir imagen
            image = self.construir_imagen(project_id, repo_path)

            # 3. Ejecutar contenedor
            container_name, container_id = self.ejecutar_contenedor(project_id, image)

            # 4. Actualizar mapa del proxy (subdominio → contenedor)
            self.actualizar_mapa_nginx(nombre, username, container_name)

            # 5. Actualizar estado a "running"
            try:
                if hasattr(self.roble, "update_project_status"):
                    self.roble.update_project_status(
                        project_id=project_id,
                        status="running",
                        container_id=container_id,
                        access_token=token
                    )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar estado a 'running' en Roble: {e}")

            logger.info(f"✅ Despliegue exitoso del proyecto {project_id}")

            return {
                "image": image,
                "container_name": container_name,
                "container_id": container_id
            }

        except Exception as e:
            logger.error(f"❌ Error durante el despliegue: {e}")

            # Estado en error
            try:
                if hasattr(self.roble, "update_project_status"):
                    self.roble.update_project_status(
                        project_id=project_id,
                        status="error",
                        access_token=token
                    )
            except Exception as e2:
                logger.warning(f"⚠️ No se pudo actualizar estado a 'error' en Roble: {e2}")

            # Intentar limpiar contenedor si se creó algo
            try:
                subprocess.call(["docker", "rm", "-f", f"project_{project_id}"])
            except Exception:
                pass

            raise
