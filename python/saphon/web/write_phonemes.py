from collections import *

def writeLocal(saphonData, htmlDir, loc):

  metalang = loc.metalang_code
  filename = loc.find_by_phonemes_phonemes

  fo = open(htmlDir_'/'+metalang+'/'+filename+'.html')
  fo.write('''
    <?php include("header.php"); ?>
    <link rel="stylesheet" media="screen" type="text/css" href="../inv.css"/>
    <link rel="stylesheet" media="screen" type="text/css" href="../chooser.css"/>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js"></script>
    <script type="text/javascript" src="../chooser.js"></script>
    </head>
    <body>
    <?php include("title.php"); ?>
    <?php include("nav-languages.php"); ?>
    <div id="content">\n''')
  fo.write(loc.find_by_phonemes_text)
  fo.write('</div><br/>\n')
  fo.write('<div id=chooser>\n')

  # Get counts for each feature.
  featCount = defaultdict(int)
  for lang in saphonData.lang_:
    for feat in lang.feat_:
      featCount(feat) += 1

  def markup(feat):
    return '<span f=%d%s>%s</span>' % (
      saphonData.featOrder(feat),
      ' class=rare' if featCount(feat) < 4 else '',
      feat)

  def writeField(fieldName, fieldValue):
    write('<div class=field><div class=key>')
    write(Xlt(loc, fieldName) + ':')
    write('</div><div class=value>')
    write(fieldValue)
    write('</div></div>\n')

  writeTable(
    'consonants',
    filter(isConsonant, soundInfo.keys()),
    lambda layout: optimizeConsonantLayout(layout, lump=True),
    lambda label: Xlt(loc, label),
    lambda feats: ''.join(markup(f) for f in feats),
    lambda s: fo.write(s))

  writeTable(
    'vowels',
    filter(isVowel, soundInfo.keys()),
    lambda layout: optimizeVowelLayout(layout, lump=True),
    lambda label: Xlt(loc, label),
    lambda feats: ''.join(markup(f) for f in feats),
    lambda s: fo.write(s))

  writeNonsounds(
    'suprasegmentals',
    filter(isSuprasegmental, soundInfo.keys()),
    lambda label: Xlt(loc, label),
    lambda feats: ''.join(markup(f) for f in feats),
    writeField)

  fo.write('<div class=field><span f=-2>'+loc.find_by_phonemes_more_phonemes+'</span>\n')
  fo.write('<span f=-3>'+loc.find_by_phonemes_fewer_phonemes+'</span>\n')
  fo.write('&nbsp;&nbsp;&nbsp;<span f=-1><b>'+loc.find_by_phonemes_reset+'</b></span></div>\n')
  fo.write('</div><br/>\n')
  fo.write('<div id=languages>\n')
  fo.write('<span>'+loc.find_by_phonemes_matches+':</span> <span class=key>999</span>\n')
  fo.write('<table>\n')

  for lang in lang_:
    attr = ''.join(' f%d=1' % saphonData.featOrder(feat) for feat in lang.feat_)
    fo.write('<tr%s><td><a href="http:inv/%s.html">%s</a></td></tr>\n' %
      (attr, lang.nameComp, lang.name))

  fo.write('</table></div></body>\n')
  fo.close()
