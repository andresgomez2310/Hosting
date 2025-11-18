import requests
import json

# === CONFIG GENERAL ===
ROBLE_BASE_HOST = "https://roble-api.openlab.uninorte.edu.co"

#CAMBIAR SEGÚN EL PROYECTO
ROBLE_CONTRACT = "hosting_adcce8f544"

ROBLE_LOGIN = f"{ROBLE_BASE_HOST}/auth/{ROBLE_CONTRACT}/login"


def login_en_roble():
    print("=== LOGIN DIRECTO EN ROBLE ===\n")

    email = input("Correo: ")
    password = input("Contraseña: ")

    payload = {"email": email, "password": password}

    print("\n→ Autenticando con Roble…")
    res = requests.post(ROBLE_LOGIN, json=payload)

    print("Status HTTP:", res.status_code)

    # Validar solo 200 o 201
    if res.status_code not in (200, 201):
        print("\n❌ No se pudo iniciar sesión.")
        print("Detalle del error:")
        print(res.text)
        return None

    data = res.json()

    # ÉXITO
    print("\n✅ Inicio de sesión exitoso.")
    print("── INFORMACIÓN DEL USUARIO ──")

    user = data.get("user", {})

    print(f"ID: {user.get('id')}")
    print(f"Nombre: {user.get('name')}")
    print(f"Correo: {user.get('email')}")
    print(f"Rol: {user.get('role')}\n")

    print("Se generó un accessToken y refreshToken correctamente.\n")

    # Si quieren ver el token completo, quitan el comentario:
    # print("AccessToken:", data.get("accessToken"))
    # print("RefreshToken:", data.get("refreshToken"))

    return data.get("accessToken")


def main():
    token = login_en_roble()

    if token:
        print("🎉 El programa finalizó correctamente.")
    else:
        print("⚠️ El programa terminó sin iniciar sesión.")


if __name__ == "__main__":
    main()
