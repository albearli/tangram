import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class MapView extends StatefulWidget {
  @override
  _MapViewState createState() => _MapViewState();
}

class _MapViewState extends State<MapView> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: Icon(Icons.refresh),
      ),
      body: Container(
        color: Colors.grey,
        child: InteractiveViewer(
            minScale: 0.1,
            maxScale: 100.0,
            child: Stack(children: [
              SvgPicture.asset(
                'assets/grey_map.svg',
                alignment: Alignment.center,
                width: MediaQuery.of(context).size.width,
                height: MediaQuery.of(context).size.height,
              ),
              ...buildGrid(),
            ])),
      ),
    );
  }

  List<Widget> buildGrid() {
    List<Widget> toReturn = [];
    for (int i = 0; i < 170; i++) {
      for (int j = 0; j < 90; j++) {
        // toReturn.add(Pixel(x: i, y: j));
      }
    }
    return toReturn;
  }
}

class Pixel extends StatelessWidget {
  final double left = 8;
  final double top = 230;
  final double screenWidth = 408.7;
  final double screenHeight = 300;

  final double pixelWidth = 2;
  final double pixelHeight = 3;

  final int x;
  final int y;

  Pixel({
    this.x = 0,
    this.y = 0,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: left + this.x * (pixelWidth + .5),
      top: top + this.y * (pixelHeight + .5),
      child: Container(
        width: pixelWidth,
        height: pixelHeight,
        color: Colors.yellow,
      ),
    );
  }
}
