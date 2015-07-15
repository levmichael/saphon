from collections import *

places = orderedDict([
  ('b', "bilabial"),
  ('l', "labio=dental"),
  ('d', "dental"),
  ('a', "alveolar"),
  ('A', "alveolar"),
  ('o', "post=alveolar"),
  ('r', "retroflex"),
  ('R', "retroflex"),
  ('p', "palatal"),
  ('P', "palatal"),
  ('v', "velar"),
  ('q', "labio=velar"),
  ('u', "uvular"),
  ('f', "pharyngeal"),
  ('g', "glottal"),
  ('x', "unspe=cified")])

manners = orderedDict([
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
  ('t', "tap, flap"),
  ('l', "lateral")])

# Takes a list of consonants and returns a layout (c), row labels
# (mannerLabels), and column labels (placeLabels).

def layoutConsonants(consonants, lump):

  # c, the consonant layout, is a dict whose keys are pairs of chars,
  # denoting manner and place, and whose values are lists of IPA
  # symbols.

  c = defaultdict(list)

  # Populate c with the initial layout.

  for consonant in consonants:
    assert isConsonant(consonant)
    c[manner(consonant) + place(consonant)].append(c)

  # Split stops into voiced and unvoiced if it's the only row with
  # voice opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, isVoiced)) == {i}:
    for j in places.keys():
      move(c['v',j], c['s',j], isVoiced)

  # Initially, stops and affricates both have 'stop' place of
  # articulation.  Here I create a new row for affricates if the
  # stop row is the only one with stop/affricate opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, isAffricate)) == {i}:
    for j in places.keys():
      move(c['v',j], c['s',j], isAffricate)

  # Move palatovelars to palatal column if no collisions result.

  if all(j=='p' or not c[i,'p'] or not ANY(ss, isPalatalized) for (i,j), ss in c.items()):
    for j in places.keys():
      for i in manners.keys():
        move(c[i,'p'], c[i,j], isPalatalized)

  # Move labialized sounds to labiovelar column if among labialized
  # sounds, there is no more than one place of articulation for each
  # manner of articulation.

  if all(not MANY(filter(c[i,j], isLabialized) for j in manner) for i in places.keys()):
    for i in places.keys():
      for j in manner:
        move(c[i,'q'], c[i,j], isLabialized)

  # Move w to velar if labiovelar column otherwise empty.

  if all(i=='x' or not c[i,'q'] for i in manner):
    move(c['x','v'], c['x','q'])

  ########
  # Lump #
  ########

  if lump:
    for i in manners.keys():
      move(c[i,'b'], c[i,'l'])
      move(c[i,'v'], c[i,'q'])
      move(c[i,'u'], c[i,'f'])
      move(c[i,'u'], c[i,'g'])
      move(c[i,'u'], c[i,'x'])
    for j in places.keys():
      move(c['x',j], c['r',j])
      move(c['x',j], c['t',j])
      move(c['e',j], c['i',j])

  ######################################
  # Create labels for rows and columns #
  ######################################

  # mannerLabels is a list of pairs, each pair denoting the
  # symbol and the label for each non-empty row.

  mannerLabels = [(i, manners[i]) for
    i in manners.keys() if any(v[i,j] for j in places.keys())]

  # Modify mannerLabels if necessary.

  # Use a more specific label for ejective/creaky if possible.
  eSounds = [s for j in places.keys() for s in c['e',j]]
  if NONE(eSounds, ejective):
    mannerLabels['e'] = 'creaky@stop'
  if ALL(eSounds, ejective):
    mannerLabels['e'] = 'ejective@stop'

  # Are there non-plain stops?
  if ANY(c[i,j] for j in places.keys() for i in 'aevp'):
    # Are plain and voiced stops mixed together?
    if ANY(isVoiced(sound) for j in places.keys() for sound in c['s',j]):
      mannerLabels['s'] = 'plain/voiced@stop'
    else:
      mannerLabels['s'] = 'plain@stop'

  # Lump rows?
  if lump:
    mannerLabels['x'] = 'attf'
    mannerLabels['e'] = 'glottalized@stop'

  # Are there affricates mixed in with stops?
  for i in "aesvp":
    if ANY(ANY(c[i,j], isAffricate) for j in places.keys()):
      mannerLabels[i] += '/affricate'

  # placeLabels is a list of pairs, each pair denoting the
  # symbol and the label for each non-empty column.

  placeLabels = [(j, places[j]) for
    j in places.keys() if any(v[i,j] for i in manners.keys())]

  # Lump columns?
  if lump:
    placeLabels['u'] = 'pvus'
    placeLabels['b'] = 'labial'

  return (c, mannerLabels, placeLabels)
