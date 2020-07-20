import csv, math, re, sys, os, unicodedata
import glob
import yaml
from collections import *

class SaphonData:
  def __init__(self, familyOrdered_, featInfo, lang_):
    self.familyOrdered_ = familyOrdered_
    self.featInfo = featInfo
    self.lang_ = lang_

class FeatInfo:
  def __init__(self, featAttr):
    self.featAttr = featAttr

  def feats(self):
    return list(self.featAttr.keys())

  def order(self):
    return {sound: i for i, sound in enumerate(self.featAttr.keys())}

  def isSuprasegmental(self, sound): return self.featAttr[sound][0] == 's'
  def isConsonant     (self, sound): return self.featAttr[sound][0] == 'c'
  def isVowel         (self, sound): return self.featAttr[sound][0] == 'v'
  def isVoiced        (self, sound): return self.featAttr[sound][3] == 'v'
  def isLabialized    (self, sound): return 'ʷ' in sound
  def isPalatalized   (self, sound): return 'ʲ' in sound
  def isPalatal       (self, sound): return self.featAttr[sound][2] == 'p'
  def isPalataloid    (self, sound): return self.isPalatalized(sound) or self.isPalatal(sound)
  def isEjective      (self, sound): return '\'' in sound
  def isAffricate     (self, sound): return self.featAttr[sound][4:5] == 'a'

class Geo:
  def __init__(self, lat, lon, elv):
    self.lat = lat
    self.lon = lon
    self.elv = elv

  def toDMS(deg):
    sec = int(3600.0 * deg + 0.5)
    return '%d°%02d\'%02d"' % (sec / 3600, (sec / 60) % 60, sec % 60)
    
  def toLatLonString(self):
    return Geo.toDMS(abs(self.lat)) + 'NS'[self.lat < 0] +\
     ' ' + Geo.toDMS(abs(self.lon)) + 'EW'[self.lon < 0]


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

class YAMLLang(object):
    '''A class for reading new-style YAML saphon lang files and interfacing
with existing code based on .txt files.'''
    def __init__(self, yamlfile):
        '''Instantiate object from .yaml file.'''
        self.synthesis = None
        self.refs = []
        with open(yamlfile, 'r') as fh:
            docs = list(yaml.safe_load_all(fh))
        for doc in docs:
            try:
                assert(doc['doctype'] in ('synthesis', 'ref'))
            except AssertionError:
                raise RuntimeError(f"Unrecognized doctype \'{doc['doctype']}\'")
            except KeyError:
                raise RuntimeError('Found a document with no `doctype`.')
            if doc['doctype'] == 'synthesis':
                try:
                    assert(self.synthesis is None)
                except AssertionError:
                    raise AssertionError('Multiple synthesis documents found')
                self.synthesis = doc
            elif doc['doctype'] == 'ref':
                self.refs.append(doc)

        # Filter None values out of list values.
        listflds = (
            'alternate_names', 'iso_codes', 'countries', 'coordinates',
            'phonemes', 'allophones', 'notes'
        )
        for fld in listflds:
            self.synthesis[fld] = [v for v in self.synthesis[fld] if v is not None]
        for ref in self.refs:
            for fld in ('graphemes2phonemes', 'ref_allophones', 'ref_notes'):
                try:
                    ref[fld] = [v for v in ref[fld] if v is not None]
                except:
                    print(ref)
                    raise

 
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

# TODO: This needs to be more comprehensive.
def normalizeIPA(s):
  return unicodedata.normalize('NFD', s)

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

  return SaphonData(familyOrdered_, feat_, lang_)

# Read in features (including phonemes) and properties.
# TODO: Error checking on feat info.
def readFeatList(filename):
  featAttr = OrderedDict()
  for line in open(filename):
    if ':' not in line: continue
    position, sounds = re.split(': *', line.strip(), 1)
    for sound in re.split(' +', sounds):
      featAttr[normalizeIPA(sound)] = position
  return FeatInfo(featAttr)

# TODO: generate file for feat info
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


def readSaphonYAMLFiles(yamldir, ipatable):
    '''Read all saphon .yaml datafiles.'''
    featInfo = readFeatList(ipatable)
    featOrder = featInfo.order()

    lang_ = []
    for fname in glob.glob(f'{yamldir}/*.yaml'):
        ylang = YAMLLang(fname)
        synth = ylang.synthesis
        refs = ylang.refs
        phonemes = [
            normalizeIPA(p) for p in synth['phonemes']
        ]
        phonemes.sort(key = lambda p: featOrder[p])
        for fld in ('nasal_harmony', 'tone', 'laryngeal_harmony'):
            if synth[fld] is True:
                phonemes.append(fld)
        geography = [
            Geo(c['latitude'], c['longitude'], c['elevation_meters']) \
                for c in synth['coordinates']
        ]
        lang_.append(
            Lang(
                name=synth['name'],
                nameShort=synth['short_name'],
                nameAlt_=synth['alternate_names'],
                nameComp=os.path.splitext(os.path.basename(fname))[0],
                iso_=synth['iso_codes'],
                family=familyName(synth['family'], synth['name']),
                familyStr=synth['family'],
                country_=synth['countries'],
                geo_=geography,
                feat_=phonemes,
                note_=synth['notes'],
                bib_=[ref['citation'] for ref in refs]
            )
        )
    family_ = [lang.family for lang in lang_]
    familyOrdered_ = sorted(set(family_), key = lambda x: (family_.count(x), x))

    return SaphonData(familyOrdered_, featInfo, lang_)


def readSaphonFiles(dir_name):
    featInfo = readFeatList(dir_name+'/ipa-table.txt')
    featOrder = featInfo.order()

    lang_ = []
    for file in os.listdir(dir_name):
        if file[-4:] != '.txt': continue
        if file == 'ipa-table.txt': continue
        file_name = os.path.join(dir_name, file)
        with open(file_name, "r") as f:
            f_lines = f.readlines()
            NameAlt = []
            Code = []
            Country = []
            Geography = []
            Feat = []
            Note = []
            Bib = []
            for line_raw in f_lines:
                line = line_raw.strip()
                if line == '': continue
                try:
                  key, value = re.split(r':\s*', line.strip(), 1)
                except BaseException as e:
                  print('*** Error parsing %s on line:' % file_name)
                  print(line)
                  raise e

                if key == "name": Name = value
                elif key == "name.short": NameShort = value
                elif key == "name.alt": NameAlt.append(value)
                elif key == "name.comp": NameComp = value
                elif key == "code": Code.append(value)
                elif key == "family": Family = value
                elif key == "country": Country.append(value)
                elif key == "geo":
                    geo = [readFloat(x) for x in value.split()]
                    if len(geo) == 2:
                      Geography.append(Geo(geo[0], geo[1], nan))
                    else:
                      Geography.append(Geo(geo[0], geo[1], geo[2]))
                elif key == "feat": Feat += [normalizeIPA(s) for s in value.split()]
                elif key == "note": Note.append(value)
                elif key == "bib": Bib.append(value)
                else:
                    print('Bad line %s in %s' % (line, file_name))

            # Reorder features by the order given in ipa-table.txt.
            try:
              Feat.sort(key = lambda sound: featOrder[sound])
            except BaseException as e:
              print('*** Error parsing %s, raising exception:' % file_name)
              print(e)
              raise e

            lang_.append(Lang(Name, NameShort, NameAlt, NameComp, Code, familyName(Family, Name), Family, Country, Geography, Feat, Note, Bib))
    
    family_ = [lang.family for lang in lang_]
    familyOrdered_ = sorted(set( family_),
        key = lambda x: (family_.count(x), x))

    # Check features against featInfo
    # feat_ = []
    # for lang in lang_:
    #     for item in lang.feat_:
    #         feat_.append(item)
    # feat_ = sorted(set( feat_))
    
    return SaphonData(familyOrdered_, featInfo, lang_)

if __name__ == '__main__':
  family_, feat_, lang_ = readSaphonTable(sys.argv[1])

  print('%d languages' % len(lang_))
  print('%d families' % len(family_))
  print('%d features' % len(feat_))

  writeSaphonFiles(sys.argv[2], lang_, feat_)

  # test Emily's code
  family2_, feat2_, lang2_ = readSaphonFiles(sys.argv[2])
  writeSaphonFiles('bar', lang2_, feat2_)

