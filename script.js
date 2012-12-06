var w = 1280,
    h = 800,
    spacing = 2,
    scale = 0.5;

var nodes, force, projection;

var svg = d3.select("#body").append("svg:svg")
    .attr("width", window.width)
    .attr("height", window.height);

function zoom() {
  projection.translate(d3.event.translate).scale(d3.event.scale);
  //clusters.selectAll("circle").attr("d", path);
  console.log('zoomed');
}

d3.json("tile.json", function(json) {

  json = json.sort(function(a, b) { return a.count < b.count; });

  nodes = json.map(function(cluster) { return {
	  radius: spacing + scale * Math.sqrt(cluster.count),
	  x: cluster.center[1], y: cluster.center[0],
	  anchor: cluster.center.reverse(),
	  cluster: cluster
      };}),
      color = d3.scale.category10();
  
  var llbounds = new Bounds({
    left: nodes.map(function(d) { return d.anchor[0]; }).reduce(function(a, b){ return Math.min(a, b); }),
    right: nodes.map(function(d) { return d.anchor[0]; }).reduce(function(a, b){ return Math.max(a, b); }),
    bottom: nodes.map(function(d) { return d.anchor[1]; }).reduce(function(a, b){ return Math.min(a, b); }),
    top: nodes.map(function(d) { return d.anchor[1]; }).reduce(function(a, b){ return Math.max(a, b); })
  });

  projection = d3.geo.albers();
  projection.origin(llbounds.center());
  projection.scale(400000);

  var zoom = d3.behavior.zoom()
    .translate(projection.translate())
    .scale(projection.scale())
    .scaleExtent([h, 8 * h])
    .on("zoom", zoom);
    //.on("zoom", function(){ console.log('on zoom thing'); });

  d3.json("us.counties.500k.json", function(counties) {
    var g = svg.append("g").attr("id", "counties");
    g.selectAll("path")
      .data(counties.features)
    .enter().append("path")
      .attr("d", d3.geo.path().projection(projection));
  });
  
  nodes.forEach(function(d){
    var xy = projection([d.x, d.y]);
    d.x = xy[0];
    d.y = xy[1];
  });

  force = d3.layout.force()
      .gravity(0.05)
      //.charge(function(d, i) { return i ? 0 : -2000; })
      //.charge(function(d, i) { return i ? 0 : -2000; })
      .nodes(nodes)
      .size([w, h]);
  
  force.start();
  
  var defs = svg.append("defs");
  defs.selectAll("clipPath")
        .data(nodes)
      .enter().append("clipPath")
        .attr("id", function(d, i){ return i+"-clip"; })
          .append("svg:circle")
            .attr("r", function(d) { return d.radius - spacing; });

  var clusters = svg.append("g")
        .attr("id", "clusters")
        .call(zoom);

  clusters.selectAll("image")
        .data(nodes)
      .enter().append("image")
        .attr("xlink:href", function(d, i){ return d.cluster.image ? d.cluster.image.image_url : ""; })
        .attr("preserveAspectRatio", "xMinYMin slice")
        //.attr("preserveAspectRatio", "none slice")
        .attr("width", function(d){ return d.radius * 2; })
        .attr("height", function(d){ return d.radius * 2; })
        .attr("clip-path", function(d, i){
          return "url(#"+i+"-clip)";
        })
        .on("mouseover", function(d) { console.log(d.cluster.count); })
        .on("click", function(d) { window.location = d.cluster.image.flickr_page_url; })

  var tick = function(e) {
    var q = d3.geom.quadtree(nodes),
        i = 0,
        n = nodes.length;
 
    var k = 1.0 * e.alpha;
    nodes.forEach(function(o, i) {
      var anchorXY = projection(o.anchor);
      o.y += (anchorXY[1] - o.y) * k;
      o.x += (anchorXY[0] - o.x) * k;
    });

    while (++i < n) {
      q.visit(collide(nodes[i]));
    }
  
    svg.selectAll("circle")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });

    clusters.selectAll("image")
         .attr("x", function(d) { return d.x - d.radius; })
         .attr("y", function(d) { return d.y - d.radius; });
  };

  force.on("tick", tick);

});

function collide(node) {
  var r = node.radius + 16,
      nx1 = node.x - r,
      nx2 = node.x + r,
      ny1 = node.y - r,
      ny2 = node.y + r;
  return function(quad, x1, y1, x2, y2) {
    if (quad.point && (quad.point !== node)) {
      var x = node.x - quad.point.x,
          y = node.y - quad.point.y,
          l = Math.sqrt(x * x + y * y),
          r = node.radius + quad.point.radius;
      if (l < r) {
        l = (l - r) / l * .5;
        node.x -= x *= l;
        node.y -= y *= l;
        quad.point.x += x;
        quad.point.y += y;
      }
    }
    return x1 > nx2
        || x2 < nx1
        || y1 > ny2
        || y2 < ny1;
  };
}

function Bounds(params)
{
  for(key in params)
  {
    this[key] = params[key];
  }
}
Bounds.prototype.center = function()
{
  return [
    (this.right + this.left) / 2.0,
    (this.top + this.bottom) / 2.0
  ];
}
