from collections import *

# Quantifiers.
def indic(x): return not not x
def count(seq, pred): return sum(pred(x) for x in seq)

def NONE(seq, pred=indic): return count(seq, pred) == 0
def ANY (seq, pred=indic): return count(seq, pred) >= 1
def MANY(seq, pred=indic): return count(seq, pred) >= 2
def ALL (seq, pred=indic): return count(seq, pred) == len(seq)

# Write a table labeled `name` with `sounds`, using `optimizeLayout`
# to improve the initial layout derived from soundInfo, using
# `formatLabel` to format labels and `formatSounds` to format lists
# of sounds, and using `write` to write.

def writeTable(featInfo, name, sounds, optimizeLayout, formatLabel, formatSounds, write):

  # Define for convenience.
  fa = featInfo.featAttr

  # Create initial layout.
  layout = defaultdict(list)
  for sound in sounds:
    layout[fa[sound][1], fa[sound][2]].append(sound)

  # Improve layouts, get relevant table rows/columns.
  rowLabels, colLabels = optimizeLayout(layout)

  # Write out layout
  write('<div class=field><table class=inv>\n')

  for i in ['?'] + rowLabels.keys():
    write('<tr>')
    if i == '?': # top-left cell
      write('<td class=key>')
      write(formatLabel(name))
      write('</td>')
    else: # row header
      write('<td class=header>')
      write(formatLabel(rowLabels(i)))
      write('</td>')

    for j in colLabels.keys():
      if i == '?': # column header
        write('<td class=header>')
        write(formatLabel(colLabels(j)))
        write('</td>')
      else: # body cells
        write('<td>')
        write(formatSounds(layout[i,j]))
        write('</td>')
    write('</tr>\n')

  write('</table></div>\n')

# Write a field labeled `name` with `nonsounds`, using `formatLabel`
# to format labels and `formatSounds` to format lists of sounds, and
# using `writeField` to write.

def writeNonsounds(name, nonsounds, formatLabel, formatNonsounds, writeField):
  writeField(formatLabel(name), formatNonsounds(nonsounds))

def writeLocal(saphonData, htmlDir, loc):

  # Define for convenience.
  featInfo = saphonData.featInfo
  metalang = loc.metalang_code

  inventoryHead = """
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
  <link rel="stylesheet" type="text/css" href="../../inv.css" />
  </head>
  <body>
  """

  # Create a file for our own use that contains all inventories.
  foMaster = open(htmlDir+'/'+metalang+'/inv/master.html', 'w')
  foMaster.write(inventoryHead)

  for lang in saphonData.lang_:
    fo = open(htmlDir+'/'+metalang+'/inv/'+lang.nameComp+'.html', 'w')
    fo.write(inventoryHead)

    # For writing to master and individual inventories simultaneously.
    def write(s):
      foMaster.write(s)
      fo.write(s)

    def writeField(fieldName, fieldValue):
      write('<div class=field><div class=key>')
      write(Xlt(loc, fieldName))
      write('</div><div class=value>')
      write(fieldValue)
      write('</div></div>\n')

    write('<div class=entry>\n')
    write('<h1>%s</h1>\n' % lang.name)

    if lang.nameAlt_:
      writeField('other names', '; '.join(lang.nameAlt_))

    if lang.iso_:
      writeField('language code', ', '.join(lang.iso_))

    writeField('location', '; '.join(geo.toLatLonString for geo in lang.geo_))

    writeField('family', lang.familyStr)

    writeTable(
      featInfo,
      'consonants',
      filter(isConsonant, soundInfo.keys()),
      lambda layout: optimizeConsonantLayout(featInfo, layout, lump=False),
      lambda label: Xlt(loc, label),
      lambda sounds: '&nbsp'.join(sounds),
      write)

    writeTable(
      featInfo,
      'vowels',
      filter(isVowel, soundInfo.keys()),
      lambda layout: optimizeVowelLayout(featInfo, layout, lump=False),
      lambda label: Xlt(loc, label),
      lambda sounds: '&nbsp'.join(sounds),
      write)

    writeNonsounds(
      'suprasegmentals',
      filter(isSuprasegmental, soundInfo.keys()),
      lambda label: Xlt(loc, label),
      lambda sounds: ', '.join(xlt(loc, sounds)).capitalize(),
      writeField)
      
    if lang.bib_:
      bibStr = ''.join('<p>'+bib+'</p>\n' for bib in lang.bib_)
      writeField('bibliography', bibStr)

    if lang.note_:
      noteStr = ''.join('<p>'+note+'</p>\n' for note in lang.note_)
      writeField('notes', noteStr)
        
    write('</div>\n') # Close class=entry.

    fo.write('</body>\n')
    fo.close()

  foMaster.write('</body>\n')
  foMaster.close()
