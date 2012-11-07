function WeightedVoronoi(clusters)
{
  this.clusters = clusters;
  this.scene = new THREE.Scene();
  this.cones = this.clusters.map(clusterToCone);
  for(var c = 0; c < this.cones.length; c++)
  {
    this.scene.add(this.cones[c]);
  }
}

function clusterToCone(cluster)
{
  var length = 1.0;
  var steps = 32;
  var angle = (cluster.count/400000) * Math.PI / 4.0;
  
  var coneMesh = cone(length, steps, angle);
  //var coneMesh = sphere(cluster.center, 0.05, randomColor());
  coneMesh.position.x = cluster.center[1];
  coneMesh.position.y = cluster.center[0];
  coneMesh.position.z = 0.0;
  coneMesh.material.color = randomColor();

  return coneMesh;
}

function cone(radius, steps, angle)
{
  // ensure all cones extend to/beyond edges of viewport
  var coneGeometry = new THREE.Geometry();
  coneGeometry.vertices.push( new THREE.Vector3( 0.0, 0.0, 0.0 ) );
  for(var s = 0; s < steps; s++)
  {
    var xyAngle = 2.0 * Math.PI * s / steps;
    var xyRadius = radius * Math.sin(angle);
    var depth = radius * Math.cos(angle);
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
