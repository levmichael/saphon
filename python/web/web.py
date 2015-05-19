object Inventories extends App {

  if( args.length < 2) {
     println( "Two filepaths required.")
     System.exit( 1)
  }

  val (family_, feat_, area_, lang_) = Saphon.readLanguages( args(0))
  val K = feat_.length

placeC, placeS0 = zip(
  ('b', "bilabial"),
  ('l', "labio=dental"),
  ('d', "dental"),
  ('a', "alveolar"),
  ('A', "alveolar"),
  ('o', "post=alveolar"),
  ('r', "retroflex"),
  ('R', "retroflex"),
  ('p', "palatal"),
  ('P', "palatal"),
  ('v', "velar"),
  ('q', "labio=velar"),
  ('u', "uvular"),
  ('f', "pharyngeal"),
  ('g', "glottal"),
  ('x', "unspe=cified"))

mannerC, mannerS0 = zip(
  ('a', "aspirated@stop"),
  ('e', "stop"),  # ejective/creaky stops, exact name TBD.
  ('s', "stop"),
  ('v', "voiced@stop"),
  ('p', "prenasalized@stop"),
  ('i', "implosive@stop"),
  ('A', "affricate"),
  ('f', "fricative"),
  ('n', "nasal"),
  ('x', "approximant"),
  ('r', "trill"),
  ('t', "tap, flap"),
  ('l', "lateral"))

heightC, heightS0 = zip(
  ('7', "high"),
  ('6', "near high"),
  ('5', "mid-high"),
  ('4', "mid"),
  ('3', "mid-low"),
  ('2', "near low"),
  ('1', "low"))

backnessC, backnessS0 = zip(
  ('f', "front"),
  ('c', "central"),
  ('b', "back"))

roundednessC, roundednessS0 = zip(
  ('u', "unrounded"),
  ('r', "rounded"))

# text and unicode routines
def cap(s): s[0].upper() + s[1:]

def uncap(s): "" if s == "" else s[0].lower() +: s[1:]

def normalize(s):
  # TODO
  # Normalizer.normalize( s, Normalizer.Form.NFKD)
  #   .replaceAll( "\\p{InCombiningDiacriticalMarks}+", "")
  #   .replaceAll( "ɨ", "i")
  #   .replaceAll( "ʔ", "")
  #   .toLowerCase
  s

  # translator
  val tr = {
    # read translation table
    val javaRow_ = new CSVReader( new FileReader( "data/trans-table.csv")).readAll()
    # the uncapping is a small hack!
    val row_ = javaRow_.toIndexedSeq.map(
      (row: Array[ java.lang.String]) => row.toIndexedSeq
        .map( (s: String) => uncap( strip( s))))
    val trmap = HashMap.empty[(String, String), String]
    for( row <- row_) {
      if( row( 1) != "") {
        val key = if( row( 0) == "") row( 1) else row( 0) 
        trmap( ("en", key)) = row( 1)
        trmap( ("es", key)) = row( 2)
        trmap( ("pt", key)) = row( 3)
      }
    }

    def tr( metalang: String, s: String) = {
      val x_ = for( x <- s.split( """@""")) yield {
        (for( s <- x.split( """\/""")) yield {
          if( !trmap.isDefinedAt( (metalang, s))) {
            println( "WARNING: Cannot translate %s %s".format( metalang, s))
          }
          trmap.getOrElse( (metalang, s), s)
        }).mkString( "/")
      }
      val t = if( x_.length == 1) x_(0)
        else if( metalang == "en") x_(0) ++ " " ++ x_(1)
        else x_(1) ++ " " ++ x_(0)
      t.replaceAll( "=", "-<br/>")
    }
    tr _
  }

  # read in IPA chart info
  var soundOrder_ = Seq.empty[ String]
  val soundMap = Map.empty[ String, String]
  for( l <- io.Source.fromFile( "data/ipa-table.txt").getLines()
       if l contains ':')
  {
    val (position, sounds) = l.splitAt( l.indexWhere( _ == ':'))
    if( position == "s") {
      val sound = sounds
        .replaceAll( """^:\s*""", "")
        .replaceAll( """\s*$""", "")
      soundMap( sound) = position
      soundOrder_ = soundOrder_ :+ sound
    } else {
      val sound_ = sounds
        .replaceAll( """^:\s*""", "")
        .replaceAll( """\s*$""", "")
        .split( """\s+""")
        .map( Saphon.decompose( _))
      for( sound <- sound_) soundMap( sound) = position
      soundOrder_ = soundOrder_ ++ sound_
    }
  }
  val soundOrderMap = Map( soundOrder_.zipWithIndex:_*)

  # define IPA routines
  def insert[T]( t_ : Seq[T], i: Int, t: T) = {
      (t_.slice( 0, i) :+ t) ++ t_.slice( i, t_.length)
  }
  def voice( sound: String) = soundMap( sound)( 3) == 'v'
  def labialized( sound: String) = sound contains 'ʷ'
  def palatalized( sound: String) = sound contains 'ʲ'
  def affricate( sound: String) = {
    ("aesvp" contains soundMap( sound)( 1)) &&
    ("AoRP" contains soundMap( sound)( 2))
  }
  def ejective( sound: String) = sound contains '\''

  def not[T]( f: T => Boolean) = (x:T) => !f(x)
  def opposition[T]( f: T => Boolean, sound_ : Seq[T]): Boolean = {
    val b_ = sound_.map( f( _))
    (b_ contains true) && (b_ contains false)
  }
  def any[T]( f: T => Boolean, sound_ : Seq[T]): Boolean = {
    !sound_.forall( !f( _))
  }
  def none[T]( f: T => Boolean, sound_ : Seq[T]): Boolean = {
    sound_.forall( !f( _))
  }
  def I( x: Boolean) = if( x) 1 else 0

  case class SeqRef[T]( var seq: Seq[T]) {
    def klone() = copy()
  }
  implicit def convert_SeqRef_Seq[T]( sr: SeqRef[ T]) = sr.seq
  implicit def convert_Seq_SeqRef[T]( s: Seq[ T]) = new SeqRef( s)

  def move( t_ : MutSet[ String], s_ : MutSet[ String],
    f: String => Boolean = (s => true)) 
  {
    val u_ = s_.filter( f)
    t_.seq ++= u_
    s_.seq --= u_
  }

  class IPAMap extends HashMap[ (Char,Char), MutSet[ String]] { 
    override def default( key:(Char, Char)) = {
      val v = MutSet.empty[String]
      this.update( key, v)
      v
    }
    def klone() = {
      val m = new IPAMap()
      for( (k,v) <- this.toSeq) {
        m( k) = v.clone()
      }
      m
    }
    def dump() = {
      for( (k,v) <- this.toSeq if !v.isEmpty) {
        println( k, v.toSeq.mkString( " "))
      }
    }
  }

  def writeInventory(
    tr1: (String => String),
    hasFeat_ : IndexedSeq[Int], write: String => Unit,
    lump: Boolean = false,
    assemble: (Seq[String] => String) = _.mkString("&nbsp;"),
    assembleTrans: (Seq[String] => String) = _.mkString("&nbsp;"),
    table: Boolean = false)
  {
    var mannerS = HashMap( (mannerC zip mannerS0):_*)
    var placeS = HashMap( (placeC zip placeS0):_*)

    var heightS = HashMap( (heightC zip heightS0):_*)
    var backnessS = HashMap( (backnessC zip backnessS0):_*)

    var c = new IPAMap()
    var v = new IPAMap() 
    var ss_ = Seq.empty[String]
    for( k <- 0 until K if hasFeat_( k) == 1) {
      val sound = feat_( k)
      val pos = soundMap( sound)
      if( pos( 0) == 'c') {
        val i = mannerC.indexWhere( _ == pos( 1))
        val j = placeC.indexWhere( _ == pos( 2))
        assert( i >= 0 && j >= 0, println( "Bad location '%s' for sound [%s].".format( pos, sound)))
        c( (pos(1), pos(2))) += sound
      } else if( pos( 0) == 'v') {
        val i = heightC.indexWhere( _ == pos( 1))
        val j = backnessC.indexWhere( _ == pos( 2))
        assert( i >= 0 && j >= 0, println( "Bad location '%s' for sound [%s].".format( pos, sound)))
        v( (pos(1), pos(2))) += sound
      } else if( pos( 0) == 's') {
        ss_ = ss_ :+ sound
      } else {
        assert( false, println( "Bad location '%s' for sound [%s].".format( pos, sound)))
      }
    }

    # split stops if it's the only row with voice opposition
    {
      val save_c = c.klone()

      if( placeC.map( j => opposition( voice, c(('s',j)).toSeq)).reduce(_||_))
        for( j <- placeC)
          move( c(('v',j)), c(('s',j)), voice)

      if( !c.forall( x => !opposition( voice, x._2.toSeq))) c = save_c
    }

    # move palatovelars to palatal column if possible
    {
      val save_c = c.klone()

      var revert = false

      # move palatalized segments over
      for( j <- placeC if j != 'p') {
        for( i <- mannerC) {
          if( !c((i, 'p')).isEmpty && 
              !c((i, j)).filter( palatalized( _)).isEmpty)
          {
            revert = true
          }
          move( c((i, 'p')), c((i, j)), palatalized)
        }
      }

      if( revert) c = save_c
    }

    # create labiovelar column
    {
      val save_c = c.klone()

      # move labialized velars over
      for( i <- mannerC)
        move( c((i,'q')), c((i,'v')), labialized)

      # move h^w over if possible
      if( c(('f','q')).isEmpty)
        move( c(('f','q')), c(('f','g')), labialized)

      # move w over if labiovelar column is not empty
      if( !mannerC.map( i => c((i,'q'))).flatten.isEmpty) {
        move( c(('x','q')), c(('x','b')))
      }

      # check that no labial opposition remains, else revert
      if( !c.forall( x => !opposition( labialized, x._2.toSeq))) c = save_c
    }

    # create affricate row
    {
      val m = collection.immutable.Map(('A','a'),('R','r'),('P','p'))
      val ii = MutSet.empty[Char]
      var narrower = 0
      for( i <- mannerC; j <- placeC; s <- c((i,j))) {
        if( affricate( s)) {
          ii += i
          if( m contains j) {
            if( !c((i,m( j))).isEmpty) narrower += 1
          }
        }
      }
      if( ii.size == 1 && narrower > 0) {
        val i = ii.head
        for( j <- placeC)
          move( c(('A',j)), c((i,j)), affricate)
      }
    }

    # collapse retroflex and palatal columns if possible
    for( (j1,j2) <- List(('a','A'),('r','R'),('p','P'))) {
      if( lump || !mannerC.map( i => !c((i,j1)).isEmpty && 
            !c((i,j2)).isEmpty).reduce( _ || _))
      {
        for( i <- mannerC) {
          move( c((i,j1)), c((i,j2)))
        }
      }
    }

    if( lump) {
      for( i <- mannerC) {
        move( c((i,'b')), c((i,'l')))
        move( c((i,'v')), c((i,'q')))
        move( c((i,'u')), c((i,'f')))
        move( c((i,'u')), c((i,'g')))
        move( c((i,'u')), c((i,'x')))
      }
      for( j <- placeC) {
        move( c(('x',j)), c(('r',j)))
        move( c(('x',j)), c(('t',j)))
        move( c(('e',j)), c(('i',j)))
      }
      placeS( 'u') = "pvus"
      placeS( 'b') = "labial"
      mannerS( 'x') = "attf"
    }

    # rename rows
    {
      var nonPlainStops = false
      for( i <- "aesvp") {
        val sSound_ = placeC.map( j => c((i,j))).flatten
        if( i != 's' && sSound_.length > 0) {
          nonPlainStops = true
        }
        if( any( affricate, sSound_)) {
          mannerS( i) ++= "/affricate"
        }
      }
      if( nonPlainStops) {
        val sSound_ = placeC.map( j => c(('s',j))).flatten
        if( any( voice, sSound_)) {
          mannerS( 's') = "plain/voiced@" ++ mannerS( 's')
        } else {
          mannerS( 's') = "plain@" ++ mannerS( 's')
        }
      }

      val eSound_ = placeC.map( j => c(('e',j))).flatten
      if( !eSound_.isEmpty) {
        val e1 = any( ejective, eSound_)
        val e0 = any( not( ejective), eSound_)
        if( lump) {
          mannerS( 'e') = "glottalized@" ++ mannerS( 'e')
        } else if( e1 && e0) {
          mannerS( 'e') = "ejective/creaky@" ++ mannerS( 'e')
        } else if( e1) {
          mannerS( 'e') = "ejective@" ++ mannerS( 'e')
        } else {
          mannerS( 'e') = "creaky@" ++ mannerS( 'e')
        }
      }
    }

    # delete empty rows/columns
    for( i <- mannerC) {
      if( placeC.map( j => c((i,j))).flatten.isEmpty) mannerS( i) = null
    }
    for( j <- placeC) {
      if( mannerC.map( i => c((i,j))).flatten.isEmpty) placeS( j) = null
    }

    # collapse mid-high, mid, mid-low
    {
      var nogo = false
      for( j <- backnessC) {
        val filled = I( !v(('5',j)).isEmpty) +
          I( !v(('4',j)).isEmpty) +
          I( !v(('3',j)).isEmpty)
        if( filled > 1) nogo = true
      }
      if( !nogo) {
        for( j <- backnessC) {
          move( v(('4',j)), v(('3',j)))
          move( v(('4',j)), v(('5',j)))
        }
      }
    }

    # juggle ash and type-a
    {
      if( v(('1','f')).isEmpty && !v(('2','f')).isEmpty)
        move( v(('1','f')), v(('2','f')))
      if( v(('1','f')).isEmpty && !v(('1','c')).isEmpty && !v(('1','b')).isEmpty)
        move( v(('1','f')), v(('1','c')))
    }

    # move near-low to low if possible
    {
      var nogo = false
      for( j <- backnessC) {
        if( !v(('2',j)).isEmpty && !v(('1',j)).isEmpty) nogo = true
      }
      if( !nogo) {
        for( j <- backnessC) {
          if( !v(('2',j)).isEmpty) {
            move( v(('1',j)), v(('2',j)))
          }
        }
      }
    }

    # move near-high to high if possible
    {
      var nogo = false
      for( j <- backnessC) {
        if( !v(('6',j)).isEmpty && !v(('7',j)).isEmpty) nogo = true
      }
      if( !nogo) {
        for( j <- backnessC) {
          if( !v(('6',j)).isEmpty) {
            move( v(('7',j)), v(('6',j)))
          }
        }
      }
    }

    if( lump) {
      for( j <- backnessC) {
        move( v(('7',j)), v(('6',j)))
        move( v(('1',j)), v(('2',j)))
        move( v(('4',j)), v(('5',j)))
        move( v(('4',j)), v(('3',j)))
      }
    }

    # delete empty rows/columns
    for( i <- heightC) {
      if( backnessC.map( j => v((i,j))).flatten.isEmpty) heightS( i) = null
    }
    for( j <- backnessC) {
      if( heightC.map( i => v((i,j))).flatten.isEmpty) backnessS( j) = null
    }

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

  # index pages
  def writeIndices( 
    metalang: String,
    indexHead: String,
    fname_ : List[ String],
    th_ : List[ String],
    altText_ : List[ String])
  {
    val keyFn_ = List[Lang => Seq[(String,Lang)]](
      l => for( name <- l.name +: l.nameAlt_) 
        yield { (normalize( name), l.copy( name=name))},
      l => for( iso <- l.iso_) yield { (normalize( iso), 
        l.copy( iso_ = iso +: l.iso_.filterNot( _ == iso))
      )},
      l => Seq( (normalize( strip( l.familyStr)) ++ " " ++ normalize( strip( l.name)), l)),
      l => {
        (for( country <- l.country_) yield { (normalize( country) ++ " " ++ normalize( strip( l.name)),
          l.copy( country_ = country +: l.country_.filterNot( _ == country))
      )})})

    for( alt <- List( false, true);
         i <- 0 until th_.length)
    {
      val altS = if( alt) "-alt" else ""
      val altSO = if( alt) "" else "-alt"

      val fo = new FileWriter( args( 1) ++ "/" ++ metalang ++ "/" ++ fname_(i) ++ altS ++ ".php")
      fo.write( indexHead)
      fo.write( "<table class=index><tr>\n")
      for( j <- 0 until th_.length) {
        fo.write( "<th>")
        if( i == j) {
          fo.write( th_( j) ++ "<br/>" ++ "<span><a href=\"" ++ 
            fname_( i) ++ altSO 
            ++ ".php\">" ++ 
            altText_( if( alt) 1 else 0) ++ "</a></span>")
        } else {
          fo.write( "<a href=\"" ++ fname_( j) ++ altS ++ ".php\">" ++ 
            th_( j) ++ "</a>")
        }
        fo.write( "</th>")
      }
      fo.write( "<th></th>")

      val kv_ = lang_.map( keyFn_( i)( _).take( if( alt) 100 else 1)).flatten
      for( (k,lang) <- kv_.sortBy( _._1)) {
        fo.write( "</tr><tr>\n")
        fo.write( "<td><a href=\"inv/" ++ lang.nameComp ++ ".html\">" ++ lang.name ++ "</a></td>")
        fo.write( "<td>" ++ lang.iso_.mkString( ", ") ++ "</td>")
        fo.write( "<td>" ++ lang.familyStr ++ "</td>")
        fo.write( "<td>" ++ lang.country_.mkString( ", ") ++ "</td>")
        fo.write( "<td><a href=\"./?c=%s\">%s</a></td>".format( lang.iso_( 0), 
          cap( tr( metalang, "map"))))
      }

      fo.write( "</tr></table>\n")
      fo.write( "</body>\n")
      fo.close()
    }
  }

  writeIndices( 
    "en",
    en.language_lists_text,
    en.language_lists_sort_method,
    en.language_lists_columns,
    en.language_lists_show_alternatives)

  writeIndices( 
    "es",
    es.language_lists_text,
    es.language_lists_sort_method,
    es.language_lists_columns,
    es.language_lists_show_alternatives)

  writeIndices( 
    "pt",
    pt.language_lists_text,
    pt.language_lists_sort_method,
    pt.language_lists_columns,
    pt.language_lists_show_alternatives)

  # map locations
  ;{
    val fo = new FileWriter( args( 1) ++ "/lang.xml")
    fo.write( "<markers>\n")
    for( l <- lang_) {
      fo.write( "  <marker title=\"" ++ l.name ++ "\" " ++
        "iso_code=\"" ++ l.iso_(0) ++ "\" " ++
        "language=\"" ++ l.name ++ "\" " ++
        "family=\"" ++ l.familyStr ++ "\" " ++
        "labeltype=\"type1\" " ++
        "link=\"http:inv/" ++ l.nameComp ++ ".html\" " ++
        "lat=\"" ++ l.geo_(0).lat.toString ++ "\" " ++
        "lng=\"" ++ l.geo_(0).lon.toString ++ "\" />\n"
      )
    }
    fo.write( "</markers>\n")
    fo.close()
  }

  # lookup by phonemes
  def write_find_by_phonemes(
    metalang: String,
    filename: String,
    html_instructions: String,
    text1a: String,
    text1b: String,
    text2: String,
    text3: String
  ) {
    val fo = new FileWriter( "%s/%s/%s.php".format( args(1), metalang, filename))
    fo.write(
      """
        <?php include("header.php"); ?>
        <link rel="stylesheet" media="screen" type="text/css" href="../inv.css"/>
        <link rel="stylesheet" media="screen" type="text/css" href="../chooser.css"/>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js"></script>
        <script type="text/javascript" src="../chooser.js"></script>
        </head>
        <body>
        <?php include("title.php"); ?>
        <?php include("nav-languages.php"); ?>
        <div id="content">
      """ ++ html_instructions ++
      """
        </div><br/>
      """)
    fo.write( "<div id=chooser>\n")

    # count phonemes
    val featCount_ = ArrayBuffer.fill( soundOrder_.size)( 0)
    for( l <- lang_; k <- 0 until K) 
      featCount_( soundOrderMap( feat_( k))) += l.feat_( k)

    writeInventory( tr( metalang, _),
      IndexedSeq.fill( K)( 1), fo.write( _), true,
      _.map( s => "<span f=%d%s>%s</span>".format( 
        soundOrderMap( s), 
        if( featCount_( soundOrderMap( s)) >= 4) "" else " class=rare",
        s)).mkString(""),
      _.map( s => "<span f=%d%s>%s</span>".format( 
        soundOrderMap( s), 
        if( featCount_( soundOrderMap( s)) >= 4) "" else " class=rare",
        tr( metalang, s))).mkString(""),
      true
    )
    fo.write( "<div class=field><span f=-2>%s</span>\n".format( text1a))
    fo.write( "<span f=-3>%s</span>\n".format( text1b))
    fo.write( "&nbsp;&nbsp;&nbsp;<span f=-1><b>%s</b></span></div>\n".format( text2))
    fo.write( "</div><br/>\n")
    fo.write( "<div id=languages>\n")
    fo.write( "<span>%s:</span> <span class=key>999</span>\n".format( text3))
    fo.write( "<table>\n")

    for( l <- lang_.sortBy( l => normalize( l.name))) {
      val f_ = l.feat_.zipWithIndex.filter( _._1 == 1)
        .map( x => " f%d=1".format( soundOrderMap( feat_( x._2))))
      fo.write( "<tr%s><td><a href=\"http:inv/%s.html\">%s</a></td></tr>\n"
        .format( f_.mkString(""), l.nameComp, l.name))
    }
    fo.write( "</table></div></body>\n")
    fo.close()
  }

  write_find_by_phonemes( 
    "en",
    en.find_by_phonemes_phonemes,
    en.find_by_phonemes_text,
    en.find_by_phonemes_more_phonemes,
    en.find_by_phonemes_fewer_phonemes,
    en.find_by_phonemes_reset,
    en.find_by_phonemes_matches)

  write_find_by_phonemes( 
    "es",
    es.find_by_phonemes_phonemes,
    es.find_by_phonemes_text,
    es.find_by_phonemes_more_phonemes,
    es.find_by_phonemes_fewer_phonemes,
    es.find_by_phonemes_reset,
    es.find_by_phonemes_matches)

  write_find_by_phonemes( 
    "pt",
    pt.find_by_phonemes_phonemes,
    pt.find_by_phonemes_text,
    pt.find_by_phonemes_more_phonemes,
    pt.find_by_phonemes_fewer_phonemes,
    pt.find_by_phonemes_reset,
    pt.find_by_phonemes_matches)


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
}

