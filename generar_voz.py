"""Genera con ElevenLabs la voz de Chispa que falta (audio/<id>.mp3) a partir de audio/guion.json.

Uso (PowerShell):
    $env:ELEVEN_API_KEY = "tu_clave"
    python generar_voz.py            # solo crea los clips que faltan
    python generar_voz.py --force    # regenera todos

Al terminar actualiza audio/clips.js; el juego usa el clip si existe y, si no, la voz del dispositivo.
Solo usa la biblioteca estándar de Python. Cada ejecución consume créditos de tu cuenta de ElevenLabs
(unos 6 200 caracteres para el guion completo).
"""
import json, os, sys, time, urllib.request, urllib.error

VOZ = "qSd0nNFPQdeWlFXiPj2l"          # Nancy Narradora Dulce: voz joven, dulce y suave (la voz de Chispa)
MODELO = "eleven_multilingual_v2"      # el que usé para los clips actuales: natural y estable en español
ESTILO = "[cheerfully] "               # solo se usa con eleven_v3 / eleven_v4 (admiten etiquetas de entonación)
AQUI = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(AQUI, "audio")

def generar(clave, texto, api):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOZ}?output_format=mp3_44100_128",
        data=json.dumps({"text": (ESTILO if MODELO.startswith("eleven_v") else "") + texto, "model_id": MODELO}).encode("utf-8"),
        headers={"xi-api-key": api, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def main():
    api = os.environ.get("ELEVEN_API_KEY")
    if not api:
        sys.exit("Define la variable de entorno ELEVEN_API_KEY.")
    guion = json.load(open(os.path.join(AUDIO, "guion.json"), encoding="utf-8"))
    forzar = "--force" in sys.argv
    for clave, texto in guion.items():
        destino = os.path.join(AUDIO, clave + ".mp3")
        if os.path.exists(destino) and not forzar:
            continue
        print("generando", clave, "…", flush=True)
        try:
            open(destino, "wb").write(generar(clave, texto, api))
        except urllib.error.HTTPError as e:
            print("  error", e.code, e.read().decode("utf-8", "ignore")[:200])
            break  # no seguir gastando intentos si la cuenta rechaza la petición
        time.sleep(1)  # un clip a la vez: evita bloqueos por exceso de peticiones
    clips = sorted(f[:-4] for f in os.listdir(AUDIO) if f.endswith(".mp3"))
    open(os.path.join(AUDIO, "clips.js"), "w", encoding="utf-8").write("window.CLIPS=" + json.dumps(clips) + ";\n")
    print("clips disponibles:", len(clips), "de", len(guion))

if __name__ == "__main__":
    main()
