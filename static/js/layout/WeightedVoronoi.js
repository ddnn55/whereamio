var LABEL_BUFFER_SIZE = 1024;

function WeightedVoronoi(clusters, canvas)
{
  var _this = this;

  this.clusters = clusters;
  this.canvas = canvas;
  this.scene = new THREE.Scene();
  this.labelBuffer = null;

  this.left = this.clusters
    .map(function(cluster) { return cluster.center[1] })
    .reduce(function(a, b) { return Math.min(a, b) });
  this.right = this.clusters
    .map(function(cluster) { return cluster.center[1] })
    .reduce(function(a, b) { return Math.max(a, b) });
  this.top = this.clusters
    .map(function(cluster) { return cluster.center[0] })
    .reduce(function(a, b) { return Math.max(a, b) });
  this.bottom = this.clusters
    .map(function(cluster) { return cluster.center[0] })
    .reduce(function(a, b) { return Math.min(a, b) }); 
  
  console.log( 'layout left', this.left );
  console.log( 'layout right', this.right );
  console.log( 'layout top', this.top );
  console.log( 'layout bottom', this.bottom );
  
  this.llwidth = this.right - this.left;
  this.llheight = this.top - this.bottom;
  
  this.llcenter = new THREE.Vector3(
    this.left + this.llwidth / 2.0,
    this.bottom + this.llheight / 2.0,
    0.0
  );

  this.maxClusterCount = this.clusters
    .map(function(cluster) { return cluster.count })
    .reduce(function(a, b) { return Math.max(a, b) }, 0);

  this.cones = this.clusters
    .map(function(cluster) { return clusterToCone(cluster, _this.maxClusterCount) });
 
  this.labelBuffer = new THREE.WebGLRenderTarget(
    LABEL_BUFFER_SIZE, LABEL_BUFFER_SIZE,
    {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.NearestFilter,
      //format: THREE.LuminanceFormat,
      //format: THREE.AlphaFormat, // OS X bugs for these two!
      format: THREE.RGBFormat,
      //type: THREE.FloatType
      //type: THREE.UnsignedByteType
    }
  );

  this.renderLabelBuffer();

  var labelBufferPlane = new THREE.PlaneGeometry( this.llwidth, this.llheight, 1, 1 );
  var labelBufferPlaneMaterial = new THREE.MeshBasicMaterial({ map: this.labelBuffer, color: 0xffffff, opacity: 0.5, transparent: true });
  var labelBufferPlaneMesh = new THREE.Mesh( labelBufferPlane, labelBufferPlaneMaterial );
  labelBufferPlaneMesh.position = this.llcenter;
  console.log( labelBufferPlaneMesh.position );

  this.scene.add( labelBufferPlaneMesh );
}

WeightedVoronoi.prototype.renderLabelBuffer = function()
{
  var _this = this;

  var labelScene = new THREE.Scene();
  for(var c = 0; c < this.cones.length; c++)
  {
    //var coneCopy = this.cones[c].clone();
    if(c < this.cones.length / 2)
      labelScene.add(this.cones[c]);
    else
      this.scene.add(this.cones[c]);
    //console.log(this.cones[c].position);
  }
 
  var labelCamera = new THREE.OrthographicCamera( this.left, this.right, this.top, this.bottom, -1, 1000 );

  /*var labelRenderer = new THREE.WebGLRenderer({
    //canvas: this.threeCanvas,
    antialias: false
  });*/

  NV.threeRenderer.render( labelScene, labelCamera, this.labelBuffer );
  console.log( 'not working render call', labelScene, labelCamera, this.labelBuffer );
}

var CONE_MIN_ANGLE = Math.PI / 32.0;
var CONE_MAX_ANGLE = Math.PI / 2.8;

function clusterToCone(cluster, maxClusterCount)
{
  var length = 0.02;
  var steps = 64;
  var angle = CONE_MIN_ANGLE + (cluster.count/maxClusterCount) * (CONE_MAX_ANGLE - CONE_MIN_ANGLE);
  
  /*var coneMesh;

  if(cluster.count == maxClusterCount)
    coneMesh = cone(length, steps, angle, true);
  else
    coneMesh = cone(length, steps, angle, false);*/
  //var angle = Math.PI / 4.0;
  
  /* DEBUG FIXME COMMENT THIS LINE */ var coneMesh = sphere(cluster.center, 0.005, randomColor());
  coneMesh.position.x = cluster.center[1];
  coneMesh.position.y = cluster.center[0];
  coneMesh.position.z = 0.0;
  //coneMesh.material.color = randomColor();
  coneMesh.material.color = new THREE.Color().setRGB(255, 255, 255);

  return coneMesh;
}

function cone(radius, steps, angle, debug)
{
  // ensure all cones extend to/beyond edges of viewport
  var coneGeometry = new THREE.Geometry();
  coneGeometry.vertices.push( new THREE.Vector3( 0.0, 0.0, 0.0 ) );
  var xyRadius = radius * Math.sin(angle);
  var depth = radius * Math.cos(angle);
  if(debug)
  {
    console.log('xyRadius', xyRadius, 'depth', depth);
  }
  for(var s = 0; s < steps; s++)
  {
    var xyAngle = 2.0 * Math.PI * s / steps;
    coneGeometry.vertices.push( new THREE.Vector3(
      xyRadius * Math.cos(xyAngle),
      xyRadius * Math.sin(xyAngle),
      -depth
    ));
  }
  for(var s = 0; s < steps; s++)
  {
    coneGeometry.faces.push( new THREE.Face3( 0, s+1, ((s+1)%steps)+1 ) );
  }

  var coneMaterial = new THREE.MeshBasicMaterial({
  //var coneMaterial = new THREE.ShaderMaterial({
    color: 0x000000,
    opacity: 1.0,
    /*vertexShader: [
      
    ].join("\n"),
    fragmentShader: ""*/
  });
  
  var coneMesh = new THREE.Mesh( coneGeometry, coneMaterial );

  return coneMesh;
}

function sphere(latLng, radius, color)
{
  var sphereGeometry = new THREE.SphereGeometry(radius, 64, 64);
  var sphereMaterial = new THREE.MeshBasicMaterial({
    color: color,
    opacity: 1.0
  });
  
  var sphereMesh = new THREE.Mesh( sphereGeometry, sphereMaterial );
  sphereMesh.position.x = latLng[1];
  sphereMesh.position.y = latLng[0];
  sphereMesh.position.z = 0.0;

  return sphereMesh;
}

function randomColor()
{
  return new THREE.Color().setHSV(Math.random(), 1, 1);
}
