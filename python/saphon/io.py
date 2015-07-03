import csv, math, re, sys, os

class Geo:
  def __init__(self, lat, lon, elv):
    self.lat = lat
    self.lon = lon
    self.elv = elv

class Lang:
  def __init__(self, name, nameShort, nameAlt_, nameComp, iso_,
      family, familyStr, country_, geo_, feat_, note_, bib_):
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
    self.note_ = note_
    self.bib_ = bib_

nan = float('nan')
def readFloat(s):
  try:
    x = float(s)
  except:
    x = nan
  return x

def parseGeoFields(geo_):
  x_ = [readFloat(g) for g in geo_]
  y_ = [Geo(x_[i+1], x_[i+2], x_[i+0]) for i in range(0, len(geo_), 3) 
    if not (math.isnan(x_[i+1]) or math.isnan(x_[i+2]))]
  return y_

def familyName(family, lang):
  return lang if family == 'Isolate' else family

def readSaphonTable(filename):
  row_ = [row for row in csv.reader(open(filename, 'rb'))]

  head_ = row_[0]
  meta_ = row_[1]
  iName = head_.index('Name')
  iNameShort = head_.index('Display form')
  iNameAlt = head_.index('Alternate names')
  iNameComp = head_.index('Computer name')
  iISO = head_.index('ISO')
  iCountry = head_.index('Country')
  iFamily = head_.index('Family')
  iGeo_ = [i for i,m in enumerate( meta_) if m == 'g']
  iFeat_ = [i for i,m in enumerate( meta_) if m == 'f']
  iBib_ = [i for i,m in enumerate( meta_) if m == 'b']
  iNote_ = [i for i,m in enumerate( meta_) if m == 'n']

  body_ = row_[2:]

  # analyze language families
  family_ = [familyName(r[ iFamily], r[ iName]) for r in row_]
  familyOrdered_ = sorted(set( family_), 
    key = lambda x: (family_.count(x), x))  # O(n^2), i don't care

  # create return values
  feat_ = [head_[ i] for i in iFeat_]

  lang_ = []
  for i, r in enumerate(body_):
    r = [f.strip() for f in r] # strip all cells in row
    lang_.append(
      Lang(
        r[iName],
        r[iNameShort],
        re.split(r"\s*[,;]\s*", r[iNameAlt]) if r[iNameAlt] != '' else [],
        r[iNameComp],
        re.split(r"\s+", r[iISO]) if r[iISO] != '' else [],
        familyOrdered_.index(familyName(r[iFamily], r[iName])),
        r[iFamily],
        re.split(r"\s*[,]\s*", r[iCountry]) if r[iCountry] != '' else [],
        parseGeoFields([r[i] for i in iGeo_]),
        [head_[i] for i in iFeat_ if r[i] == '1'],
        [r[i].replace('\n', ' ') for i in iNote_ if r[i] != ''],
        [r[i].replace('\n', ' ') for i in iBib_ if r[i] != ''],
      ))

  return familyOrdered_, feat_, lang_

def writeSaphonFiles(dir, lang_, feat_):
  if not os.path.exists(dir):
    os.makedirs(dir)
  for lang in lang_:
    fo = open(dir+'/'+lang.nameComp+'.txt', 'w')
    fo.write('name: ' + lang.name + '\n')
    fo.write('name.short: ' + lang.nameShort + '\n')
    for nameAlt in lang.nameAlt_:
      fo.write('name.alt: ' + nameAlt + '\n')
    fo.write('name.comp: ' + lang.nameComp + '\n')
    for iso in lang.iso_:
      fo.write('code: ' + iso + '\n')
    fo.write('family: ' + lang.familyStr + '\n')
    for country in lang.country_:
      fo.write('country: ' + country + '\n')
    for geo in lang.geo_:
      fo.write('geo: %.3f %.3f %.0f\n' % (geo.lat,geo.lon,geo.elv))

    fo.write('feat: ' + ' '.join(lang.feat_) + '\n')

    for note in lang.note_:
      fo.write('note: ' + note + '\n')
    for bib in lang.bib_:
      fo.write('bib: ' + bib + '\n')

def readSaphonFiles(dir_name):
    lang_ = []
    for file in os.listdir(dir_name):
        file_name = os.path.join(dir_name, file)
        with open(file_name, "r") as f:
            f_lines = f.readlines()
            NameAlt = []
            Code = []
            Country = []
            Geography = []
            Note = []
            Bib = []
            for line in f_lines:
                if "name:" in line:
                    Name = line[6:-1]
                elif "name.short:" in line:
                    NameShort = line[12:-1]
                elif "name.alt:" in line:
                    name_alt = line[10:-1]
                    NameAlt.append(name_alt)
                elif "name.comp:" in line:
                    NameComp = line[11:-1]
                elif "code:" in line:
                    code = line[6:-1]
                    Code.append(code)
                elif "family:" in line:
                    Family = line[8:-1] 
                elif "country:" in line:
                    country = line[9:-1]
                    Country.append(country)
                elif "geo:" in line:
                    geo = line[5:-1]
                    geo = [readFloat(x) for x in geo.split()]
                    if len(geo) == 2:
                      Geography.append(Geo(geo[0], geo[1], nan))
                    else:
                      Geography.append(Geo(geo[0], geo[1], geo[2]))
                elif "feat:" in line:
                    Feat = line[6:-1]
                    Feat = Feat.split()
                elif "note:" in line:
                    note = line[6:-1]
                    Note.append(note)
                elif "bib:" in line:
                    bib = line[5:-1]
                    Bib.append(bib)
                else:
                    print "Error in %s" % file_name
                f.close()
            lang_.append(Lang(Name, NameShort, NameAlt, NameComp, Code, familyName(Family, Name), Family, Country, Geography, Feat, Note, Bib))
    
    family_ = [lang.family for lang in lang_]
    familyOrdered_ = sorted(set( family_),
        key = lambda x: (family_.count(x), x))
    feat_ = []
    for lang in lang_:
        for item in lang.feat_:
            feat_.append(item)
    feat_ = sorted(set( feat_))
    
    return familyOrdered_, feat_, lang_

if __name__ == '__main__':
  family_, feat_, lang_ = readSaphonTable(sys.argv[1])

  print "%d languages" % len(lang_)
  print "%d families" % len(family_)
  print "%d features" % len(feat_)

  writeSaphonFiles(sys.argv[2], lang_, feat_)

  # test Emily's code
  family2_, feat2_, lang2_ = readSaphonFiles(sys.argv[2])
  writeSaphonFiles('bar', lang2_, feat2_)

