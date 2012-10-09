var dgeo = {

  distanceOnSphericalEarth: function (lat1, long1, lat2, long2)
  {
    // Convert latitude and longitude to 
    // spherical coordinates in radians.
    var degrees_to_radians = Math.PI / 180.0;
        
    // phi = 90 - latitude
    var phi1 = (90.0 - lat1) * degrees_to_radians;
    var phi2 = (90.0 - lat2) * degrees_to_radians;
        
    // theta = longitude
    var theta1 = long1*degrees_to_radians;
    var theta2 = long2*degrees_to_radians;
        
    // Compute spherical distance from spherical coordinates.
        
    // For two locations in spherical coordinates 
    // (1, theta, phi) and (1, theta, phi)
    // cosine( arc length ) = 
    //    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    // distance = rho * arc length
    
    var _cos = Math.sin(phi1)*Math.sin(phi2)*Math.cos(theta1 - theta2) + Math.cos(phi1)*Math.cos(phi2);
    var arc = Math.acos( _cos );

    // Remember to multiply arc by the radius of the earth 
    // in your favorite set of units to get length.
    return arc * 6378100.0;
  },

  okProjectionAspect: function(left, right, top, bottom)
  {
    var degree_width  = (right - left);
    var degree_height = (top - bottom);

    var center_x = left + (right - left) / 2.0;
    var center_y = bottom + (top - bottom) / 2.0;

    var meter_width  = dgeo.distanceOnSphericalEarth(center_y, left, center_y, right);
    var meter_height = dgeo.distanceOnSphericalEarth(bottom, center_x, top, center_x);

    var degreeAspect = degree_width / degree_height;
    var meterAspect = meter_width / meter_height;

    //console.log(degreeAspect, '-->', meterAspect);

    return meterAspect;
  }

} // end dgeo
