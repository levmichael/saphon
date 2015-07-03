
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

