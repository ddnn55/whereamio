
var TESSELATION_CANALS_WIDTH = 4;

if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

var map, mapBounds;
var material, mesh, testTexture;
var NV;

function NVUnixTime()
{
  return Math.round((new Date()).getTime() / 1000);
}

function triangleArea(t)
{
  var x1 = t[1].x - t[0].x;
  var y1 = t[1].y - t[0].y;
  var x2 = t[2].x - t[0].x;
  var y2 = t[2].y - t[0].y;
  var area = 0.5 * Math.abs(x1*y1-x2*y2);
  return area;
}

function median(list)
{
  list.sort();
  return list[Math.floor(list.length/2)];
}

/*function latLngTranslatedByPointsTowardPoint(latLngFrom, screenDistance, latLngTarget)
{
  var latLngDirection = [ latLngTarget[0] - latLngFrom[0], latLngTarget[1] - latLngFrom[1] ];
  var screenDirection = [ latLngDirection[1], latLngDirection[0] ]; // FIXME TODO fix latLng vs. screen aspect here, need a more abstract solution... :(

  var screenDestination
}*/

/******* Class Neatview **********/
var DELAY = 1000.0 / 60;
function Neatview()
{
  var _this = this;
  
  this.clusters = [];
  this.voronoiVertices;
  this.lastTime = null;
  this.loadedOrFailedClusterCount = 0;
  this.textureRequestCount = 0;
  this.clusterCount = 0;
  this.clusterDensityMedian;

  this.datGui = new dat.GUI({ width: 400 });
  this.options = {};

  this.options.opacity = 0.5;
  this.datGui.add(this.options, 'opacity', 0.0, 1.0).onChange(function(opacity) {
    _this.setOpacity(opacity);
  });

  this.options.drawImages = false;
  this.datGui.add(this.options, 'drawImages').onChange(function() {
    _this.render();
  });

  this.options.drawImplicitWeightedVoronoi = true;
  this.datGui.add(this.options, 'drawImplicitWeightedVoronoi').onChange(function() {
    _this.render();
  });

  var WV = this.datGui.addFolder('Weighted Voronoi');

  this.options.coneRadius = 0.02;
  WV.add(this.options, 'coneRadius', 0.0, 0.05).onChange(function(coneRadius){
    _this.weightedVoronoi.coneRadius = coneRadius;
    _this.weightedVoronoi.update();
    _this.render();
  });
  this.options.coneAngleMin = Math.PI / 32.0;
  WV.add(this.options, 'coneAngleMin', 0.0, Math.PI / 2.0).onChange(function(coneAngleMin){
    _this.weightedVoronoi.coneAngleMin = coneAngleMin;
    _this.weightedVoronoi.update();
    _this.render();
  });
  this.options.coneAngleMax = Math.PI / 2.0;
  WV.add(this.options, 'coneAngleMax', 0.0, Math.PI / 2.0).onChange(function(coneAngleMax){
    _this.weightedVoronoi.coneAngleMax = coneAngleMax;
    _this.weightedVoronoi.update();
    _this.render();
  });

  this.threeCanvas = document.getElementById('three_canvas');
  this.threeCanvas.width  = $('#map_canvas').width();
  this.threeCanvas.height = $('#map_canvas').height();

  this.camera = new THREE.OrthographicCamera( 0, this.threeCanvas.width, this.threeCanvas.height, 0, -1, 1000 );
  this.scene = new THREE.Scene();
  this.threeRenderer = new THREE.WebGLRenderer({
    canvas: _this.threeCanvas,
    antialias: true
  });

  google.maps.event.addListener(map, 'bounds_changed', function() {
    mapBounds = {};
    mapBounds.left   = map.getBounds().getSouthWest().lng();
    mapBounds.bottom = map.getBounds().getSouthWest().lat();
    mapBounds.right  = map.getBounds().getNorthEast().lng();
    mapBounds.top    = map.getBounds().getNorthEast().lat();
    
    _this.threeRenderer.setSize($('#map_canvas').width(), $('#map_canvas').height());
    
    _this.camera.left = mapBounds.left;
    _this.camera.right = mapBounds.right;
    _this.camera.top = mapBounds.top;
    _this.camera.bottom = mapBounds.bottom;

    _this.camera.updateProjectionMatrix();

    _this.render();
  });
}

Neatview.prototype.needsRender = function()
{
  var _this = this;
  requestAnimationFrame(function() { _this.render() });
}

Neatview.prototype.render = function()
{
  this.threeRenderer.clear();

  if(this.options.drawImages)
    this.threeRenderer.render( this.scene, this.camera );
  
  if(this.options.drawImplicitWeightedVoronoi && this.weightedVoronoi)
  {
    //this.weightedVoronoi.renderLabelBuffer();
    this.threeRenderer.render( this.weightedVoronoi.scene, this.camera );
    this.once || console.log( 'working render call', this.weightedVoronoi.scene, this.camera );
    this.once = true;
  }
}

Neatview.prototype.setOpacity = function(opacity)
{
  for(var c = 0; c < this.clusters.length; c++)
  {
    var cluster = this.clusters[c];
    cluster.mesh.material.opacity = opacity;
  }
  this.needsRender();
}

Neatview.prototype.loadTile = function(data)
{
  
  mapBounds.left   = map.getBounds().getSouthWest().lng();
  mapBounds.bottom = map.getBounds().getSouthWest().lat();
  mapBounds.right  = map.getBounds().getNorthEast().lng();
  mapBounds.top    = map.getBounds().getNorthEast().lat();

  var imageUrl = "static/img/grid.png";
  testTexture = new THREE.ImageUtils.loadTexture( imageUrl );

  this.voronoiVertices = data['voronoi_vertices']
  this.clusterCount = data['clusters'].length;

  // DEBUG DELETEME FIXME just first few
  //this.clusterCount = 100;

  for(var c = 0; c < this.clusterCount; c++) 
  {
    var cluster_data = data['clusters'][c];
    var cluster = new Cluster(cluster_data);
    this.clusters.push(cluster);
  }

  this.totalDensity = this.computeTotalDensity();
  this.weightedVoronoi = new WeightedVoronoi(this.clusters, this.threeCanvas);

  this.render();
}

Neatview.prototype.allClustersLoaded = function()
{
  NV.render();
  console.log("NV Loaded");
  //NV.stepWeightedVoronoi();
}

Neatview.prototype.computeTotalDensity = function()
{
  var densities = [];
  for(var c = 0; c < this.clusters.length; c++)
  {
    var cluster = this.clusters[c];
    densities.push(cluster.computeDensity());
  }
  NV.clusterDensityMedian = median(densities);
  var totalCount = this.clusters.map(function(c) { return c.count }).reduce(function(a, b) { return a+b });
  var totalArea = this.clusters.map(function(c) { return c.area() }).reduce(function(a, b) { return a+b });
  var totalDensity = totalCount / totalArea;
  console.log('totalDensity', totalDensity);
  return totalDensity;
  //console.log('NV.totalDensity', NV.totalDensity);
}

Neatview.prototype.stepWeightedVoronoi = function()
{
  console.log('stepWeightedVoronoi');

  var _this = this;

  var time = (new Date()).getTime() / 1000.0;
  if(this.lastTime == null)
    this.lastTime = time;
  var timeStep = time - _this.lastTime;


  // calculate forces
  var vertexForces = _this.voronoiVertices.map(function(vertex) { return [0.0, 0.0]});
  var numberOfInfluencers = _this.voronoiVertices.map(function(vertex) { return 0});
  for(var c = 0; c < this.clusters.length; c++)
  {
    var cluster = this.clusters[c];
    cluster.updateDensity();

    // this cluster too big or too small?
    //console.log('my density', cluster.density, 'total', NV.totalDensity);
    //console.log('my power', power);
    //console.log('-----');

    // append cluster's pushPower to cluster's voronoi vertices
    for(var v = 0; v < cluster.boundaryVertices.length; v++)
    {
      var vertexIndex = cluster.boundaryVertices[v];
      var force = cluster.forceOnPoint(_this.voronoiVertices[vertexIndex]).map(function(v) { return timeStep * v });
      vertexForces[vertexIndex][0] += force[0];
      vertexForces[vertexIndex][1] += force[1];
      numberOfInfluencers[vertexIndex]++;
    }
  }
  var maxForce = 0.0;
  for(var vertexIndex = 0; vertexIndex < _this.voronoiVertices.length; vertexIndex++)
  {
    vertexForces[vertexIndex][0] /= numberOfInfluencers[vertexIndex];
    vertexForces[vertexIndex][1] /= numberOfInfluencers[vertexIndex];
    var mag = Math.sqrt(
      Math.pow(vertexForces[vertexIndex][0], 2) + Math.pow(vertexForces[vertexIndex][1], 2) 
    );
    if(mag > maxForce)
      maxForce = mag;
  }

  // update NVVoronoiVertices
  for(var vertexIndex = 0; vertexIndex < _this.voronoiVertices.length; vertexIndex++)
  {
    _this.voronoiVertices[vertexIndex][0] += vertexForces[vertexIndex][0];
    _this.voronoiVertices[vertexIndex][1] += vertexForces[vertexIndex][1];
  }

  // update meshes
  for(var c = 0; c < this.clusters.length; c++)
  {
    this.clusters[c].updateMesh();
  }

  // render
  requestAnimationFrame(function() { _this.render() });

  this.lastTime = time;

  window.setTimeout(function() { _this.stepWeightedVoronoi() }, DELAY);
}

/******* Class Cluster ***********/
function Cluster(data){
  this.data = data;
  this.center = data.center;
  this.count = data.count;
  this.boundaryVertices = data['voronoi_vertices'];

  // can't put a flickr.com URL here unless they enable CORS :(
  // http://enable-cors.org/
  var clusterTexture;
  if(data['image'] !== undefined)
  {
    var imageUrl = data['image']['image_url'];
    clusterTexture = new THREE.ImageUtils.loadTexture( imageUrl, null,
      function() { // onLoad
        NV.loadedOrFailedClusterCount++;
        if(NV.loadedOrFailedClusterCount == NV.clusterCount)
          NV.allClustersLoaded();
      },
      function() { // onFail
        console.warn("NV: A texture failed to load");
        NV.loadedOrFailedClusterCount++;
      }
    );
  }
  else
  {
    clusterTexture = testTexture;
    NV.loadedOrFailedClusterCount++;
  }
 
  var boundaryPoints = this.data['voronoi_vertices'].map(function(vertexIndex) {
    return NV.voronoiVertices[vertexIndex];
  });

  var geometry = new THREE.Geometry();
  geometry.vertices.push( new THREE.Vector3( data.center[1], data.center[0], 0 ) );
  
  for(p = 0; p < data.voronoi_vertices.length; p++)
  {
    geometry.vertices.push( new THREE.Vector3( 0.0, 0.0, 0.0 ) );
  }

  var uv = [];
  for(var v = 0; v < geometry.vertices.length; v++)
  {
    var vertex = geometry.vertices[v];
    uv.push(new THREE.UV( 0.0, 0.0 ));
  }
  for(var f = 1; f <= boundaryPoints.length; f++)
  {
    var v1 = f;
    var v2 = (f % boundaryPoints.length) + 1;
  
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
    opacity: NV.options.opacity,
    //color: 0x991111
  });
  
  this.mesh = new THREE.Mesh( geometry, material );
  this.mesh.position.x = 0.0;
  this.mesh.position.y = 0.0;
  
  NV.scene.add( this.mesh );

  this.updateMesh();
}

Cluster.prototype.forceOnPoint = function(point)
{
  var pushPower = (this.density - NV.totalDensity) / NV.totalDensity;
  
  /*var absDistance = [
    Math.abs(this.center[0] - point[0]),
    Math.abs(this.center[1] - point[1])
  ];
  var signedSquaredDistance = [
    (this.center[0] - point[0]) * absDistance[0],
    (this.center[1] - point[1]) * absDistance[1]
  ];*/
  var angle = Math.atan2(point[0] - this.center[0], point[1] - this.center[1]);
  var forceX = pushPower * Math.cos(angle) / 1000.0;
  var forceY = pushPower * Math.sin(angle) / 1000.0;

  return [forceY, forceX]; // lat, lng = y, x
}

Cluster.prototype.area = function()
{
  var cluster = this;
  var area = 0.0;
  this.mesh.geometry.faces.map(function(face) {
    area += triangleArea([
      cluster.mesh.geometry.vertices[ face.a ],
      cluster.mesh.geometry.vertices[ face.b ],
      cluster.mesh.geometry.vertices[ face.c ]
    ]);
  });
  return area;
}

Cluster.prototype.computeDensity = function()
{
  return this.data.count / this.area();
}

Cluster.prototype.updateDensity = function()
{
  return this.density = this.computeDensity();
}

Cluster.prototype.updateMesh = function()
{
  var left, right, top, bottom;
  left   = this.center[1];
  right  = this.center[1];
  top    = this.center[0];
  bottom = this.center[0];
 
  // do mesh of image
  var p, uv = [];
  var boundaryPoints = this.data['voronoi_vertices'].map(function(vertexIndex) {
    return NV.voronoiVertices[vertexIndex];
  });
  for(p = 0; p < boundaryPoints.length; p++)
  {
    //var point = latLngTranslatedByPointsTowardPoint(boundaryPoints[p], TESSELATION_CANAL_WIDTH, this.center);
    var point = boundaryPoints[p];
    //this.mesh.geometry.vertices.push( new THREE.Vector3( point[1], point[0], 0 ) );
    this.mesh.geometry.vertices[p+1].x = point[1];
    this.mesh.geometry.vertices[p+1].y = point[0];
    left   = Math.min(left, point[1]);
    right  = Math.max(right, point[1]);
    top    = Math.max(top, point[0]);
    bottom = Math.min(bottom, point[0]);
  }
  //var latLngAspect = dgeo.okProjectionAspect(left, right, top, top - (right-left));
  var latLngAspect = (mapBounds.right - mapBounds.left) / (mapBounds.top - mapBounds.bottom);
  var pixelAspect = NV.threeCanvas.width / NV.threeCanvas.height;
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
  for(var v = 0; v < this.mesh.geometry.vertices.length; v++)
  {
    var vertex = this.mesh.geometry.vertices[v];
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
  for(var f = 1; f <= boundaryPoints.length; f++)
  {
    var v1 = f;
    var v2 = (f % boundaryPoints.length) + 1;
  
    //this.mesh.geometry.faces.push( new THREE.Face3( 0, v1, v2 ) );
    this.mesh.geometry.faceVertexUvs[0][f-1] = [ uv[0], uv[v1], uv[v2] ];
  }
  
  this.mesh.geometry.computeBoundingSphere();
  this.mesh.geometry.computeBoundingBox();

  this.mesh.geometry.verticesNeedUpdate = true;
  this.mesh.geometry.uvsNeedUpdate = true;
}
/******* End Cluster *******/

function initNV() {
  NV = new Neatview();
  //$.getJSON('debug', receiveDebug);
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

  NV.scene.add( mesh );
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

    NV.scene.add( polyline );
  }
  
  console.log('debugVoronoiCreate end');
}
