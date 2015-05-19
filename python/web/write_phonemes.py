
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

