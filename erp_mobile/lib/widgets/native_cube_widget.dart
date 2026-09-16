import 'dart:math' as math;
import 'package:flutter/material.dart';

class NativeCubeWidget extends StatefulWidget {
  const NativeCubeWidget({super.key});

  @override
  State<NativeCubeWidget> createState() => _NativeCubeWidgetState();
}

class _NativeCubeWidgetState extends State<NativeCubeWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 10),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const double cubeSize = 100.0;

    return SizedBox(
      height: 250,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          final double angle = _controller.value * 2 * math.pi;

          return Center(
            child: Transform(
              alignment: Alignment.center,
              transform: Matrix4.identity()
                ..setEntry(3, 2, 0.001) // Perspectiva 3D
                ..rotateX(angle)
                ..rotateY(angle),
              child: Stack(
                children: [
                  // Frente (Roxo)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.deepPurple.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(0.0, 0.0, cubeSize / 2),
                    label: 'Frente',
                  ),
                  // Trás (Azul)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.blue.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(0.0, 0.0, -cubeSize / 2)
                      ..rotateY(math.pi),
                    label: 'Trás',
                  ),
                  // Esquerda (Laranja)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.orange.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(-cubeSize / 2, 0.0, 0.0)
                      ..rotateY(-math.pi / 2),
                    label: 'Esq',
                  ),
                  // Direita (Verde)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.green.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(cubeSize / 2, 0.0, 0.0)
                      ..rotateY(math.pi / 2),
                    label: 'Dir',
                  ),
                  // Topo (Amarelo)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.amber.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(0.0, -cubeSize / 2, 0.0)
                      ..rotateX(math.pi / 2),
                    label: 'Topo',
                  ),
                  // Base (Vermelho)
                  _buildFace(
                    size: cubeSize,
                    color: Colors.red.withValues(alpha: 0.85),
                    transform: Matrix4.identity()
                      ..translate(0.0, cubeSize / 2, 0.0)
                      ..rotateX(-math.pi / 2),
                    label: 'Base',
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildFace({
    required double size,
    required Color color,
    required Matrix4 transform,
    required String label,
  }) {
    return Transform(
      alignment: Alignment.center,
      transform: transform,
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          color: color,
          border: Border.all(color: Colors.white, width: 2),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Center(
          child: Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}