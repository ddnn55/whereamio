var map, mapBounds;
var camera, scene, renderer, canvas;
var geometry, material, mesh;

function latLngToCanvasXY(latLng)
{
  var mapHeight = mapBounds.top - mapBounds.bottom;
  var mapWidth = mapBounds.right - mapBounds.left;

  var latIn = latLng[0];
  var lngIn = latLng[1];
  
  var out = {};
  out.x = canvas.width  * (lngIn - mapBounds.left)   / mapWidth;
  out.y = canvas.height * (latIn - mapBounds.bottom) / mapHeight;

  return out;
}

function initNV() {

  canvas = document.getElementById('three_canvas');
  canvas.width  = $('#map_canvas').width();
  canvas.height = $('#map_canvas').height();
  console.log($('#map_canvas').width());

  camera = new THREE.OrthographicCamera( 0, canvas.width, canvas.height, 0, -1, 1 );
  scene = new THREE.Scene();
  renderer = new THREE.WebGLRenderer({
    canvas: canvas
  });

  google.maps.event.addListener(map, 'bounds_changed', function() {

    mapBounds = {};
    mapBounds.left   = map.getBounds().getSouthWest().lng();
    mapBounds.bottom = map.getBounds().getSouthWest().lat();
    mapBounds.right  = map.getBounds().getNorthEast().lng();
    mapBounds.top    = map.getBounds().getNorthEast().lat();
    
    canvas.width  = $('#map_canvas').width();
    canvas.height = $('#map_canvas').height();
    
    camera.left = mapBounds.left;
    camera.right = mapBounds.right;
    camera.top = mapBounds.top;
    camera.bottom = mapBounds.bottom;
    camera.updateProjectionMatrix();
  });

}

function NVMakeClusters(clusters)
{
    mapBounds.left   = map.getBounds().getSouthWest().lng();
    mapBounds.bottom = map.getBounds().getSouthWest().lat();
    mapBounds.right  = map.getBounds().getNorthEast().lng();
    mapBounds.top    = map.getBounds().getNorthEast().lat();

  for(var c = 0; c < clusters.length; c++)
  {
    var cluster = clusters[c];
    if('convex_hull' in cluster)
      NVMakeCluster(cluster);
  }
}

function NVMakeCluster(cluster)
{
  var convexHull = cluster['convex_hull'];
 
  var mapBounds = map.getBounds();

  var geometry = new THREE.Geometry();
  geometry.vertices.push( new THREE.Vector3( cluster.center[1], cluster.center[0], 0 ) );
  
  canvasClusterCenter = latLngToCanvasXY(cluster.center);
 

  // put something at center just to see
  geometry = new THREE.PlaneGeometry( 0.001, 0.001, 5, 5 );
  var texture = new THREE.ImageUtils.loadTexture( '/random' );
  material = new THREE.MeshBasicMaterial( { map:texture } );

  mesh = new THREE.Mesh( geometry, material );
  //mesh.position.x = canvasClusterCenter.x;
  //mesh.position.y = canvasClusterCenter.y;
  mesh.position.x = cluster.center[1];
  mesh.position.y = cluster.center[0];
  scene.add( mesh );


  // do mesh of convex hull
  for(var p = 0; p < convexHull.length; p++)
  {
    var point = convexHull[p];
    geometry.vertices.push( new THREE.Vector3( point[1], point[0], 0 ) );
  }
  geometry.faces.push( new THREE.Face3( 0, 1, 2 ) );
}

function animateNV() {
  var d = new Date();
  var time = d.getTime() / 1000.0;

  // note: three.js includes requestAnimationFrame shim
  requestAnimationFrame( animateNV );

  //mesh.rotation.z += 0.01;
  //mesh.position.y = canvas.height / 2.0 + 100 * Math.sin(time);

  renderer.render( scene, camera );

}
