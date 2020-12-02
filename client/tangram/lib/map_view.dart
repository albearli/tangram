import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:tangram/scale_transition.dart';
import 'package:tangram/tileview.dart';

import 'package:http/http.dart' as http;
import 'dart:convert' as convert;

import 'constants.dart';

class MapView extends StatefulWidget {
  final String usernameHighlight;

  MapView({this.usernameHighlight});

  @override
  _MapViewState createState() => _MapViewState();
}

class _MapViewState extends State<MapView> {
  List<Widget> _grid = [];
  bool _refresh = false;

  double tapX;
  double tapY;

  void recordTap(BuildContext context, TapDownDetails details) {
    final RenderBox box = context.findRenderObject();
    final Offset localOffset = box.globalToLocal(details.globalPosition);
    // final Offset localOffset = details.globalPosition;
    tapX = localOffset.dx;
    tapY = localOffset.dy;
  }

  void launchTileView(BuildContext context) {
    print('$tapX $tapY');
    int coordX = ((tapX - Pixel.left) / (Pixel.pixelWidth + .5)).floor();
    int coordY = ((tapY - Pixel.top) / (Pixel.pixelHeight + .5)).floor();

    print('Coordinate: $coordX $coordY');

    Navigator.of(context).push(ScaleRoute(
        page: TileView(
      initialX: coordX,
      initialY: coordY,
    )));
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
            buildGrid();
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
        color: Colors.cyan[100],
        child: InteractiveViewer(
            minScale: 0.1,
            maxScale: 100.0,
            child: Builder(
              builder: (context) => GestureDetector(
                onTapDown: (TapDownDetails details) =>
                    recordTap(context, details),
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
              ),
            )),
      ),
    );
  }

  void buildGrid() async {
    var url = widget.usernameHighlight == null
        ? '$ip/get-heat-map'
        : '$ip/get-user-heat-map/${widget.usernameHighlight}';

    _grid = [];

    var response = await http.get(url);
    if (response.statusCode == 200) {
      List<dynamic> jsonResponse = convert.jsonDecode(response.body);
      List<List<double>> arr = List<List<double>>.from(jsonResponse
          .map((x) => List<double>.from(x.map((x) => x.toDouble()))));

      print(arr[0][0]);
      for (int i = 0; i < arr.length; i++) {
        for (int j = 0; j < arr[i].length; ++j) {
          double intensity = arr[i][j];
          if (intensity != 0) {
            if (intensity > 0)
              _grid.add(Pixel(
                x: i,
                y: j,
                intensity: intensity,
              ));
            else
              _grid.add(Pixel(
                x: i,
                y: j,
                intensity: intensity,
                color: Colors.blue,
              ));
          }
        }
      }
    }

    _refresh = false;
    setState(() {});
  }
}

class Pixel extends StatelessWidget {
  static final double left = 8;
  static final double top = 230;
  static final double screenWidth = 408.7;
  static final double screenHeight = 300;

  static final double pixelWidth = 2;
  static final double pixelHeight = 3;

  final int x;
  final int y;

  final double intensity;

  final Color color;

  Pixel({
    this.x = 0,
    this.y = 0,
    this.color = Colors.yellow,
    this.intensity = 1,
  });

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: left + this.x * (pixelWidth + .5),
      top: top + this.y * (pixelHeight + .5),
      child: Container(
        width: pixelWidth,
        height: pixelHeight,
        color: intensity == 1
            ? color
            : color.withAlpha((80 + 175 * intensity).round()),
      ),
    );
  }
}
