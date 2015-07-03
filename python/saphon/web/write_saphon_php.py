
  # Language count
  ;{
    val fo = new FileWriter( "%s/saphon.php".format( args(1)))
    fo.write(
"""<?php
$version = "1.1.3";
$n_lang = "%d";
?>""".format( lang_.length))
    fo.close()
  }
