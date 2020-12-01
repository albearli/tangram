import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:tangram/scale_transition.dart';
import 'package:tangram/tileview.dart';

class MapView extends StatefulWidget {
  @override
  _MapViewState createState() => _MapViewState();
}

class _MapViewState extends State<MapView> {
  List<Widget> _grid = [];
  bool _refresh = false;

  void launchTileView(BuildContext context) {
    Navigator.of(context).push(ScaleRoute(page: TileView()));
  }

  @override
  void initState() {
    super.initState();

    buildGrid();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          setState(() {
            _refresh = !_refresh;
          });
        },
        backgroundColor: _refresh ? Colors.black : Colors.yellow,
        child: _refresh
            ? SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(),
              )
            : Icon(Icons.refresh),
      ),
      body: Container(
        color: Colors.grey,
        child: InteractiveViewer(
            minScale: 0.1,
            maxScale: 100.0,
            child: GestureDetector(
              onTap: () => launchTileView(context),
              child: Stack(children: [
                SvgPicture.asset(
                  'assets/grey_map.svg',
                  alignment: Alignment.center,
                  width: MediaQuery.of(context).size.width,
                  height: MediaQuery.of(context).size.height,
                ),
                ..._grid,
              ]),
            )),
      ),
    );
  }

  void buildGrid() {
    _grid = [
      Pixel(x: 108, y: 40),
      Pixel(
        x: 107,
        y: 40,
        color: Colors.yellow.withAlpha(180),
      ),
      Pixel(
        x: 107,
        y: 41,
        color: Colors.yellow.withAlpha(230),
      ),
      Pixel(
        x: 108,
        y: 41,
        color: Colors.yellow.withAlpha(230),
      ),
      Pixel(
        x: 106,
        y: 41,
        color: Colors.yellow.withAlpha(255),
      ),
      Pixel(
        x: 107,
        y: 42,
        color: Colors.yellow.withAlpha(100),
      ),
    ];
    // for (int i = 0; i < 170; i++) {
    //   for (int j = 0; j < 90; j++) {
    //     _grid.add(Pixel(x: i, y: j));
    //   }
    // }
    setState(() {});
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

  final Color color;

  Pixel({
    this.x = 0,
    this.y = 0,
    this.color = Colors.yellow,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: left + this.x * (pixelWidth + .5),
      top: top + this.y * (pixelHeight + .5),
      child: Container(
        width: pixelWidth,
        height: pixelHeight,
        color: color,
      ),
    );
  }
}
