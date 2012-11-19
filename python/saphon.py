import csv, math, re, sys

class Geo:
  def __init__( self, lat, lon, elv):
    self.lat = lat
    self.lon = lon
    self.elv = elv

class Lang:
  def __init__( self, id, name, nameShort, nameAlt_, nameComp, iso_,
      family, familyStr, country_, geo_, feat_, area_, note_, bib_):
    self.id = id
    self.name = name
    self.nameShort = nameShort
    self.nameAlt_ = nameAlt_
    self.nameComp = nameComp
    self.iso_ = iso_
    self.family = family
    self.familyStr = familyStr
    self.country_ = country_
    self.geo_ = geo_
    self.feat_ = feat_
    self.area_ = area_
    self.note_ = note_
    self.bib_ = bib_

def readSaphon( filename):
  row_ = [row for row in csv.reader( open( filename, 'rb'))]

  head_ = row_[0]
  meta_ = row_[1]
  iName = head_.index( 'Name')
  iNameShort = head_.index( 'Display form')
  iNameAlt = head_.index( 'Alternate names')
  iNameComp = head_.index( 'Computer name')
  iISO = head_.index( "ISO")
  iCountry = head_.index( "Country")
  iFamily = head_.index( "Family")
  iGeo_ = [i for i,m in enumerate( meta_) if m == 'g']
  iFeat_ = [i for i,m in enumerate( meta_) if m == 'f']
  iArea_ = [i for i,m in enumerate( meta_) if m == 'a']
  iBib_ = [i for i,m in enumerate( meta_) if m == 'b']
  iNote_ = [i for i,m in enumerate( meta_) if m == 'n']

  body_ = row_[2:]

  def familyName( family, lang):
    return lang if family == 'Isolate' else family

  # analyze language families
  family_ = [familyName( r[ iFamily], r[ iName]) for r in row_]
  familyOrdered_ = sorted( set( family_), 
    key = lambda x: (family_.count( x), x))  # O(n^2), i don't care

  # create return values
  feat_ = [head_[ i] for i in iFeat_]
  area_ = [head_[ i] for i in iArea_]

  nan = float( 'nan')
  def readFloat( s):
    try:
      x = float( s)
    except:
      x = nan
    return x

  def parseGeoFields( geo_):
    x_ = [readFloat( g) for g in geo_]
    y_ = [Geo(x_[i+1], x_[i+2], x_[i+0]) for i in range( 0, len(geo_), 3) 
      if not (math.isnan( x_[i+1]) or math.isnan( x_[i+2]))]
    return y_

  lang_ = []
  for i, r in enumerate( body_):
    lang_.append(
      Lang(
        i,
        r[ iName],
        r[ iNameShort],
        re.split( r"\s*[,;]\s*", r[ iNameAlt]),
        r[ iNameComp],
        re.split( r"\s+", r[ iISO]),
        familyOrdered_.index( familyName( r[iFamily], r[iName])),
        r[ iFamily],
        re.split( r"\s*[,]\s*", r[ iCountry]),
        parseGeoFields( [r[i] for i in iGeo_]),
        [1 if '1' in r[i] else 0 for i in iFeat_],
        [1 if '1' in r[i] else 0 for i in iArea_],
        [r[i] for i in iNote_ if r[i].strip() != ''],
        [r[i] for i in iBib_ if r[i].strip() != ''],
      ))

  return familyOrdered_, feat_, area_, lang_

if __name__ == '__main__':
  family_, feat_, area_, lang_ = readSaphon( sys.argv[1])

  print "%d languages" % len( lang_)
  print "%d families" % len( family_)
  print "%d features" % len( feat_)
  print "%d areas" % len( area_)

