

function date_string_to_timestamp(str) {
    var parts = str.split('/');
    return new Date(parts[2], parts[0] - 1, parts[1], 0, 0, 0, 0).getTime() / 1000;
}

function initialize() {

    var center = new google.maps.LatLng((40.878582000732536 + 40.700420379638786) / 2.0, (-73.91047668457026 + -74.02426147460932) / 2.0)


    var mapOptions = {
        zoom: 13,
        center: center,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);


    var rectangles = [];
    var mean_shift_paths = [];

    function update() {
        //$('#image_count').load('/image_count');

        $.getJSON('/mines.json', function (data) {

            for (r in rectangles) {
                rectangles[r].setMap(null);
            }
            rectangles = [];

            var avgX = 0.0;
            var avgY = 0.0;

            var count = 0;
            var rectsString = "";
            $.each(data, function (key, val) {

                var rectangle = new google.maps.Rectangle();
                var sw = new google.maps.LatLng(val['bbox']['bottom'], val['bbox']['left']);
                var ne = new google.maps.LatLng(val['bbox']['top'], val['bbox']['right']);
                var rectBounds = new google.maps.LatLngBounds(sw, ne);
                var rectOptions = {
                    strokeColor: '#FF0000',
                    strokeOpacity: 0.8,
                    strokeWeight: 1,
                    //fillColor: '#FF0000',
                    //fillOpacity: 0.35,
                    map: map,
                    bounds: rectBounds
                };
                rectangle.setOptions(rectOptions);
                rectangles.push(rectangle);

                rectsString += sw.toString() + "<br>";
            });

            $('#delete_mines').html("Delete All " + rectangles.length + " Mines");

            $('#rectList').html(rectsString);


        });

        setTimeout(update, 2000);
    }

    function handle_meanshifts(data) {
        for (p in mean_shift_paths) {
            mean_shift_paths[p].setMap(null);
        }
        mean_shift_paths = []
        console.log(data.length + " meanshifts in window")
	var step = 1;
	if(data.length > 1000) {
	   step = Math.floor(data.length / 1000)
           console.log('too many meanshifts! showing ~1,000');
	}
        for (var i = 0; i < data.length; i += step) {
            var rawPath = data[i];
            var path = [];
            for (p in rawPath) {
                path.push(new google.maps.LatLng(rawPath[p][0], rawPath[p][1]));
            }
            var opts = {
                clickable: false,
                map: map,
                path: path,
                strokeWeight: 2.0,
                strokeOpacity: 0.5,
                strokeColor: 'black'
            };
            mean_shift_paths.push(new google.maps.Polyline(opts));
        }

        setTimeout(requestMeanshifts, 2000);
    }


    var clusters = [];

    function attachLink(item, url){
       google.maps.event.addListener(item, 'click', function (e) {
	  window.open(url);
       });
    }


    function clearClusters()
    {
        for (c in clusters) {
            clusters[c].setMap(null);
        }
        clusters = [];
    }

    function handle_clusters(data) {
       clearClusters();

       console.log('NV Clusters:', data);
        
	NVMakeClusters(data);
        
	for (var clusterIndex = 0; clusterIndex < data.length; clusterIndex++) {
	    // parse cluster
	    var cluster = data[clusterIndex];
            var center = cluster['center'];
            var _id = cluster['_id'];
            var radius = 'count' in cluster ? cluster['count'] / 10.0 : 100.0;
            if('convex_hull' in cluster && cluster['convex_hull'].length > 0)
	    {
	       // convex hull
	       convex_hull = cluster['convex_hull'];


               var coords = [];
	       for(var pointIndex = 0; pointIndex < convex_hull.length; pointIndex++)
	       {
	          var point = convex_hull[pointIndex];
                  coords.push(new google.maps.LatLng(point[0], point[1]));
	       }
	       var polygon = new google.maps.Polygon({
                  paths: coords,
		  strokeWeight: 0.5,
		  fillOpacity:0.0,
		  strokeOpacity:0.0, // let THREE draw cool stuff, this poly just takes mouse events
		  map: map
	       });
               attachLink(polygon, cluster['flickr_page_url']);
	       clusters.push(polygon);
	    }
            
            // create cluster's circle
            /*var circleOpts = {
                center: new google.maps.LatLng(center[0], center[1]),
                radius: radius,
		map: map
            }
            var circle = new google.maps.Circle(circleOpts);
            attachLink(circle, _id);
            clusters.push(circle);*/

   /*         var path = [];
            for (p in rawPath) {
                path.push(new google.maps.LatLng(rawPath[p][0], rawPath[p][1]));
            }
            var opts = {
                clickable: false,
                map: map,
                path: path,
                strokeWeight: 2.0,
                strokeOpacity: 0.5,
                strokeColor: 'black'
            };
            mean_shift_paths.push(new google.maps.Polyline(opts));*/
        }

        //setTimeout(requestCenters, 2000);
    }




    function requestClusters() {
        var params;
        var bounds = map.getBounds();
        if (typeof bounds !== "undefined") {
            params = {
                //'left': map.getBounds().getSouthWest().lng(),
                //'bottom': map.getBounds().getSouthWest().lat(),
                //'right': map.getBounds().getNorthEast().lng(),
                //'top': map.getBounds().getNorthEast().lat(),
            };
        } else {
            params = {}
            console.log("bounds undefined!!!!!");
        }

        console.log("about to do clusters request");
        $.getJSON('clusters', params, handle_clusters);
    }





    function requestMeanshifts() {
        var params;
        var bounds = map.getBounds();
        if (typeof bounds !== "undefined") {
            params = {
                'left': map.getBounds().getSouthWest().lng(),
                'bottom': map.getBounds().getSouthWest().lat(),
                'right': map.getBounds().getNorthEast().lng(),
                'top': map.getBounds().getNorthEast().lat(),
            };
        } else {
            params = {}
            console.log("bounds undefined!!!!!");
        }

        console.log("about to do meanshifts request");
        $.getJSON('/mean_shifts.json', params, handle_meanshifts);
    }

    var annotationSW = new google.maps.LatLng(0.0, 0.0);
    var annotationNE = new google.maps.LatLng(0.0, 0.0);
    var flip = 0;
    var annotationRect = new google.maps.Rectangle();
    var rectBounds = new google.maps.LatLngBounds(annotationSW, annotationNE);
    var rectOptions = {
        strokeColor: '#3300CC',
        strokeOpacity: 0.8,
        strokeWeight: 1,
        //fillColor: '#FF0000',
        fillOpacity: 0.05,
        map: map,
        bounds: rectBounds
    };
    annotationRect.setOptions(rectOptions);

    //###################################
    //       Console mode
    //###################################
    if(NV.mode == 'console')
    {
    google.maps.event.addListener(map, 'rightclick', function (e) {
        console.log(e.latLng.toString());
        $.ajax({
            method: "GET",
            url: "/mean_shift",
            data: {
                'lat': e.latLng.lat(),
                'lng': e.latLng.lng()
            },
            //success: success
        });
    });

    google.maps.event.addListener(map, 'click', function (e) {
        if (flip == 0) annotationSW = e.latLng;
        else annotationNE = e.latLng;
        flip = (flip + 1) % 2;
        var rectBounds = new google.maps.LatLngBounds(annotationSW, annotationNE);
        annotationRect.setBounds(rectBounds);

        var min_date = date_string_to_timestamp($('#min_upload_time').val());
        var max_date = date_string_to_timestamp($('#max_upload_time').val());
        mine_params = '{"min_upload_time":' + min_date + ', "max_upload_time":' + max_date + ', "bbox": { "left":' + annotationSW.lng() + ', "right":' + annotationNE.lng() + ', "top":' + annotationNE.lat() + ', "bottom":' + annotationSW.lat() + ' } }';
        $('#rect').html(mine_params);
    });



    $("#min_upload_time").datepicker();
    $("#max_upload_time").datepicker();


    $('#create_mine').click(function () {
        console.log("hello rfom submitter");

        var min_date = date_string_to_timestamp($('#min_upload_time').val());
        var max_date = date_string_to_timestamp($('#max_upload_time').val());

        mine_params = '{"min_upload_time":' + min_date + ', "max_upload_time":' + max_date + ', "bbox": { "left":' + annotationSW.lng() + ', "right":' + annotationNE.lng() + ', "top":' + annotationNE.lat() + ', "bottom":' + annotationSW.lat() + ' } }';
        $.ajax({
            type: 'POST',
            url: "/create_mine",
            data: mine_params,
            success: function (data, textStatus) {
                console.log("Create mine: " + textStatus + " - " + data);
            },
            dataType: 'text'
        });
    });

    $('#delete_mines').click(function () {
        if (confirm('Do you really want to DELETE ALL MINES?')) {
            $.ajax({
                type: 'GET',
                url: "/delete_all_mines",
                //data: ,
                success: function (data, textStatus) {
                    console.log("Delete all mines: " + textStatus + " - " + data);
                },
                dataType: 'text'
            });

        }
    });

    }

    initNV();
    animateNV();

    setTimeout(requestClusters, 1000);
};

