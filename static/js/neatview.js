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
    {
      var convexHull = cluster['convex_hull'];
      //console.log(cluster['convex_hull'].length);
      if(cluster['convex_hull'].length >= 3)
      {
        NVMakeCluster(cluster);
      }
    }
  }
}

function NVMakeCluster(cluster)
{
  var convexHull = cluster['convex_hull'];


  var mapBounds = map.getBounds();

  var geometry = new THREE.Geometry();
  geometry.vertices.push( new THREE.Vector3( cluster.center[1], cluster.center[0], 0 ) );
  
  // do mesh of convex hull
  for(var p = 0; p < convexHull.length && p < 3; p++)
  {
    var point = convexHull[p];
    geometry.vertices.push( new THREE.Vector3( point[1], point[0], 0 ) );
  }
  geometry.faces.push( new THREE.Face3( 0, 1, 2 ) );

  var texture = new THREE.ImageUtils.loadTexture( '/random' );
  var material = new THREE.MeshBasicMaterial({
    //map:texture,
    color:0xcc1111
  });
 
  geometry.computeBoundingSphere();
  geometry.computeBoundingBox();

  mesh = new THREE.Mesh( geometry, material );
  mesh.position.x = 0.0;
  mesh.position.y = 0.0;
  
  scene.add( mesh );

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
