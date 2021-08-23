def write(saphonData, htmlDir):
  fo = open(htmlDir + '/saphon.php', 'w')
  fo.write("""<?php
$version = "2.1.0";
$n_lang = "%d";
?>""" % len(saphonData.lang_))
  fo.close()
