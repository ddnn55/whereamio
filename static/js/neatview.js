var camera, scene, renderer, canvas;
var geometry, material, mesh;

//initNV();
//animateNV();

function initNV() {

  canvas = document.getElementById('three_canvas');
  canvas.width  = $('#map_canvas').width();
  canvas.height = $('#map_canvas').height();
  console.log($('#map_canvas').width());

  //camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 10000 );
  camera = new THREE.OrthographicCamera( 0, canvas.width, canvas.height, 0, -1, 1 );
  //camera.position.z = 1000;

  scene = new THREE.Scene();

  //geometry = new THREE.CubeGeometry( 1, 1, 1 );
  geometry = new THREE.PlaneGeometry( 200, 200, 10, 10 );
  var texture = new THREE.ImageUtils.loadTexture( '/random' );
  material = new THREE.MeshBasicMaterial( { map:texture } );

  mesh = new THREE.Mesh( geometry, material );
  mesh.position.x = canvas.width / 2.0;
  mesh.position.y = canvas.height / 2.0;
  scene.add( mesh );

  renderer = new THREE.WebGLRenderer({
    canvas: canvas
  });

}

function animateNV() {
  var d = new Date();
  var time = d.getTime() / 1000.0;

  // note: three.js includes requestAnimationFrame shim
  requestAnimationFrame( animateNV );

  mesh.rotation.z += 0.01;
  mesh.position.y = canvas.height / 2.0 + 100 * Math.sin(time);

  renderer.render( scene, camera );

}
