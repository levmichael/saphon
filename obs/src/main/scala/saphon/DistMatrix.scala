package saphon

import au.com.bytecode.opencsv._

import java.io.FileReader
import java.io.FileWriter
import java.text.Normalizer

import collection.JavaConversions._
import collection.mutable.HashMap
import collection.mutable.Set
import math._

object DistMatrix extends App {

  if( args.length < 2) {
     println( "Two filepaths required.")
     System.exit( 1)
  }

  val (family_, feat_, area_, lang_) = Saphon.readLanguages( args(0))

  def minDistance( a: Lang, b: Lang) : Double = {
    (for( g <- a.geo_; h <- b.geo_) yield {
      Saphon.distance( g, h)
    }).min
  }

  val fo = new FileWriter( args(1))
  
  for( a <- lang_) {
    val dist_ = for( b <- lang_) yield {
      minDistance( a, b)
    }
    fo.write( dist_.map( "%.3f".format( _)).mkString( ", ") ++ "\n")
  }
}


