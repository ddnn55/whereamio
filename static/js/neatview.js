var map, mapBounds;
var camera, scene, renderer, canvas;
var geometry, material, mesh, testTexture;

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
    canvas: canvas,
    antialias: true
  });

  google.maps.event.addListener(map, 'bounds_changed', function() {

    mapBounds = {};
    mapBounds.left   = map.getBounds().getSouthWest().lng();
    mapBounds.bottom = map.getBounds().getSouthWest().lat();
    mapBounds.right  = map.getBounds().getNorthEast().lng();
    mapBounds.top    = map.getBounds().getNorthEast().lat();
    
    //canvas.width  = $('#map_canvas').width();
    //canvas.height = $('#map_canvas').height();
    renderer.setSize($('#map_canvas').width(), $('#map_canvas').height());
    
    camera.left = mapBounds.left;
    camera.right = mapBounds.right;
    camera.top = mapBounds.top;
    camera.bottom = mapBounds.bottom;

    camera.updateProjectionMatrix();

    console.log("updated projection matrix");
  });

}

function NVMakeClusters(clusters)
{
  mapBounds.left   = map.getBounds().getSouthWest().lng();
  mapBounds.bottom = map.getBounds().getSouthWest().lat();
  mapBounds.right  = map.getBounds().getNorthEast().lng();
  mapBounds.top    = map.getBounds().getNorthEast().lat();

  var imageUrl = "static/img/grid_tall.png";
  testTexture = new THREE.ImageUtils.loadTexture( imageUrl );

  for(var c = 0; c < clusters.length; c++)
  {
    var cluster = clusters[c];
    if('convex_hull' in cluster)
    {
      var convexHull = cluster['convex_hull'];
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

  // can't put a flickr.com URL here unless they enable CORS :(
  // http://enable-cors.org/
  var imageUrl = cluster['image_url'];
  var clusterTexture = new THREE.ImageUtils.loadTexture( imageUrl );
  //var clusterTexture = testTexture;
  //var imageAspect = clusterTexture.image.width / clusterTexture.image.height;
  //var imageAspect = 0.5 / 1.0;

  var geometry = new THREE.Geometry();
  geometry.vertices.push( new THREE.Vector3( cluster.center[1], cluster.center[0], 0 ) );
 
  var left, right, top, bottom;
  left   = cluster.center[1];
  right  = cluster.center[1];
  top    = cluster.center[0];
  bottom = cluster.center[0];

  // do mesh of convex hull
  var p, uv = [];
  for(p = 0; p < convexHull.length; p++)
  {
    var point = convexHull[p];
    geometry.vertices.push( new THREE.Vector3( point[1], point[0], 0 ) );
    left   = Math.min(left, point[1]);
    right  = Math.max(right, point[1]);
    top    = Math.max(top, point[0]);
    bottom = Math.min(bottom, point[0]);
  }
  //var latLngAspect = dgeo.okProjectionAspect(left, right, top, top - (right-left));
  var latLngAspect = (mapBounds.right - mapBounds.left) / (mapBounds.top - mapBounds.bottom);
  var pixelAspect = canvas.width / canvas.height;
  var aspectCorrection = pixelAspect / latLngAspect;

  //console.log('imageAspect:', imageAspect, 'latLngAspect:', latLngAspect, 'pixelAspect:', pixelAspect, 'aspectCorrection:', aspectCorrection);

  var aspect = (right - left) / (top - bottom);
  aspect *= aspectCorrection /*/ imageAspect*/;
  var uvLeft = 0.0, uvRight = 1.0, uvTop = 1.0, uvBottom = 0.0;
  if(aspect > 1.0)
  {
    var uvHeight = 1.0 / aspect;
    uvBottom = (1.0 - uvHeight) / 2.0;
    uvTop = 1.0 - uvBottom;
  }
  else
  {
    var uvWidth = aspect;
    uvLeft = (1.0 - uvWidth) / 2.0;
    uvRight = 1.0 - uvLeft;
  }
  for(var v = 0; v < geometry.vertices.length; v++)
  {
    var vertex = geometry.vertices[v];
    if(aspect > 1.0)
      uv.push(new THREE.UV(
        (vertex.x - left) / (right - left),
        uvBottom + ((vertex.y - bottom) / (top - bottom)) / aspect
      ));
    else
      uv.push(new THREE.UV(
        uvLeft + aspect * (vertex.x - left) / (right - left),
        (vertex.y - bottom) / (top - bottom)
      ));
  }
  for(var f = 1; f <= convexHull.length; f++)
  {
    var v1 = f;
    var v2 = (f % convexHull.length) + 1;

    geometry.faces.push( new THREE.Face3( 0, v1, v2 ) );
    geometry.faceVertexUvs[ 0 ].push([
      uv[0],
      uv[v1],
      uv[v2]
    ]);
  }


  var material = new THREE.MeshBasicMaterial({
    //map: testTexture,
    map: clusterTexture,
    transparent: true,
    opacity: 0.9,
    //color: 0x991111
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
