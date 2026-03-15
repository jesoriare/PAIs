import socket
import ssl
import threading
import os
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

# -----------------------------
# CONFIGURACIÓN DEL PROXY MitM
# -----------------------------
PUERTO_FALSO = 3444 
HOST_REAL = "127.0.0.1"
PUERTO_REAL = 3443 

CERT_FALSO = "certs/fake_cert.pem"
KEY_FALSA = "certs/fake_key.pem"

def generar_cert_falso():
    """Genera un certificado falso sobre la marcha para intentar engañar al cliente."""
    if os.path.exists(CERT_FALSO) and os.path.exists(KEY_FALSA):
        return

    print("[*] Generando certificado FALSO para el ataque MitM...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost (HACKER)"),
    ])
    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
        private_key.public_key()
    ).serial_number(x509.random_serial_number()).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    ).sign(private_key, hashes.SHA256())

    with open(KEY_FALSA, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(CERT_FALSO, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

def manejar_victima(cliente_conn, addr):
    # 1. Configuramos el contexto SSL del servidor falso
    contexto_falso = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    contexto_falso.load_cert_chain(certfile=CERT_FALSO, keyfile=KEY_FALSA)

    print(f"\n[!] Víctima interceptada desde {addr}. Intentando handshake TLS falso...")
    try:
        # Aquí intentamos engañar al cliente con nuestro certificado falso
        conn_tls_falsa = contexto_falso.wrap_socket(cliente_conn, server_side=True)
        print("\n[💀] ¡PELIGRO! MitM EXITOSO. El cliente ha aceptado el certificado falso.")
        # Si llegamos aquí, el pinning falló o está desactivado.
        
    except ssl.SSLError as e:
        print(f"\n[🛡️] MitM BLOQUEADO. El cliente detectó el certificado falso y cortó la conexión.")
        print(f"    Motivo del rechazo del cliente: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        cliente_conn.close()

def iniciar_proxy_tls():
    generar_cert_falso()
    
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy.bind(("127.0.0.1", PUERTO_FALSO))
    proxy.listen(5)
    
    print(f"[*] PROXY TLS ATACANTE ESCUCHANDO EN EL PUERTO {PUERTO_FALSO}...")
    
    while True:
        try:
            cliente_conn, addr = proxy.accept()
            threading.Thread(target=manejar_victima, args=(cliente_conn, addr), daemon=True).start()
        except (socket.timeout, TimeoutError):
            pass # Hace una pausa y comprueba si has pulsado Ctrl+C
        except KeyboardInterrupt:
            print("\n[!] Apagando el proxy atacante...")
            break
        except Exception as e:
            # Si el cliente da un portazo y genera un error raro, el proxy no muere
            print(f"[!] Error inesperado en el proxy ignorado: {e}")
            pass

if __name__ == "__main__":
    iniciar_proxy_tls()
