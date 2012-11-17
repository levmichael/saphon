package saphon

import collection.mutable.HashMap
import collection.mutable.Set
import scala.collection.JavaConversions._
import java.io.FileReader
import java.io.FileWriter
import java.text.Normalizer
import au.com.bytecode.opencsv._
import scala.math._

case class Geo (
  lat: Double,
  lon: Double,
  elv: Double
) {
  def toDMS( x: Double) = {
    val y = x + 0.5 / 3600.  // for rounding
    "%d°%02d'%02d\"".format(
      y.floor.toInt,
      ((y - y.floor) * 60).floor.toInt,
      (((y*60) - (y*60).floor) * 60).floor.toInt)
  }
  def same( x: Double, y: Double) = {
    x.isNaN && y.isNaN || x == y
  }
  override def equals( that: Any) = that match {
    case other: Geo => 
      same( this.lat, other.lat) &&
      same( this.lon, other.lon) &&
      same( this.elv, other.elv)
    case _ => false
  }
  def toRawString = {
    lat.toString ++ " " ++ lon.toString ++ " " ++ elv.toString
  }

  override def toString = {
    toDMS( lat.abs) ++ (if( lat < 0) "S" else "N") ++ " " ++
    toDMS( lon.abs) ++ (if( lon < 0) "W" else "E") ++
    (if( elv.isNaN) "" else " " ++ elv.toInt.toString ++ "m")
  }

  def toLatLonString = {
    toDMS( lat.abs) ++ (if( lat < 0) "S" else "N") ++ " " ++
    toDMS( lon.abs) ++ (if( lon < 0) "W" else "E")
  }
}

case class Lang (
  id: Int,
  name: String,
  nameShort: String,
  nameAlt_ : IndexedSeq[String],
  nameComp: String,
  iso_ : IndexedSeq[String],
  family: Int,
  familyStr: String,
  country_ : IndexedSeq[ String],
  geo_ : IndexedSeq[ Geo],
  feat_ : IndexedSeq[ Int],
  area_ : IndexedSeq[ Int],
  note_ : IndexedSeq[ String],
  bib_ : IndexedSeq[ String]
)

object Saphon extends App {

  def readLanguages( filename: String) :
    (IndexedSeq[String], IndexedSeq[String], IndexedSeq[String], IndexedSeq[Lang]) = 
  {
    val javaRow_ = new CSVReader( new FileReader( filename)).readAll()
    val row_ = javaRow_.toIndexedSeq.map( 
      (row: Array[ java.lang.String]) => row.toIndexedSeq)

    // analyze column headers
    val head_ : IndexedSeq[String] = row_( 0)
    val meta_ : IndexedSeq[String] = row_( 1)
    val iName = head_.indexOf( "Name")
    val iNameShort = head_.indexOf( "Display form")
    val iNameAlt = head_.indexOf( "Alternate names")
    val iNameComp = head_.indexOf( "Computer name")
    val iISO = head_.indexOf( "ISO")
    val iCountry = head_.indexOf( "Country")
    val iFamily = head_.indexOf( "Family")
    val iGeo_ = meta_.zipWithIndex.filter( _._1 == "g").map( _._2)
    val iFeat_ = meta_.zipWithIndex.filter( _._1 == "f").map( _._2)
    val iArea_ = meta_.zipWithIndex.filter( _._1 == "a").map( _._2)
    val iBib_ = meta_.zipWithIndex.filter( _._1 == "b").map( _._2)
    val iNote_ = meta_.zipWithIndex.filter( _._1 == "n").map( _._2)

    val spaces = "\u0020|\u00a0|\u2002|\u2003|\u202f|\ufeff"

    // a function to fix language family
    def fixFamily( family: String, name: String) = {
      val io = "Isolate/Other"
      val corrections = HashMap(
        ("chapakuran", "Chapacuran"),
        ("aymara", "Aymaran"),
        ("aruan", "Arawan"),
        ("cahuapana", "Cahuapanan"),
        ("maku", "Nadahup"),
        ("choco", "Chocoan"),
        ("katukinan", "Katukinan"),
        ("arutani-sape", "Arutani-Sape"),
        ("isolate", io),
        ("unclassified", io),
        ("contact", io),
        ("mixed", io),
        ("", io)
      )
      // trim spaces, including non-breaking, en, and em
      val s1 = family.replaceAll( spaces, "")  
      val s2 = if( corrections.contains( s1.toLowerCase)) 
          corrections( s1.toLowerCase) 
        else s1
      val s3 = if( s2 == io)
          name.replaceAll( spaces, "")  
        else s2
      s3
    }

    val body_ = row_.tail.tail

    // analyze language families
    val family_ = body_.map( r => fixFamily( r( iFamily), r( iName)))
    val orderFamily = {
      var count = new HashMap[ String, Int]() { 
        override def default( key: String) = 0
      }
      for( family <- family_) count( family) += 1
      count.toSeq.sortBy( x => (-x._2, x._1)).map( _._1).toIndexedSeq
    }

    // create return values
    val feat_ = iFeat_.map( i => decompose( head_( i)))
    val area_ = iArea_.map( head_( _))

    val nan = "NaN".toDouble

    def strip( s: String) = s.replace( """^\s*""", "")
      .replace( """\s*$""", "")

    
    // check everything
    def extraSpace( s: String) =
      s.matches( """\s+.*""") || s.matches( """.*\s+""")

    def nbSpace( s: String) =
      s.matches( """.*[\u00a0\u2002\u2003\u202f\ufeff].*""")

    def plainABC( s: String) =
      s.matches( """[A-Za-z]+""")
      
    def goodISO( s: String) =
      s.matches( """[a-z_ ]+""")

    def goodGeo( s: String) =
      s == "" || {try{ s.toFloat; true } catch { case _ => false}}

    def numericGeo( s: String) =
      {try{ s.toFloat; true } catch { case _ => false}}

    def goodFeat( s: String) = {
      s == "" || {
        val a = try{ s.toFloat } catch {case _ => -1.}
        a == 1. || a == 0.
      }
    }
      
    val dejavu = Set.empty[String]
    for( i <- 0 until iFeat_.length) {
      if( dejavu contains feat_( i)) {
        println( "[ERR] HEADER ROW: duplicate feature: /%s/".format( feat_( i)))
      }
      dejavu += feat_( i)
    }

    for( i <- 0 until iArea_.length) {
      val s = area_( i)
      if( extraSpace( s)) println( "[ERR] HEADER ROW: extra space in area name: \"%s\"".format( s))
      if( nbSpace( s)) println( "[ERR] HEADER ROW: non-breaking space in area name: \"%s\"".format( s))
    }

    for( (row, i) <- body_.zipWithIndex) {
      val name = strip( row( iName))
      def check( probandum: String, fn: String => Boolean, err: String) {
        if( fn( probandum)) println( "[ERR] %s: %s: \"%s\"".format( name, err, probandum))
      }
      check( row( iName), extraSpace, "extra space in long display name")
      check( row( iName), nbSpace, "non-breaking space in long display name")
      check( row( iNameShort), extraSpace, "extra space in short display name")
      check( row( iNameShort), nbSpace, "non-breaking space in short display name")
      check( row( iNameAlt), extraSpace, "extra space in altenate names")
      check( row( iNameAlt), nbSpace, "non-breaking space in alternate names")
      check( row( iNameComp), s => !plainABC( s), "non-alphabetic character in computer name")
      check( row( iFamily), extraSpace, "extra space in family name")
      check( row( iFamily), nbSpace, "non-breaking space in family name")
      check( row( iCountry), extraSpace, "extra space in country")
      check( row( iCountry), nbSpace, "non-breaking space in country")
      check( row( iISO), s => !goodISO( s), "bad character in ISO")
      check( row( iISO), extraSpace, "extra space in ISO")
      for( iGeo <- iGeo_) {
        check( row( iGeo), s => !goodGeo( s), "bad character in geo coordinate")
        check( row( iGeo), extraSpace, "extra space in geo coordinate")
      }
      check( row( iGeo_( 1)), s => !numericGeo( s), "missing latitude")
      check( row( iGeo_( 2)), s => !numericGeo( s), "missing longitude")
      for( (iFeat, i) <- iFeat_.zipWithIndex) {
        check( row( iFeat), s => !goodFeat( s), "bad value for /%s/".format( feat_( i)))
      }
      for( (iArea, i) <- iArea_.zipWithIndex) {
        check( row( iArea), s => !goodFeat( s), "bad value for area \"%s\"".format( area_( i)))
      }
    }

    // return languages
    val lang_ = for( (row, i) <- body_.zipWithIndex) yield {
      Lang(
        i,
        strip( row( iName)),
        strip( row( iNameShort)),
        {
          val s = strip( row( iNameAlt))
          if( s == "") Array.empty[String]
          else s.split( """\s*[,;]\s*""")
        },
        strip( row( iNameComp)),
        row( iISO).split( """\s+"""),
        orderFamily.indexOf( fixFamily( row( iFamily), row( iName))),
        strip( row( iFamily)),
        {
          val s = strip( row( iCountry))
          if( s == "") Array.empty[String]
          else s.split( """\s*,\s*""")
        },
        iGeo_.map( row( _))
          .map( s => """(-?[0-9.]+)""".r.findFirstIn( s))
          .map( s => if( s.isEmpty) nan else s.get.toDouble)
          .grouped( 3).toIndexedSeq
          .filterNot( s_ => s_( 1).isNaN && s_( 2).isNaN)
          .map( g => Geo(g(1),g(2),g(0))),
        iFeat_.map( row( _))
          .map( (s: String) => if( s contains '1') 1 else 0),
        iArea_.map( row( _))
          .map( (s: String) => if( s contains '1') 1 else 0),
        iNote_.map( row( _))
          .map( (s: String) => strip( s)).filterNot( _ == ""),
        iBib_.map( row( _))
          .map( (s: String) => strip( s)).filterNot( _ == "")
      )
    }

    // check for close geographical coordinates 
    for( x <- lang_; y <- lang_) {
      if( x.id < y.id && distance( x.geo_(0), y.geo_(0)) < 1.) {
        println( "WARNING: primary locations for %s and %s are within 1 km."
          .format( x.name, y.name))
      }
    }

    (orderFamily, feat_, area_, lang_)
  }

  def writeCSV(
    path : String,
    family_ : Seq[ String],
    feat_ : Seq[ String],
    area_ : Seq[ String],
    lang_ : Seq[ Lang]): Unit =
  {
    def esc( s: String) = '"' +: s.replaceAll( "\"", "\"\"") :+ '"' 

    val fo = new FileWriter( path)

    val nGeo = lang_.map( _.geo_.length).max
    val nBib = lang_.map( _.bib_.length).max
    val nNote = lang_.map( _.note_.length).max

    val row1 = "Name, Display form, Alternate names, Computer name, ISO, Country, Family".split( ", ") ++
      (0 until nGeo).map( i => "z, y, x".split( ", ")).flatten ++
      feat_ ++ area_ ++
      (0 until nBib).map( i => "Bibliographic information") ++
      (0 until nNote).map( i => "Notes")

    fo.write( row1.map( esc( _)).mkString( ",") ++ "\n")
    fo.write( row1.map( esc( _)).mkString( ",") ++ "\n")

    val row3 = "o, o, o, o, o, o, o".split( ", ") ++
      (0 until nGeo).map( i => "g, g, g".split( ", ")).flatten ++
      feat_.map( s => "f") ++ 
      area_.map( s => "a") ++
      (0 until nBib).map( i => "b") ++
      (0 until nNote).map( i => "n")

    fo.write( row3.map( esc( _)).mkString( ",") ++ "\n")

    for( lang <- lang_) {
      val row = 
        List(
          esc( lang.name),
          esc( lang.nameShort),
          esc( lang.nameAlt_.mkString( "; ")),
          esc( lang.nameComp),
          esc( lang.iso_.mkString( " ")),
          esc( lang.country_.mkString( ", ")),
          esc( lang.familyStr)) ++
        lang.geo_.map( g => Seq( g.elv.toString, g.lat.toString, g.lon.toString))
          .padTo( nGeo, Seq( "", "", "")).flatten ++
        lang.feat_.map( _.toString) ++
        lang.area_.map( _.toString) ++
        lang.bib_.map( esc( _)).padTo( nBib, "") ++
        lang.note_.map( esc( _)).padTo( nNote, "")

      fo.write( row.mkString( ",") ++ "\n")
    }

    fo.close()
  }
    

  def writeFreqs( 
    fn : String,
    family_ : Seq[ String], 
    feat_ : Seq[ String], 
    lam : Double,
    mu_ : Seq[ Double],
    theta__ : Seq[ Seq[ Double]]): Unit = 
  {
    val fo = new CSVWriter( new FileWriter( fn))
    fo.writeNext( Array("") ++ feat_)  // headers
    fo.writeNext( Array("lam") ++ 
      Array.fill( feat_.length)( lam).map( "%.4f" format _))
    fo.writeNext( Array("mu") ++ 
      mu_.map( "%.4f" format _))
    for( k <- 0 until family_.length) {
      fo.writeNext( Array( family_( k)) ++
        theta__( k).map( "%.4f" format _))
    }
    fo.close();
  }

  def writeFreqsLambda( 
    fn : String,
    family_ : Seq[ String], 
    feat_ : Seq[ String], 
    lam_ : Seq[ Double],
    mu_ : Seq[ Double],
    theta__ : Seq[ Seq[ Double]]): Unit = 
  {
    val fo = new CSVWriter( new FileWriter( fn))
    fo.writeNext( Array("lam") ++ 
      mu_.map( "%.4f" format _))
    fo.writeNext( Array("") ++ feat_)  // headers
    fo.writeNext( Array("mu") ++ 
      mu_.map( "%.4f" format _))
    for( k <- 0 until family_.length) {
      fo.writeNext( Array( family_( k)) ++
        theta__( k).map( "%.4f" format _))
    }
    fo.close();
  }

  def readFreqs( fn : String) = 
  {
    val javaRow_ = new CSVReader( new FileReader( fn)).readAll()
    val row_ = javaRow_.toIndexedSeq.map( 
      (row: Array[ java.lang.String]) => row.toIndexedSeq)

    // throw away labels without checking
    val lam = row_(1)(1).toDouble
    val mu_ = row_(2).tail.map( _.toDouble)
    val theta__ = row_.tail.tail.tail.map( _.tail.map( _.toDouble))

    (lam, mu_, theta__)
  }

  def readFreqsLambda( fn : String) = 
  {
    val javaRow_ = new CSVReader( new FileReader( fn)).readAll()
    val row_ = javaRow_.toIndexedSeq.map( 
      (row: Array[ java.lang.String]) => row.toIndexedSeq)

    val lam_ = row_(0).tail.map( _.toDouble)
    // throw away labels without checking
    val mu_ = row_(2).tail.map( _.toDouble)
    val theta__ = row_.tail.tail.tail.map( _.tail.map( _.toDouble))

    (lam_, mu_, theta__)
  }

  def readPairScores( fn : String) = 
  {
    val javaRow_ = new CSVReader( new FileReader( fn)).readAll()
    val row_ = javaRow_.toIndexedSeq.map( 
      (row: Array[ java.lang.String]) => row.toIndexedSeq)
    row_.map( _.map( _.toDouble))
  }

  val (family_, feat_, area_, lang_) = readLanguages( args( 0))
  println( "%d languages" format lang_.length)
  println( "%d families" format family_.length)
  val c_ = {
    val c_ = Array.fill( family_.length)( 0)
    for( lang <- lang_) c_( lang.family) += 1
    c_.toIndexedSeq
  }
  for( (family, c) <- family_ zip c_)
    println( "  %d %s".format( c, family))
  println( "%d areas" format area_.length)
  for( iArea <- area_.indices) {
    println( "  %d %s".format( lang_.map( _.area_( iArea)).sum, area_( iArea)))
  }

  // look for duplicate ISOs
  val isoMap = HashMap.empty[ String, IndexedSeq[ Lang]]
  for( lang <- lang_; iso <- lang.iso_) {
    if( isoMap contains iso) {
      isoMap( iso) = isoMap( iso) :+ lang
    } else {
      isoMap( iso) = IndexedSeq( lang)
    }
  }
  for( iso <- isoMap.keys) {
    if( isoMap( iso).length > 1)
      println( "ISO %s shared by %s"
        .format( iso, isoMap( iso).map( _.name).mkString( "; ")))
  }

  writeCSV( "data/salangOut.csv", family_, feat_, area_, lang_)

  def distance( a: Geo, b: Geo) =
  {
    def lon( l: Geo) = l.lon / 180. * Pi
    def lat( l: Geo) = l.lat / 180. * Pi
    val ax = cos( lon( a)) * cos( lat( a))
    val ay = sin( lon( a)) * cos( lat( a))
    val az = sin( lat( a))
    val bx = cos( lon( b)) * cos( lat( b))
    val by = sin( lon( b)) * cos( lat( b))
    val bz = sin( lat( b))
    val dot = ax * bx + ay * by + az * bz
    val phi = if( dot >= 1.) 0. else acos( dot)
    phi * 6371
  }

  def distance( a: Lang, b: Lang) : Double = distance( a.geo_(0), b.geo_(0))

  def decompose( s: String) = {
    val t = Normalizer.normalize( s, Normalizer.Form.NFD)
    "\\p{InCombiningDiacriticalMarks}+".r
      .replaceAllIn( t, m => m.group(0).sorted)
  }
}
