<?php include("header.php"); ?>

  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
  <script type="text/javascript" src="../saphon-map.js"></script>

  <script type="text/javascript">
    const translation = {
      "code": "Código",
      "family": "Familia",
      "language": "Lengua",
    };
  </script>

</head>
<body onload="initMap(translation)">

<?php include("title.php"); ?>
<?php include("nav-languages.php"); ?>
		
</div>


<div id="langinfo"></div> 
<div id="map"></div> 
<div id="tooltip"></div>

</body>
</html>
