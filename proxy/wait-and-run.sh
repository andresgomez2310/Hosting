#!/bin/sh
set -eu

echo " HOSTING INICIADO"
echo " ACCESO A DASHBOARD: http://localhost"
echo " ACCESO A MANAGER: http://localhost/api"
echo " AUTH: http://localhost/auth"
echo " PROJECTS: http://localhost/projects"
echo ""
echo " Esperando servicios (timeout ~30s cada uno)..."

wait_for_url() {
  url="$1"
  max=30
  i=0
  while ! curl -sSf "$url" >/dev/null 2>&1 && [ "$i" -lt "$max" ]; do
    i=$((i+1))
    echo "esperando $url... ($i)"
    sleep 1
  done

  if [ "$i" -ge "$max" ]; then
    echo "timeout esperando $url (continuando)";
  else
    echo "$url disponible"
  fi
}

# esperar dashboard y manager (no abortar si timeout)
wait_for_url "http://dashboard:3000/"
wait_for_url "http://manager:5000/"

echo "➡️ Iniciando nginx (si los servicios responden, de lo contrario nginx arrancará igual)..."
exec nginx -g 'daemon off;'
