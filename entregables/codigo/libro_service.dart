import 'package:dio/dio.dart';

import '../core/constants/api_config.dart';

/// El service SOLO sabe las rutas. No transforma nada:
/// devuelve el JSON tal cual (List o Map).
class LibroService {
  LibroService(this.dio);
  final Dio dio;

  // ✅ GET /api/libros  -> 200 + lista en JSON
  Future<List<dynamic>> getLibros() async {
    final res = await dio.get(ApiConfig.libros);
    return res.data as List<dynamic>;
  }

  // ✅ POST /api/libros  -> 201 + libro creado en JSON
  Future<Map<String, dynamic>> crear(Map<String, dynamic> body) async {
    final res = await dio.post(ApiConfig.libros, data: body);
    return res.data as Map<String, dynamic>;
  }

  // ✅ PUT /api/libros/{id} -> 200 + libro actualizado en JSON
  Future<Map<String, dynamic>> actualizar(int id, Map<String, dynamic> body) async {
    final res = await dio.put('${ApiConfig.libros}/$id', data: body);
    return res.data as Map<String, dynamic>;
  }

  // ✅ DELETE /api/libros/{id} -> 204 (sin cuerpo)
  Future<void> eliminar(int id) async {
    await dio.delete('${ApiConfig.libros}/$id');
  }

  // ✅ Reto: GET /api/libros/{id} -> 200 + libro, o 404 si no existe
  Future<Map<String, dynamic>> getLibro(int id) async {
    final res = await dio.get('${ApiConfig.libros}/$id');
    return res.data as Map<String, dynamic>;
  }
}
