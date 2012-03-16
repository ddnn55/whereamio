#!/usr/bin/env python

from dgeo import GeoGrid

nyc = GeoGrid(-74.034805, -73.891296, 40.800296, 40.66866, 10)
html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
<title>Google Maps JavaScript API v3 Example: Polygon Simple</title>
<link href="http://code.google.com/apis/maps/documentation/javascript/examples/default.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>
<script type="text/javascript">

  function initialize() {
    var myLatLng = new google.maps.LatLng(24.886436490787712, -70.2685546875);
    var myOptions = {
      zoom: 5,
      center: myLatLng,
      mapTypeId: google.maps.MapTypeId.TERRAIN
    };

    var bermudaTriangle;

    var map = new google.maps.Map(document.getElementById("map_canvas"),
        myOptions);

    var triangleCoords = [
"""

def outline_on_google_maps(cell):
   global html
   html = html + "[new google.maps.LatLng("+str(cell.bottom)+", "+str(cell.left)+"),\n"
   html = html + "new google.maps.LatLng("+str(cell.bottom)+", "+str(cell.right)+"),\n"
   html = html + "new google.maps.LatLng("+str(cell.top)   +", "+str(cell.right)+"),\n"
   html = html + "new google.maps.LatLng("+str(cell.top)   +", "+str(cell.left)+"),\n"
   html = html + "new google.maps.LatLng("+str(cell.bottom)+", "+str(cell.left)+")],\n"

nyc.foreach_cell(outline_on_google_maps)

html = html + """
    ];

    // Construct the polygon
    bermudaTriangle = new google.maps.Polygon({
      paths: triangleCoords,
      strokeColor: "#FF0000",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#FF0000",
      fillOpacity: 0.35
    });

   bermudaTriangle.setMap(map);
  }
</script>
</head>
<body onload="initialize()">
  <div id="map_canvas"></div>
</body>
</html>
"""

print html
