import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../domain/models/libro.dart';
import '../../domain/repository/libro_repository.dart';

/// Estado para las vistas: loading, error e items.
/// Cada notifyListeners() hace que la vista se vuelva a dibujar.
class LibroController extends ChangeNotifier {
  LibroController(this.repo);
  final LibroRepository repo;

  List<Libro> items = [];
  bool loading = false;
  String? error;

  // Estado de la pantalla de detalle (Reto: GET /api/libros/{id}).
  Libro? detalle;
  bool cargandoDetalle = false;
  String? errorDetalle;

  /// Busca un libro ya cargado en la lista (lo usa la vista de editar).
  Libro? buscarPorId(int id) {
    for (final l in items) {
      if (l.id == id) return l;
    }
    return null;
  }

  // ✅ GET: se llama al abrir Home
  Future<void> cargar() async {
    loading = true;
    error = null;
    notifyListeners();
    try {
      items = await repo.getLibros();
    } on DioException catch (e) {
      error = 'No se pudo conectar con la API (${e.type.name}).\n'
          '¿Está corriendo Spring Boot en el puerto 8080?';
    } catch (e) {
      error = 'Error inesperado: $e';
    }
    loading = false;
    notifyListeners();
  }

  // ✅ POST: regresa null si salio bien, o el mensaje de error
  Future<String?> crear(Libro libro) async {
    try {
      await repo.crear(libro);
      await cargar(); // recargar la lista para ver el nuevo libro
      return null;
    } on DioException catch (e) {
      return _mensaje(e);
    } catch (e) {
      return '$e';
    }
  }

  // ✅ PUT: actualiza, recarga la lista y regresa null si salió bien.
  Future<String?> actualizar(Libro libro) async {
    try {
      await repo.actualizar(libro);
      await cargar();
      return null;
    } on DioException catch (e) {
      return _mensaje(e);
    } catch (e) {
      return '$e';
    }
  }

  // ✅ DELETE: elimina, recarga la lista y regresa null si salió bien.
  Future<String?> eliminar(int id) async {
    try {
      await repo.eliminar(id);
      await cargar();
      return null;
    } on DioException catch (e) {
      return _mensaje(e);
    } catch (e) {
      return '$e';
    }
  }

  // ✅ Reto: consulta un libro por id para la pantalla de detalle.
  Future<void> cargarLibro(int id) async {
    cargandoDetalle = true;
    detalle = null;
    errorDetalle = null;
    notifyListeners();
    try {
      detalle = await repo.getLibro(id);
      if (detalle == null) errorDetalle = 'El libro no existe';
    } on DioException catch (e) {
      errorDetalle = e.response?.statusCode == 404
          ? 'El libro no existe'
          : _mensaje(e);
    } catch (e) {
      errorDetalle = '$e';
    }
    cargandoDetalle = false;
    notifyListeners();
  }

  String _mensaje(DioException e) {
    final code = e.response?.statusCode;
    switch (code) {
      case 400:
        return 'Datos inválidos (400): título y autor son obligatorios';
      case 404:
        return 'El libro no existe (404)';
      case 500:
        return 'Error del servidor (500)';
      default:
        return code != null
            ? 'Error $code'
            : 'Sin conexión con la API (${e.type.name})';
    }
  }
}
