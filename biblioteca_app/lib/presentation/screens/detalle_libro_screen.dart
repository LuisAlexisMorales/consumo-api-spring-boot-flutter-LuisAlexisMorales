import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/libro_controller.dart';

/// Reto: pantalla de detalle que consume GET /api/libros/{id}.
/// Si la API responde 404, muestra "El libro no existe" en lugar de fallar.
class DetalleLibroScreen extends StatefulWidget {
  const DetalleLibroScreen({super.key, required this.id});

  final int id;

  @override
  State<DetalleLibroScreen> createState() => _DetalleLibroScreenState();
}

class _DetalleLibroScreenState extends State<DetalleLibroScreen> {
  @override
  void initState() {
    super.initState();
    context.read<LibroController>().cargarLibro(widget.id);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.watch<LibroController>();

    Widget cuerpo;
    if (c.cargandoDetalle) {
      cuerpo = const Center(child: CircularProgressIndicator());
    } else if (c.errorDetalle != null) {
      cuerpo = Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.search_off, size: 56, color: Colors.orange),
              const SizedBox(height: 12),
              Text(c.errorDetalle!, textAlign: TextAlign.center),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: () => c.cargarLibro(widget.id),
                child: const Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
    } else if (c.detalle == null) {
      cuerpo = const Center(child: Text('El libro no existe'));
    } else {
      final libro = c.detalle!;
      cuerpo = ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ListTile(
                    leading: CircleAvatar(child: Text('${libro.id}')),
                    title: Text(
                      libro.titulo,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    subtitle: Text(libro.autor),
                    contentPadding: EdgeInsets.zero,
                  ),
                  const Divider(),
                  _dato('Año de publicación', '${libro.anio}'),
                  const SizedBox(height: 12),
                  _dato(
                    'Disponible para préstamo',
                    libro.disponible ? 'Sí' : 'No (prestado)',
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text('Detalle del libro #${widget.id}')),
      body: cuerpo,
    );
  }

  Widget _dato(String etiqueta, String valor) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(etiqueta, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(valor),
        ],
      );
}
