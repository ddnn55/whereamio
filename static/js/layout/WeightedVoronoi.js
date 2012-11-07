function WeightedVoronoi(clusters)
{
  this.clusters = clusters;
  this.scene = new THREE.Scene();
  this.cones = this.clusters.map(clusterToCone);
  for(var c = 0; c < this.cones.length; c++)
  {
    this.scene.add(this.cones[c]);
    //this.scene.add(sphere(this.clusters[c].center, 0.05, randomColor()));
  }

  console.log('cones:', this.cones);
}

function clusterToCone(cluster)
{
  var coneLength = 1.0;
  var steps = 32;
  
  var coneMesh = cone(coneLength, steps);
  //var coneMesh = sphere(cluster.center, 0.05, randomColor());
  coneMesh.position.x = cluster.center[1];
  coneMesh.position.y = cluster.center[0];
  coneMesh.position.z = 0.0;
  coneMesh.material.color = randomColor();

  return coneMesh;
}

function cone(radius, steps)
{
  var coneGeometry = new THREE.Geometry();
  coneGeometry.vertices.push( new THREE.Vector3( 0.0, 0.0, 0.0 ) );
  for(var s = 0; s < steps; s++)
  {
    var theta = 2.0 * Math.PI * s / steps;
    coneGeometry.vertices.push( new THREE.Vector3(
      radius * Math.cos(theta),
      radius * Math.sin(theta),
      -radius
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
