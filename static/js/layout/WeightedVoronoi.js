function WeightedVoronoi(clusters)
{
  this.clusters = clusters;
  this.scene = new THREE.Scene();
  this.cones = this.clusters.map(clusterToCone);
  for(var c = 0; c < this.cones.length; c++)
  {
    this.scene.add(this.cones[c]);
    this.scene.add(sphere(this.clusters[c].center, 0.05, randomColor()));
  }

  console.log('cones:', this.cones);
}

function clusterToCone(cluster)
{
  var coneGeometry = new THREE.LatheGeometry(
    [
      new THREE.Vector3(0.0, 0.0, 0.0),
      new THREE.Vector3(0, 10, 10)
    ],
    12 // lathe rotation steps
  );
  var coneMaterial = new THREE.MeshBasicMaterial({
    color: randomColor(),
    opacity: 1.0
  });
  
  var coneMesh = new THREE.Mesh( coneGeometry, coneMaterial );
  coneMesh.position.x = cluster.center[1];
  coneMesh.position.y = cluster.center[0];
  coneMesh.position.z = 0.0;

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
