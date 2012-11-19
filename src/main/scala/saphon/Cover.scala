package saphon
import collection.mutable.Map
import collection.immutable.Set
import collection.mutable.{Set => MutSet}

object Cover extends App {

  if( args.length < 2) {
     println( "Two filepaths required.")
     System.exit( 1)
  }

  val (family_, feat_, area_, lang_) = Saphon.readLanguages( args(0))

  val vowelMap = Seq( 
    ("ʉ", "ɨ"),
    ("ɯ", "ɨ"),
    ("ə", "ɨ"),
    ("ʌ", "ɨ"),

    ("ʊ", "u"),
    ("o", "u"),
    ("ɔ", "o"),
    ("ɤ", "o"),

    ("ɪ", "i"),
    ("e", "i"),
    ("ɛ", "e"))

  val consonantMap = Seq(
    ("ɑ", "a"),
    ("lʲ", "ʎ"),
    ("ʝ", "ʒ"),
    ("ʋ", "β"))

  val vowelStr = "iʏɪeɛæaɑɔoʊuɨəɘɜɐʉɵœøyʌɤɯ"
  val vowelRE = "[" ++ vowelStr ++ "]"
  val vowels = Set( vowelStr:_*)
  def isIPA( sound:String) = 
    sound != "tone" && sound != "nasal harmony" && sound != "creakspr"
  def isVowel( sound:String) = {
    isIPA( sound) && !sound.forall( s => !(vowels contains s))
  }
  def isOralVowel( sound:String) =
    isVowel( sound) && !(sound contains "\u0303")
    
  def regularize( invIn: Set[ String], debug: Boolean = false): Set[ String] = {
    val inv = MutSet( invIn.toSeq:_*)

    // regularize vowels
    for( (o, n) <- vowelMap) {
      if( debug) println( o, n)
      val inv0 = Set( inv.toSeq:_*)
      for( f: String <- inv.toSeq if isIPA( f)) {
        if( f contains o) {
          // n not already in inventory
          if( inv0.filter( isIPA( _)).forall( s => !(s contains n)))
          {
            val newF = o.r.replaceAllIn( f, n)
            if( debug) println( "**", f, newF)
            if( !(inv contains newF)) {
              inv -= f
              inv += o.r.replaceAllIn( f, n)
            }
          }
        }
      }
    }

    // replicate oral vowels as nasal vowels if nasspr
    if( inv contains "nasspr") {
      for( f <- inv.toSeq if isOralVowel( f)) {
        inv += vowelRE.r.replaceAllIn( f, m => (m.group( 0) ++ "\u0303"))
      }
    }

    // regularize consonants
    for( (o, n) <- consonantMap) {
      if( inv contains o) {
        inv -= o
        inv += n
      }
    }

    Set( inv.toSeq:_*)
  }

  val inv_ = for( lang <- lang_) yield {
    val inv = Set( 
      (for( (v, f) <- lang.feat_ zip feat_ if v == 1) yield f):_*)
    regularize( inv)
  }

  val allSounds = MutSet.empty[String]
  for( inv <- inv_) {
    allSounds ++= inv
  }

  println( allSounds.mkString( " :: "))

  // order features
  val oldL = feat_.length
  val featMap = Map( feat_.zipWithIndex:_*)
  // always keep nasal harmony, and put at end
  val nooFeat_ = 
    ((allSounds - "nasal harmony").toIndexedSeq
      .sortBy( (f:String) => (featMap.getOrElse( f, oldL), f))) :+ "nasal harmony"

  // generate report
  println( "Sounds: [old %d] [new %d]".format( oldL, nooFeat_.length))
  val oldSet = Set( feat_ :_*)
  val nooSet = Set( nooFeat_ :_*)
  println( "Offed: " ++ (for( f <- feat_ if !(nooSet contains f)) yield f).mkString(" "))
  println( "Added: " ++ (for( f <- nooFeat_ if !(oldSet contains f)) yield f).mkString(" "))

  // write CSV
  val N = lang_.length
  val nooLang_ = for( i <- 0 until N) yield {
    val inv = inv_( i)
    lang_( i).copy( feat_ = nooFeat_.map( f => if( inv contains f) 1 else 0))
  }
  Saphon.writeCSV( args(1), family_, nooFeat_, area_, nooLang_)
}

