import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class RubiksCubeWidget extends StatefulWidget {
  const RubiksCubeWidget({super.key});

  @override
  State<RubiksCubeWidget> createState() => _RubiksCubeWidgetState();
}

class _RubiksCubeWidgetState extends State<RubiksCubeWidget> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();

    // HTML5 + Three.js + Cubing.js para renderizar e animar o cubo 3D
    const String cubeHtml = '''
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { margin: 0; background-color: #0d1117; display: flex; justify-content: center; align-items: center; height: 100vh; }
        twisty-player { width: 100vw; height: 100vh; }
      </style>
      <script type="module">
        import { TwistyPlayer } from "https://cdn.cubing.net/js/cubing/twisty";
        const player = new TwistyPlayer({
          puzzle: "3x3x3",
          alg: "U2 D2 R2 L2 F2 B2", // Sequência de movimentos (Checkerboard/Xadrez)
          visualization: "3D",
          controlPanel: "none",
          background: "none"
        });
        document.body.appendChild(player);
      </script>
    </head>
    <body></body>
    </html>
    ''';

    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadHtmlString(cubeHtml);
  }

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: WebViewWidget(controller: _controller),
    );
  }
}