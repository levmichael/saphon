
read.saphon <- function( fn) {
  a <- read.csv( fn, check.names=F, stringsAsFactors=F)

  N <- dim(a)[1]
  head <- colnames( a)
  meta <- a[1,]

  name.lang <- as.character( a[,head=='Name'])[2:N]
  iso <- as.character( a[,head=='ISO'])[2:N]
  family <- as.character( a[,head=='Family'])[2:N]

  jj.area <- which( meta=='a')
  area <- as.matrix(a[2:N,jj.area])
  area <- ifelse( !is.na(area) & area == "1", 1, 0)
  n.area = dim(area)[2]
  name.area <- colnames(area)
  name.area <- gsub( '[ /]', '-', name.area)
  name.area <- gsub( '\\.', '', name.area)
  colnames( area) <- name.area
  area <- data.frame(area)

  jj.feat <- which( meta=='f')
  feat <- as.matrix(a[2:N,jj.feat])
  feat <- ifelse( !is.na(feat) & feat == "1", 1, 0)
  n.feat = dim(feat)[2]
  name.feat <- colnames(feat)
  colnames(feat) <- make.names(name.feat)
  feat <- data.frame(feat)

  jj.geo <- which( meta=='g')[1:3]
  geo <- as.matrix(a[2:N,jj.geo])
  colnames( geo) <- c('z', 'y', 'x')
  n.geo = dim(geo)[2]
  geo <- data.frame(geo)

  geo <- data.frame( x = as.numeric(as.character( geo$x)),
                     y = as.numeric(as.character( geo$y)),
                     z = as.numeric(as.character( gsub( '[A-Za-z]+', '', geo$z))))

  n.lang <- length( name.lang)

  list( 
    N=n.lang,
    name.lang=name.lang, 
    iso=iso,
    family=family,
    name.area=name.area, 
    area=area,
    name.feat=name.feat, 
    feat=feat,
    geo=geo
  )
}

# utility functions

inventory <- function( l, n) {
  paste( l$name.feat[which(l$feat[n,]==1)], collapse=' ')
}

feature.freqs <- function( k) {
  ii <- which( l$affiliation == k)
  colSums( l$feat[ii,]) / length( ii)
}

aff.by.fabb <- function( s) {
  unique( l$affiliation[ l$fabb == s])
}

lookup <- function( s) {
  l$name.lang[ grep( s, l$iso)]
}

# distance

dist <- function( geo, a, b) {
  lon <- function( i) { geo$x[i] / 180. * pi}
  lat <- function( i) { geo$y[i] / 180. * pi}
  ax <- cos( lon( a)) * cos( lat( a))
  ay <- sin( lon( a)) * cos( lat( a))
  az <- sin( lat( a))
  bx <- cos( lon( b)) * cos( lat( b))
  by <- sin( lon( b)) * cos( lat( b))
  bz <- sin( lat( b))
  dot <- ax * bx + ay * by + az * bz
  phi <- acos( ifelse( dot > 1., 1., dot))
  phi * 6371
}

# family abbreviations

list.fabb = list(
  'Tupí' = 'T',
  'Arawak' = 'A',
  'Carib' = 'C',
  'Macro-Ge' = 'Ge',
  'Quechua' = 'Q',
  'Panoan' = 'P',
  'Tucanoan' = 'Tu',
  'Arawan' = 'An',
  'Chibchan' = 'Cb',
  'Guaicuru' = 'G',
  'Mataco' = 'Mt',
  'Jivaroan' = 'J',
  'Witotoan' = 'W',
  'Barbacoan' = 'B',
  'Chapakuran' = 'Cp',
  'Choco' = 'Cc',
  'Guahiban' = 'Gh',
  'Nadahup' = 'N',
  'Nambiquaran' = 'Nm',
  'Tacanan' = 'Tn',
  'Yanomam' = 'Y',
  'Zaparoan' = 'Z'
)

fabb <- function( s) {
  t <- list.fabb[[s]]
  if( is.null(t)) return( '')
  return( t)
}
