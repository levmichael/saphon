def write(saphonData, htmlDir):
  fo = open(htmlDir + '/saphon.php', 'w')
  fo.write("""<?php
$version = "1.1.4";
$n_lang = "%d";
?>""" % len(saphonData.lang_))
  fo.close()
