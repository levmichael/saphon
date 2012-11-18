name := "saphon"

version := "1.0"

organization := "edu.berkeley.linguistics"

scalaVersion := "2.9.1"

resolvers += "Local Maven Repository" at "file://"+Path.userHome.absolutePath+"/.ivy2/local"

libraryDependencies += "net.sf.opencsv" % "opencsv" % "2.0"

libraryDependencies += "org.scalanlp" %% "scalanlp-data" % "0.5-SNAPSHOT"

libraryDependencies += "org.scalanlp" %% "scalanlp-learn" % "0.5-SNAPSHOT"