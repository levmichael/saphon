
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

