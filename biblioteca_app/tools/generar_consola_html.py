r"""Genera evidencias/consola.html con los bloques PUT y DELETE del LogInterceptor."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidencias = root / "evidencias"
lineas = (evidencias / "consola.txt").read_text(encoding="utf-8").splitlines()


def bloque(method):
    indice = next(i for i, l in enumerate(lineas) if l.strip() == f"method: {method}")
    inicio = indice
    while inicio > 0 and lineas[inicio] != "*** Request ***":
        inicio -= 1
    fin = indice + 1
    while fin < len(lineas) and lineas[fin] != "*** Request ***":
        fin += 1
    return lineas[inicio:fin]


def escapar(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


secciones = []
for metodo in ("PUT", "DELETE"):
    contenido = "\n".join(escapar(l) for l in bloque(metodo))
    secciones.append(f"<h3>{metodo} /api/libros/1</h3><pre>{contenido}</pre>")

html = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Consola Flutter - PUT y DELETE</title>
<style>
  body { margin: 0; padding: 24px; background: #1e1e1e; color: #d4d4d4;
         font-family: Consolas, "Courier New", monospace; font-size: 14px; line-height: 1.35; }
  h1 { font-family: "Segoe UI", sans-serif; color: #569cd6; font-size: 20px; margin: 0 0 4px; }
  p  { font-family: "Segoe UI", sans-serif; color: #9cdcfe; margin: 0 0 18px; }
  h3 { font-family: "Segoe UI", sans-serif; color: #4ec9b0; font-size: 16px; margin: 20px 0 6px; }
  pre { margin: 0; white-space: pre-wrap; }
</style>
</head>
<body>
<h1>Consola Flutter / LogInterceptor (Dio)</h1>
<p>Peticiones del paso 9: PUT responde 200 y DELETE responde 204.</p>
""" + "\n".join(secciones) + "\n</body>\n</html>\n"

(evidencias / "consola.html").write_text(html, encoding="utf-8")
print(evidencias / "consola.html")
