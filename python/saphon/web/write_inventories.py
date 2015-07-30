from collections import *

val invHead = """
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<link rel="stylesheet" type="text/css" href="../../inv.css" />
</head>
<body>
"""

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
  tr1: (String => String),
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
      write( cap(tr1(mannerS( i))))
      write( "</td>")
    } else {
      write( "<td class=key>")
      write( cap(tr1("consonants")))
      write( "</td>")
    }

    for( j <- placeC if placeS( j) != null) {
      if( i == '?') { # place headers
        write( "<td class=header>")
        write( cap(tr1(placeS( j))))
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
      write( cap(tr1(heightS( i))))
      write( "</td>")
    } else {
      write( "<td class=key>")
      write( cap(tr1("vowels")))
      write( "</td>")
    }

    for( j <- backnessC if backnessS( j) != null) {
      if( i == '?') { # backness headers
        write( "<td class=header>")
        write( cap(tr1(backnessS( j))))
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
      ++ cap(tr1("suprasegmental")) 
      ++ ":</div>\n")
    write( "<div class=value>")
    write( assembleTrans( ss_))
    write( "</div></div>\n")
  } else if( !ss_.isEmpty) {
    write( "<div class=field><div class=key>" 
      ++ cap(tr1("suprasegmental")) 
      ++ "</div><div class=value>")
    write( cap( ss_.map( tr1(_)).mkString( ", ")))
    write( "</div></div>\n")
  }
}

  # generate inventories
  for( metalang <- List( "en", "es", "pt")) {
    def tr1( s: String) = tr( metalang, s)

    val foAll = new FileWriter( args( 1) ++ "/" ++ metalang ++ "/inv/master.html")
    foAll.write( html.invHead)

    for( lang <- lang_) {
      val fo = new FileWriter( args( 1) ++ "/" ++ metalang ++ "/inv/" ++ lang.nameComp ++ ".html")
      fo.write( html.invHead)

      def write2( s: String) {
        foAll.write( s)
        fo.write( s)
      }

      write2( "<div class=entry>\n")
      write2( "<h1>%s</h1>\n".format( lang.name))

      if( !lang.nameAlt_.isEmpty) {
        write2( "<div class=field><div class=key>" 
          ++ cap(tr1("other names")) 
          ++ "</div><div class=value>")
        write2( lang.nameAlt_.mkString( "; "))
        write2( "</div></div>\n")
      }

      if( !lang.iso_.isEmpty) {
        write2( "<div class=field><div class=key>"
          ++ cap(tr1("language code"))
          ++ "</div><div class=value>")
        write2( lang.iso_.mkString( ", "))
        write2( "</div></div>\n")
      }

      write2( "<div class=field><div class=key>"
        ++ cap(tr1("location"))
        ++ "</div><div class=value>")
      write2( lang.geo_.map( _.toLatLonString).mkString( "; "))
      write2( "</div></div>\n")

      write2( "<div class=field><div class=key>"
        ++ cap(tr1("family"))
        ++ "</div><div class=value>")
      write2( lang.familyStr)
      write2( "</div></div>\n")

      writeInventory( tr1, lang.feat_, write2(_))

      if( !lang.bib_.isEmpty) {
        write2( "<div class=field><div class=key>"
          ++ cap(tr1("bibliography"))
          ++ "</div><div class=value>")
        write2( lang.bib_.mkString( "<p>\n", "</p><p>\n", "</p>\n"))
        write2( "</div></div>\n")
      }

      if( !lang.note_.isEmpty) {
        write2( "<div class=field><div class=key>"
          ++ cap(tr1("notes"))
          ++ "</div><div class=value>")
        for( note <- lang.note_) {
          if( note.toLowerCase.matches( """^\[\w*\].*""")) {
            write2( "<p>\n")
            write2( strip( note.replaceFirst( """^\[\w*\]""", "")))
            write2( "</p>\n")
          } else {
            foAll.write( "<p class=private>\n")
            foAll.write( note)
            foAll.write( "</p>\n")
          }
        }
        write2( "</div></div>\n")
      }
      write2( "</div>\n") # class=entry

      fo.write( "</body>\n")
      fo.close()
    }
    foAll.write( "</body>\n")
    foAll.close()
  }

