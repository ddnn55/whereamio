if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

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
    
    renderer.setSize($('#map_canvas').width(), $('#map_canvas').height());
    
    camera.left = mapBounds.left;
    camera.right = mapBounds.right;
    camera.top = mapBounds.top;
    camera.bottom = mapBounds.bottom;

    camera.updateProjectionMatrix();

    console.log("updated projection matrix");
  });

  $.getJSON('debug', receiveDebug);

}

function receiveDebug(geometries)
{
  console.log("debug geometries ", geometries);
  for(var g = 0; g < geometries.length; g++)
  {
    var geometry = geometries[g];
    switch(geometry.type)
    {
      case 'mesh':
        debugMeshCreate(geometry);
	break;
      case 'voronoi':
        debugVoronoiCreate(geometry);
	break;
      default:
        console.log("Uknown geometry type in debug geometries:", geometry.type);
	break;
    }
  }
  console.log('receiveDebug end');
}

function debugMeshCreate(mesh)
{
  var vertices = mesh.vertices;
  var triangles = mesh.triangles;
  var geometry = new THREE.Geometry();
  for(var v = 0; v < vertices.length; v++)
  {
    geometry.vertices.push( new THREE.Vector3( vertices[v][1], vertices[v][0], 0.0 ) );
  }
  for(var t = 0; t < triangles.length; t++)
  {
    geometry.faces.push( new THREE.Face3( triangles[t][0], triangles[t][1], triangles[t][2] ) );
  }
  
  var material = new THREE.MeshBasicMaterial({
    color: 0xFF0000,
    wireframe: true,
  });

  geometry.computeBoundingSphere();
  geometry.computeBoundingBox();

  var mesh = new THREE.Mesh( geometry, material );
  mesh.position.x = 0.0;
  mesh.position.y = 0.0;
  mesh.position.z = 0.1;

  scene.add( mesh );
}

function debugVoronoiCreate(voronoi)
{
  console.log('debugVoronoiCreate start');
  var vertices = voronoi.vertices;
  var segments = voronoi.segments;

  console.log('segments', segments);

  var material = new THREE.MeshBasicMaterial({
    color: 0x0000FF,
    wireframe: true,
    wireframeLinewidth: 0.5
  });

  //for(var v = 0; v < vertices.length; v++)
  //{
  //  geometry.vertices.push( new THREE.Vector3( vertices[v][1], vertices[v][0], 0.0 ) );
  //}
  for(var s = 0; s < segments.length; s++)
  {
    var segment = segments[s];

    var v1 = segments[s][0];
    var v2 = segments[s][1];

    if(v1 < 0 || v2 < 0)
      continue;

    v1 = vertices[v1];
    v2 = vertices[v2];

    var geometry = new THREE.Geometry();
    geometry.vertices.push( new THREE.Vector3( v1[1], v1[0], 0.0 ) );
    geometry.vertices.push( new THREE.Vector3( v2[1], v2[0], 0.0 ) );
    
    geometry.computeBoundingSphere();
    geometry.computeBoundingBox();

    var polyline = new THREE.Line( geometry, material );
    polyline.position.x = 0.0;
    polyline.position.y = 0.0;
    polyline.position.z = 0.1;

    scene.add( polyline );
  }
  
  console.log('debugVoronoiCreate end');
}

function NVMakeClusters(clusters)
{
  mapBounds.left   = map.getBounds().getSouthWest().lng();
  mapBounds.bottom = map.getBounds().getSouthWest().lat();
  mapBounds.right  = map.getBounds().getNorthEast().lng();
  mapBounds.top    = map.getBounds().getNorthEast().lat();

  var imageUrl = "static/img/grid.png";
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
  var clusterTexture;
  if(cluster['representative_images']['histogram'] !== undefined)
  {
    var imageUrl = cluster['representative_images']['histogram']['image_url'];
    clusterTexture = new THREE.ImageUtils.loadTexture( imageUrl );
  }
  else
  {
    clusterTexture = testTexture;
  }
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
