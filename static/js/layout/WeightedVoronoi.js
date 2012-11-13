function WeightedVoronoi(clusters)
{
  var _this = this;

  this.clusters = clusters;
  this.scene = new THREE.Scene();

  this.maxClusterCount = this.clusters
    .map(function(cluster) { return cluster.count })
    .reduce(function(a, b) { return Math.max(a, b) }, 0);

  this.cones = this.clusters.map(function(cluster) { return clusterToCone(cluster, _this.maxClusterCount) });
  for(var c = 0; c < this.cones.length; c++)
  {
    this.scene.add(this.cones[c]);
  }
}

var CONE_MIN_ANGLE = Math.PI / 32.0;
var CONE_MAX_ANGLE = Math.PI / 2.0;

function clusterToCone(cluster, maxClusterCount)
{
  var length = 0.02;
  var steps = 64;
  var angle = CONE_MIN_ANGLE + (cluster.count/maxClusterCount) * (CONE_MAX_ANGLE - CONE_MIN_ANGLE);
  
  var coneMesh;

  if(cluster.count == maxClusterCount)
    coneMesh = cone(length, steps, angle, true);
  else
    coneMesh = cone(length, steps, angle, false);
  //var angle = Math.PI / 4.0;
  
  //var coneMesh = sphere(cluster.center, 0.05, randomColor());
  coneMesh.position.x = cluster.center[1];
  coneMesh.position.y = cluster.center[0];
  coneMesh.position.z = 0.0;
  coneMesh.material.color = randomColor();

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
    color: 0x000000,
    opacity: 1.0
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
