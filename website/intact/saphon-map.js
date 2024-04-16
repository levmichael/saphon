// Asynchronous load of google maps api: https://developers.google.com/maps/documentation/javascript/overview#Loading_the_Maps_API
(g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
  key: "{GOOGLE_MAPS_API_KEY}",
  v: "quarterly",
});

let map;

// Hack for accessing the state of meta and ctrl key from
// inside map event handler.
var metadown = false;

$(window).bind('keydown keyup focusin mouseenter', function(evtobj) {
  metadown = evtobj.metaKey || evtobj.ctrlKey;
});

$(window).bind('focusout mouseleave', function(evtobj) {
  metadown = false;
});

function get_pos(el) {
  for (var lx=0, ly=0;
	 el != null;
	 lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent);
  return {x: lx,y: ly};
}


async function initMap(pglang) {
  const { Map, InfoWindow } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");
  function getIcon( color, text) {
    const pinGlyph = new PinElement({
      background: color,
      title: text
    });
    return pinGlyph;
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
  var myLatlng = new google.maps.LatLng(-4.669119, -60.829511);
  var myOptions = {
    zoom: 5,
    center: myLatlng,
    mapTypeControl: false,
    zoomControl: true,
    panControl: false,
    scaleControl: true,
    streetViewControl: false,
    mapTypeId: google.maps.MapTypeId.TERRAIN,
    mapId: "{GOOGLE_MAP_ID}"
  }

  var map_div = document.getElementById("map")
  var map_pos = get_pos( map_div)
  var map = new Map( map_div, myOptions);
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
    var langs = xml.documentElement.getElementsByTagName("marker"); 

    // Create an info window to share between markers.
    const infoWindow = new google.maps.InfoWindow();

    for (var i = 0; i < langs.length; i++) (function( lang){ 
	var title = lang.getAttribute("title"); 
	var iso_code = lang.getAttribute("iso_code"); 
	var family = lang.getAttribute("family");
	var name = lang.getAttribute("language");
	var link = lang.getAttribute("link");
	var type = lang.getAttribute("labeltype"); 
	var point = new google.maps.LatLng( 
		parseFloat(lang.getAttribute("lat")), 
		parseFloat(lang.getAttribute("lng"))); 
	var bubble = title + " (" + iso_code + `) <br/> ${pglang["family"]}: ` + family;

	const marker = new AdvancedMarkerElement({
	  map: map, 
	  position: point,
          title: bubble,
          content: (family in icons ? icons[family].element : icons["Other"].element),
	});

      if( parm_c != null && parm_c == iso_code) {
        map.panTo( point);
        map.setZoom( 9);
      }

	google.maps.event.addListener(marker, 'mouseover', function() {
        langinfo.innerHTML = `<span class=key>${pglang["language"]}:</span> <b>` + title 
          + `</b> <span class=key>${pglang["code"]}:</span> <b>` + iso_code 
          + `</b> <span class=key>${pglang["family"]}:</span> <b>` + family + "</b>"; 
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
    })( langs[i]);
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
