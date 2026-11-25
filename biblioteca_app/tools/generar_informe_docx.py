r"""Genera el cuerpo del informe de la Práctica 1 (Consumo de API Spring Boot).

Con USAR_PORTADA=1 se omite el título y los datos de portada: la portada
oficial se inserta como primera página con Word (ver tools/insertar_portada.ps1).
"""
import os
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

root = Path(__file__).resolve().parents[1]
evidencias = root / "evidencias"
doc = Document()

estilo = doc.styles["Normal"]
estilo.font.name = "Calibri"
estilo.font.size = Pt(10.5)


def parrafo(texto, negrita=False):
    p = doc.add_paragraph()
    run = p.add_run(texto)
    run.bold = negrita
    return p


def tabla(encabezados, filas, anchos=None):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    for i, texto in enumerate(encabezados):
        celda = t.rows[0].cells[i]
        celda.text = texto
        for run in celda.paragraphs[0].runs:
            run.bold = True
    for fila in filas:
        celdas = t.add_row().cells
        for i, texto in enumerate(fila):
            celdas[i].text = texto
    if anchos:
        for fila in t.rows:
            for i, ancho in enumerate(anchos):
                fila.cells[i].width = Inches(ancho)
    doc.add_paragraph()
    return t


def codigo(texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    run = p.add_run(texto)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    return p


def figura(archivo, titulo, descripcion):
    doc.add_heading(titulo, level=2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(evidencias / archivo), width=Inches(6.0))
    p = doc.add_paragraph()
    p.add_run("Descripción: ").bold = True
    p.add_run(descripcion)


# ---------------------------------------------------------------- portada
if os.getenv("USAR_PORTADA") != "1":
    doc.add_heading("Práctica 1: Consumo de una API Spring Boot desde Flutter", 0)
    parrafo("Biblioteca ITT — Desarrollo de Aplicaciones Móviles")
    tabla(
        ["Dato", "Valor"],
        [
            ["Integrante", "Luis Alexis Morales José"],
            ["Grupo", "7US"],
            ["Docente", "Josué Israel Vásquez Martínez"],
            ["Fecha", "24 de noviembre de 2026"],
        ],
        [1.4, 4.9],
    )

doc.add_heading("Objetivo", level=1)
parrafo(
    "Completar el CRUD de una aplicación Flutter que consume una API REST de Spring Boot. "
    "La app base ya leía la lista de libros (GET) y registraba libros nuevos (POST); "
    "se implementaron editar (PUT) y eliminar (DELETE) en las capas service, repository "
    "y controller, respetando la estructura de carpetas. Como reto se añadió una pantalla "
    "de detalle que consume GET /api/libros/{id} y maneja el caso 404 sin cerrar la app."
)

doc.add_heading("1. Entorno y preparación", level=1)
tabla(
    ["Elemento", "Versión / acción"],
    [
        ["Flutter", "3.47 (flutter --version)"],
        ["Java", "JDK 25 (java -version; el proyecto pide 17 o superior)"],
        ["Maven", "3.9.9 instalado en C:\\Users\\moral\\Tools\\apache-maven-3.9.9 (el documento lo marcaba como opcional)"],
        ["Navegador", "Chrome headless para ejecutar y capturar la app web"],
        ["Repositorio", "https://github.com/23620030/Practicaconsumo1.git"],
        ["Plataformas", "flutter create . --platforms=web,android,windows y flutter pub get"],
        ["Permisos Android", "INTERNET y usesCleartextTraffic=\"true\" agregados en AndroidManifest.xml"],
    ],
    [1.5, 4.8],
)
parrafo(
    "La API se levantó desde backend/ con mvn -q spring-boot:run. La consola confirmó "
    "«Tomcat started on port 8080» y «Datos de prueba cargados: 5 libros». "
    "El backend no fue modificado."
)

doc.add_heading("2. Prueba de los endpoints antes de programar (paso 3)", level=1)
parrafo(
    "Se ejecutaron las peticiones de backend/Biblioteca_API.postman_collection.json "
    "contra http://localhost:8080 y se anotaron los códigos de estado reales:"
)
tabla(
    ["Método", "Ruta", "Resultado obtenido"],
    [
        ["GET", "/", "200 — «Bienvenido a la API de la Biblioteca ITT»"],
        ["GET", "/api/libros", "200 — lista con los 5 libros de prueba"],
        ["GET", "/api/libros/1", "200 — libro con id 1"],
        ["POST", "/api/libros", "201 — libro creado con id 6"],
        ["PUT", "/api/libros/6", "200 — libro actualizado (disponible=false)"],
        ["DELETE", "/api/libros/6", "204 — sin cuerpo"],
        ["DELETE", "/api/libros/6 (repetido)", "404 — el id ya no existe"],
    ],
    [1.0, 2.0, 3.3],
)
parrafo(
    "Esto coincide con lo indicado en la consigna: PUT responde 200 con el libro cambiado, "
    "DELETE responde 204 sin cuerpo y repetir DELETE responde 404. El registro temporal "
    "creado para la prueba (id 6) se eliminó; la API quedó con sus 5 libros originales."
)

doc.add_heading("3. Implementación de los TODO (capas service, repository y controller)", level=1)
tabla(
    ["TODO", "Archivo", "Método", "Implementación"],
    [
        ["1a", "lib/services/libro_service.dart", "actualizar(int id, body)", "dio.put('${ApiConfig.libros}/$id', data: body) → res.data como Map"],
        ["1b", "lib/services/libro_service.dart", "eliminar(int id)", "dio.delete('${ApiConfig.libros}/$id') (204, sin retorno)"],
        ["2a", "lib/domain/repository/libro_repository.dart", "actualizar(Libro libro)", "service.actualizar(libro.id!, libro.toJson()) → Libro.fromJson(data)"],
        ["2b", "lib/domain/repository/libro_repository.dart", "eliminar(int id)", "await service.eliminar(id)"],
        ["3a", "lib/presentation/controllers/libro_controller.dart", "actualizar(Libro libro)", "await repo.actualizar → await cargar() → null; DioException → _mensaje(e)"],
        ["3b", "lib/presentation/controllers/libro_controller.dart", "eliminar(int id)", "await repo.eliminar → await cargar() → null; DioException → _mensaje(e)"],
    ],
    [0.5, 1.9, 1.4, 2.5],
)
parrafo("Fragmentos finales (service y controller):", negrita=True)
codigo(
    "// lib/services/libro_service.dart\n"
    "Future<Map<String, dynamic>> actualizar(int id, Map<String, dynamic> body) async {\n"
    "  final res = await dio.put('${ApiConfig.libros}/$id', data: body);\n"
    "  return res.data as Map<String, dynamic>;\n"
    "}\n\n"
    "Future<void> eliminar(int id) async {\n"
    "  await dio.delete('${ApiConfig.libros}/$id');\n"
    "}"
)
codigo(
    "// lib/presentation/controllers/libro_controller.dart\n"
    "Future<String?> actualizar(Libro libro) async {\n"
    "  try {\n"
    "    await repo.actualizar(libro);\n"
    "    await cargar();\n"
    "    return null;\n"
    "  } on DioException catch (e) {\n"
    "    return _mensaje(e);\n"
    "  } catch (e) {\n"
    "    return '$e';\n"
    "  }\n"
    "}\n"
    "// eliminar(int id) sigue exactamente el mismo patrón con repo.eliminar(id)."
)
parrafo(
    "El mensaje de éxito «Guardado correctamente» / «Libro eliminado» lo muestra la app "
    "cuando el controller devuelve null, y la lista se redibuja porque cargar() "
    "notifica a los widgets con notifyListeners()."
)

doc.add_heading("4. Reto: pantalla de detalle con GET /api/libros/{id}", level=1)
tabla(
    ["Archivo", "Cambio"],
    [
        ["lib/services/libro_service.dart", "getLibro(int id) → dio.get('${ApiConfig.libros}/$id') y res.data como Map"],
        ["lib/domain/repository/libro_repository.dart", "getLibro(int id) → Libro.fromJson(await service.getLibro(id))"],
        ["lib/presentation/controllers/libro_controller.dart", "cargarLibro(int id) con detalle, cargandoDetalle y errorDetalle"],
        ["lib/routes/app_router.dart", "Nueva ruta /libro/:id que construye DetalleLibroScreen(id)"],
        ["lib/presentation/widgets/libro_tile.dart", "onTap: context.push('/libro/${libro.id}')"],
        ["lib/presentation/screens/detalle_libro_screen.dart", "Pantalla nueva con el detalle y manejo del 404"],
    ],
    [2.4, 3.9],
)
parrafo(
    "Si la API devuelve 404, el controller detecta e.response?.statusCode == 404 y asigna "
    "«El libro no existe» a errorDetalle. La pantalla muestra ese mensaje con un botón "
    "«Reintentar» en lugar de dejar que la aplicación termine."
)

doc.add_page_break()
doc.add_heading("5. Evidencias", level=1)
figura(
    "figura_1_lista_antes.png",
    "Figura 1. Lista antes de los cambios (paso 9)",
    "Home muestra los 5 libros cargados con GET /api/libros antes de editar o eliminar.",
)
figura(
    "figura_2_formulario_edicion.png",
    "Figura 2. Formulario de edición",
    "Al tocar el lápiz del primer libro se abre /editar/1 con los datos actuales y el botón «Actualizar (PUT)».",
)
figura(
    "figura_3_lista_despues_editar.png",
    "Figura 3. Lista después de editar",
    "El título pasa a «Cien años de soledad (editado)», Disponible queda en falso («Prestado») y aparece «Guardado correctamente».",
)
figura(
    "figura_4_lista_despues_eliminar.png",
    "Figura 4. Lista después de eliminar",
    "Tras confirmar, el libro editado desaparece de la lista y la API también queda con 4 libros.",
)
figura(
    "consola.png",
    "Figura 5. Consola con las peticiones PUT y DELETE",
    "El LogInterceptor de Dio muestra PUT /api/libros/1 con statusCode 200 y DELETE /api/libros/1 con statusCode 204.",
)
figura(
    "figura_6_detalle.png",
    "Figura 6. Reto: detalle del libro",
    "Al tocar un renglón se navega a /libro/1 y la pantalla muestra id, título, autor, año y disponibilidad con GET /api/libros/1.",
)
figura(
    "figura_7_no_existe.png",
    "Figura 7. Reto: caso 404",
    "Al abrir /libro/999 la API responde 404 y la app muestra «El libro no existe» con opción de reintentar, sin cerrarse.",
)

doc.add_heading("6. Comprobación final", level=1)
tabla(
    ["Comprobación", "Resultado"],
    [
        ["flutter analyze", "No issues found!"],
        ["flutter build web --debug / --release", "Ambos correctos"],
        ["Splash", "«Conexión OK» y consola «Conexion OK -> 200»"],
        ["PUT en la app", "HTTP 200, lista recargada con el cambio"],
        ["DELETE en la app", "HTTP 204, libro eliminado de la lista y de la API"],
        ["GET /api/libros (reto)", "Detalle mostrado; id inexistente → «El libro no existe»"],
        ["Backend", "Sin modificaciones"],
    ],
    [2.2, 4.1],
)

doc.add_heading("7. Conclusión", level=1)
parrafo(
    "La práctica permitió cerrar el CRUD respetando la separación de responsabilidades: "
    "el service conoce las rutas y el código de estado, el repository convierte JSON en "
    "objetos Libro y el controller prepara el estado que consume la interfaz. El reto "
    "mostró que es posible añadir una nueva pantalla sin romper las capas existentes y "
    "que un 404 debe traducirse en un mensaje amigable para la persona usuaria."
)

destino = root / os.getenv("NOMBRE_SALIDA", "CUERPO_INFORME.docx")
doc.save(destino)
print(destino)
