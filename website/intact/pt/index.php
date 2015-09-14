<?php include("header.php"); ?>

  <script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3.11&sensor=false&language=pt"></script> 
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
  <script type="text/javascript" src="../StyledMarker.js"></script>

  <script type="text/javascript"> 

  // Hack for accessing the state of meta and ctrl key from
  // inside map event handler.
  var metadown = false;

  $(window).bind('keydown keyup focusin mouseenter', function(evtobj) {
    metadown = evtobj.metaKey || evtobj.ctrlKey;
  });

  $(window).bind('focusout mouseleave', function(evtobj) {
    metadown = false;
  });

  function getIcon( color, text) {
    return new StyledIcon( StyledIconTypes.MARKER, {
        color: color,
        text: text})
  }

  var icons = {
    'Tupi' : getIcon( '#2f0', 'T'),
    'Tupí' : getIcon( '#2f0', 'T'),
    'Arawak' : getIcon( '#f00', 'A'),
    'Carib' : getIcon( '#f80', 'C'),
    'Macro-Ge' : getIcon( '#ff0', 'M'),
    'Quechua' : getIcon( '#cf4', 'Q'),
    'Panoan' : getIcon( '#08f', 'P'),
    'Tucanoan' : getIcon( '#00f', 'Tu'),
    'Arawan' : getIcon( '#f08', 'An'),
    'Chibchan' : getIcon( '#faa', 'Cb'),
    'Guaicuru' : getIcon( '#a42', 'G'),
    'Mataco' : getIcon( '#26c', 'Mt'),
    'Jivaroan' : getIcon( '#2aa', 'J'),
    'Witotoan' : getIcon( '#999', 'W'),
    'Barbacoan' : getIcon( '#c48', 'B'),
    'Chapakuran' : getIcon( '#088', 'Cp'),
    'Choco' : getIcon( '#a80', 'Cc'),
    'Guahiban' : getIcon( '#4cf', 'Gh'),
    'Nadahup' : getIcon( '#4fc', 'N'),
    'Nambiquaran' : getIcon( '#4a2', 'Nm'),
    'Tacanan' : getIcon( '#c4f', 'Tn'),
    'Yanomam' : getIcon( '#80c', 'Y'),
    'Zaparoan' : getIcon( '#fc4', 'Z'),
    'Chon' : getIcon( '#fef', 'Ch'),
    'Other' : getIcon( '#ccd', '')
  };
   
  function get_pos(el) {
    for (var lx=0, ly=0;
	 el != null;
	 lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent);
    return {x: lx,y: ly};
  }

  function initialize() { 
    var myLatlng = new google.maps.LatLng(-4.669119, -60.829511);
    var myOptions = {
      zoom: 5,
      center: myLatlng,
      mapTypeControl: false,
      zoomControl: true,
      panControl: false,
      scaleControl: true,
      streetViewControl: false,
      mapTypeId: google.maps.MapTypeId.TERRAIN
    }

    var map_div = document.getElementById("map")
    var map_pos = get_pos( map_div)
    var map = new google.maps.Map( map_div, myOptions);
    var overlay = new google.maps.OverlayView();
    overlay.draw = function() {};
    overlay.setMap( map);
    var langinfo = document.getElementById("langinfo");
    var tooltip = document.getElementById("tooltip");

    // get URL parameter c
    var parm_c = decodeURIComponent((new RegExp('[?|&]c=' + '([^&;]+?)(&|#|;|$)')
      .exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;

    downloadUrl("../lang.xml", function(data) {
      var xml = parseXml(data); 
      var markers = xml.documentElement.getElementsByTagName("marker"); 
      for (var i = 0; i < markers.length; i++) (function(){ 
	var title = markers[i].getAttribute("title"); 
	var iso_code = markers[i].getAttribute("iso_code"); 
	var family = markers[i].getAttribute("family");
	var lang = markers[i].getAttribute("language");
	var link = markers[i].getAttribute("link");
	var type = markers[i].getAttribute("labeltype"); 
	var point = new google.maps.LatLng( 
		parseFloat(markers[i].getAttribute("lat")), 
		parseFloat(markers[i].getAttribute("lng"))); 
	var bubble = title + " (" + iso_code + ") <br/> Familia: " + family;

	var marker = 
	  new StyledMarker({
	    map: map, 
	    position: point,
            styleIcon: family in icons ? icons[family] : icons.Other
	  })

        if( parm_c != null && parm_c == iso_code) {
          map.panTo( point);
          map.setZoom( 9);
        }

	google.maps.event.addListener(marker, 'mouseover', function() {
          langinfo.innerHTML = "<span class=key>Língua:</span> <b>" + title 
            + "</b> <span class=key>Código:</span> <b>" + iso_code 
            + "</b> <span class=key>Familia:</span> <b>" + family + "</b>"; 
	  var projection = overlay.getProjection(); 
	  var pixel = projection.fromLatLngToContainerPixel( 
            marker.getPosition());
	  tooltip.style.top = (map_pos.y + pixel.y - 60) + "px";
	  tooltip.style.left = (map_pos.x + pixel.x - 11) + "px";
	  tooltip.style.padding = "1px 2px"
          tooltip.innerHTML = title;
	});

	google.maps.event.addListener(marker, 'mouseout', function() {
          langinfo.innerHTML = ""
          tooltip.innerHTML = ""
	  tooltip.style.padding = "0"
	});

	google.maps.event.addListener(marker, 'click', function( event) {
          if( metadown) {
            window.open(link);
          } else {
            window.location.href = link;
          }
	});
      })();
    });
	      

    function downloadUrl(url, callback) { 
      var request = window.ActiveXObject ? 
	new ActiveXObject('Microsoft.XMLHTTP') : 
	new XMLHttpRequest; 

      request.onreadystatechange = function() { 
	if (request.readyState == 4) { 
	  request.onreadystatechange = doNothing; 
	  callback(request.responseText, request.status); 
	}
      }; 

      request.open('GET', url, true); 
      request.send(null); 
    } 

    function parseXml(str) { 
      if (window.ActiveXObject) { 
	var doc = new ActiveXObject('Microsoft.XMLDOM'); 
	doc.loadXML(str); 
	return doc; 
      } else if (window.DOMParser) { 
	return (new DOMParser).parseFromString(str, 'text/xml'); 
      } 
    } 
      
    function doNothing() {} 
  }

    //]]> 


  </script>
</head>
<body onload="initialize()">

<?php include("title.php"); ?>
<?php include("nav-languages.php"); ?>
		
</div>


<div id="langinfo"></div> 
<div id="map"></div> 
<div id="tooltip"></div>

</body>
</html>
