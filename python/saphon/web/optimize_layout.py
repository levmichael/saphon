from collections import *

# These keys in these 5 dicts are the allowed values for place,
# manner, height, backness, and roundness in ipa-table.txt.  The
# values are possible arguments to the translation routine (xlt).

placeDict = OrderedDict([
  ('b', "bilabial"),
  ('l', "labio__dental"),
  ('d', "dental"),
  ('a', "alveolar"),
  ('A', "alveolar"),
  ('o', "post__alveolar"),
  ('r', "retroflex"),
  ('R', "retroflex"),
  ('p', "palatal"),
  ('P', "palatal"),
  ('v', "velar"),
  ('q', "labio__velar"),
  ('u', "uvular"),
  ('f', "pharyngeal"),
  ('g', "glottal"),
  ('x', "unspe__cified")])

mannerDict = OrderedDict([
  ('a', "aspirated@stop"),
  ('e', "ejective/creaky@stop"),
  ('s', "stop"),
  ('v', "voiced@stop"),
  ('p', "prenasalized@stop"),
  ('i', "implosive@stop"),
  ('A', "affricate"),
  ('f', "fricative"),
  ('n', "nasal"),
  ('x', "approximant"),
  ('r', "trill"),
  ('t', "tap_flap"),
  ('l', "lateral")])

heightDict = OrderedDict([
  ('7', "high"),
  ('6', "near_high"),
  ('5', "mid_high"),
  ('4', "mid"),
  ('3', "mid_low"),
  ('2', "near_low"),
  ('1', "low")])

backDict = OrderedDict([
  ('f', "front"),
  ('c', "central"),
  ('b', "back")])

roundDict = OrderedDict([
  ('u', "unrounded"),
  ('r', "rounded")])



# Quantifiers.
def indic(x): return not not x
def count(seq, pred): return sum(pred(x) for x in seq)

def NONE(seq, pred=indic): l = list(seq); return count(l, pred) == 0
def ANY (seq, pred=indic): l = list(seq); return count(l, pred) >= 1
def MANY(seq, pred=indic): l = list(seq); return count(l, pred) >= 2
def SOME(seq, pred=indic): l = list(seq); return 0 < count(l, pred) < len(l) 
def ALL (seq, pred=indic): l = list(seq); return count(l, pred) == len(l)

# Move items that satisfy pred(icate) from list2 to list1.
def move(list1, list2, pred=indic):
  list1 += filter(pred, list2)
  list2[:] = filter(lambda x: not pred(x), list2)



# Takes a consonant layout (consonants) and modifies it; also
# returns row labels (mannerLabels) and column labels (placeLabels).

# The consonant layout is a dict whose keys are pairs of chars,
# denoting manner and place, and whose values are lists of phonemes.

def layoutConsonants(featInfo, consonants, lump):

  c = consonants # for convenience

  #####################################
  # Attempt adjustments to the layout #
  #####################################

  # Split stops into voiced and unvoiced if it's the only row with
  # voice opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, featInfo.isVoiced)) == {'s'}:
    for j in placeDict:
      move(c['v',j], c['s',j], featInfo.isVoiced)

  # Initially, stops and affricates both have 'stop' place of
  # articulation.  Here I create a new row for affricates if the
  # stop row is the only one with stop/affricate opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, featInfo.isAffricate)) == {'s'}:
    for j in placeDict:
      move(c['A',j], c['s',j], featInfo.isAffricate)

  # Move palatalized sounds to palatal column if no collisions result.
  # Each element in pal is a location (i,j) that contains palatal sounds.
  pal = set((i,j) for i,j in c if j=='p' or SOME(c[i,j], featInfo.isPalatalized))

  # Not sure why I need to repackage c.items() with list(...), but I do.
  if ALL(j=='p' or not c[i,'p'] or not ANY(ss, featInfo.isPalatalized) for (i,j), ss in list(c.items())):
    for j in placeDict:
      for i in mannerDict:
        move(c[i,'p'], c[i,j], featInfo.isPalatalized)

  # Move labialized sounds to labiovelar column if among labialized
  # sounds, there is no more than one place of articulation for each
  # manner of articulation.

  if ALL(not MANY(filter(featInfo.isLabialized, c[i,j]) for j in mannerDict) for i in placeDict):
    for i in placeDict:
      for j in mannerDict:
        move(c[i,'q'], c[i,j], featInfo.isLabialized)

  # Move w to velar if labiovelar column otherwise empty.

  if ALL(i=='x' or not c[i,'q'] for i in mannerDict):
    move(c['x','v'], c['x','q'])

  ########
  # Lump #
  ########

  if lump:
    for i in mannerDict:
      move(c[i,'b'], c[i,'l'])
      move(c[i,'v'], c[i,'q'])
      move(c[i,'u'], c[i,'f'])
      move(c[i,'u'], c[i,'g'])
      move(c[i,'u'], c[i,'x'])
    for j in placeDict:
      move(c['x',j], c['r',j])
      move(c['x',j], c['t',j])
      move(c['e',j], c['i',j])

  ######################################
  # Create labels for rows and columns #
  ######################################

  # In mannerLabels, each key-value pair denotes the
  # symbol and the label for each non-empty row.

  mannerLabels = OrderedDict([(i, mannerDict[i]) for
    i in mannerDict if any(c[i,j] for j in placeDict)])

  # Modify mannerLabels if necessary.

  # Use a more specific label for ejective/creaky if possible.
  eSounds = [s for j in placeDict for s in c['e',j]]
  if NONE(eSounds, featInfo.isEjective):
    mannerLabels['e'] = 'creaky@stop'
  if ALL(eSounds, featInfo.isEjective):
    mannerLabels['e'] = 'ejective@stop'

  # Are there non-plain stops?
  if ANY(c[i,j] for j in placeDict for i in 'aevp'):
    # Are plain and voiced stops mixed together?
    if ANY(featInfo.isVoiced(sound) for j in placeDict for sound in c['s',j]):
      mannerLabels['s'] = 'plain/voiced@stop'
    else:
      mannerLabels['s'] = 'plain@stop'

  # Lump rows?
  if lump:
    mannerLabels['x'] = 'attf'
    mannerLabels['e'] = 'glottalized@stop'

  # Are there affricates mixed in with stops?
  for i in "aesvp":
    if ANY(ANY(c[i,j], featInfo.isAffricate) for j in placeDict):
      mannerLabels[i] += '/affricate'

  # In placeLabels, each key-value pair denotes the
  # symbol and the label for each non-empty column.

  placeLabels = OrderedDict([(j, placeDict[j]) for j in placeDict if any(c[i,j] for i in mannerDict)])

  # Lump columns?
  if lump:
    placeLabels['u'] = 'pvus'
    placeLabels['b'] = 'labial'

  return mannerLabels, placeLabels



# Takes a vowel layout (vowels) and modifies it; also returns row labels
# (heightLabels), and column labels (backnessLabels).

# The vowel layout is a dict whose keys are pairs of chars, denoting
# height and backness, and whose values are lists of IPA symbols.

def layoutVowels(featInfo, vowels, lump):

  v = vowels # for convenience

  #####################################
  # Attempt adjustments to the layout #
  #####################################

  # Collapse mid-high, mid, mid-low if there is no opposition
  # at any backness.

  if NONE(MANY(v[i,j] for i in '345') for j in backDict):
    for j in backDict:
      move(v['4',j], v['3',j])
      move(v['4',j], v['5',j])

  # Nudge ash to 1f if 1f is empty.

  if not v['1','f'] and v['2','f']:
    move(v['1','f'], v['2','f'])

  # Nudge typescript-a to 1f if 1f is empty and 1b is not.

  if not v['1','f'] and v['1','c'] and v['1','b']:
    move(v['1','f'], v['1','c'])

  # Move near-low to low if there is no opposition at any
  # backness.

  if NONE(v['1',j] and v['2',j] for j in backDict):
    for j in backDict:
      move(v['1',j], v['2',j])

  # Move near-high to high if there is no opposition at any
  # backness.

  if NONE(v['7',j] and v['6',j] for j in backDict):
    for j in backDict:
      move(v['7',j], v['6',j])

  ########
  # Lump #
  ########

  if lump:
    for j in backDict:
      move(v['7',j], v['6',j])
      move(v['1',j], v['2',j])
      move(v['4',j], v['5',j])
      move(v['4',j], v['3',j])

  ################################################
  # Create labels for non-empty rows and columns #
  ################################################
  
  # In heightLabels, each key-value pair denotes the 
  # symbol and the label for each non-empty row.

  heightLabels = OrderedDict([(i, heightDict[i]) for
    i in heightDict if any(v[i,j] for j in backDict)])

  # In backnessLabels, each key-value pair denotes the 
  # symbol and the label for each non-empty column.

  backnessLabels = OrderedDict([(j, backDict[j]) for
    j in backDict if any(v[i,j] for i in backDict)])

  return heightLabels, backnessLabels
