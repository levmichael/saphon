from collections import *

# Read in IPA sounds and properties.
# TODO: Error checking on sound info.
soundInfo = OrderedDict()
for line in open('data/ipa_table.txt'):
  if ':' not in line: continue
  position, sounds = re.split(': *', line, 1)
  for sound in re.split(' +', sounds):
    soundInfo[sound] = position

# Predicates on phonemes.
def isVoiced(sound): return soundInfo[sound][3] == 'v'
def isLabialized(sound): return 'ʷ' in sound
def isPalatalized(sound): return 'ʲ' in sound
def isAffricate(sound):
  return soundMap[sound][1] in "aesvp" \
     and soundMap[sound][2] in "AoRP"
def isEjective(sound): return '\'' in sound

# Quantifiers.
def indic(x): return not not x
def count(seq, pred): return sum(pred(x) for x in seq)

def NONE(seq, pred=indic): return count(seq, pred) == 0
def ANY (seq, pred=indic): return count(seq, pred) >= 1
def MANY(seq, pred=indic): return count(seq, pred) >= 2
def ALL (seq, pred=indic): return count(seq, pred) == len(seq)

def writeInventory(
  loc,
  sounds,
  write: String => Unit,
  lump: Boolean = false,
  assemble: (Seq[String] => String) = _.mkString("&nbsp;"),
  assembleTrans: (Seq[String] => String) = _.mkString("&nbsp;"),
  table: Boolean = false)
{
  # Partition sounds into the below 3 data structures.
  c = defaultdict(list) # consonant layout
  v = defaultdict(list) # vowel layout
  nonsounds = [] # non-sound features

  for sound in sounds:
    info = soundInfo[sound]
    if info[0] == 'c':
      c[info[1], info[2]].append(sound)
    elif info[0] == 'v':
      v[info[1], info[2]].append(sound)
    elif info[0] == 's':
      nonsounds.append(sound)

  # Improve layouts.
  mannerLabels, placeLabels    = layoutConsonants(c, lump)
  heightLabels, backnessLabels = layoutVowels    (v, lump)

  # consonant table
  write( "<div class=field><table class=inv>\n")

  for( i <- '?' +: mannerC if i == '?' || mannerS( i) != null) {
    write( "<tr>")
    if( i != '?') { # manner headers
      write( "<td class=header>")
      write( Xlt(loc, mannerS( i))))
      write( "</td>")
    } else {
      write( "<td class=key>")
      write( Xlt(loc, "consonants")))
      write( "</td>")
    }

    for( j <- placeC if placeS( j) != null) {
      if( i == '?') { # place headers
        write( "<td class=header>")
        write( Xlt(loc, placeS( j))))
        write( "</td>")
      } else { # body cells
        write( "<td>")
        write( assemble( c((i,j)).toSeq.sortBy( soundOrderMap( _))))
        write( "</td>")
      }
    }
    write( "</tr>\n")
  }
  write( "</table></div>\n")

  # vowel table
  write( "<div class=field><table class=inv>\n")

  for( i <- '?' +: heightC if i == '?' || heightS( i) != null) {
    write( "<tr>")
    if( i != '?') { # height headers
      write( "<td class=header>")
      write( Xlt(loc, heightS( i))))
      write( "</td>")
    } else {
      write( "<td class=key>")
      write( Xlt(loc, "vowels")))
      write( "</td>")
    }

    for( j <- backnessC if backnessS( j) != null) {
      if( i == '?') { # backness headers
        write( "<td class=header>")
        write( Xlt(loc, backnessS( j))))
        write( "</td>")
      } else { # body cells
        write( "<td>")
        write( assemble( v((i,j)).toSeq.sortBy( soundOrderMap( _))))
        write( "</td>")
      }
    }
    write( "</tr>\n")
  }
  write( "</table></div>\n")

  if( table) {
    write( "<div class=field>\n")
    write( "<div class=key>" 
      ++ Xlt(loc, "suprasegmental")) 
      ++ ":</div>\n")
    write( "<div class=value>")
    write( assembleTrans( ss_))
    write( "</div></div>\n")
  } else if( !ss_.isEmpty) {
    write( "<div class=field><div class=key>" 
      ++ Xlt(loc, "suprasegmental")) 
      ++ "</div><div class=value>")
    write( cap( ss_.map( xlt(loc, _)).mkString( ", ")))
    write( "</div></div>\n")
  }
}

inventoryHead = """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<link rel="stylesheet" type="text/css" href="../../inv.css" />
</head>
<body>
"""

def writeLocal(saphonData, htmlDir, loc):
  metalang = loc.metalang_code

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

    writeInventory(loc, lang.feat_, write)

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
