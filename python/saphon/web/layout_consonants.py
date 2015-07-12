import collections

# Takes a list of consonants and returns a layout (c), row labels
# (mannerLabels), and column labels (placeLabels).

def layoutConsonants(consonants, lump):

  # c, the consonant layout, is a dict whose keys are pairs of chars,
  # denoting manner and place, and whose values are lists of IPA
  # symbols.

  c = collections.defaultdict(list)

  # Populate c with the initial layout.

  for consonant in consonants:
    assert isConsonant(consonant)
    c[manner(consonant) + place(consonant)].append(c)

  # Split stops into voiced and unvoiced if it's the only row with
  # voice opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, isVoiced)) == {i}:
    for j in places:
      move(c['v',j], c['s',j], isVoiced)

  # Initially, stops and affricates both have 'stop' place of
  # articulation.  Here I create a new row for affricates if the
  # stop row is the only one with stop/affricate opposition.

  if set(i for (i,j), ss in c.items() if SOME(ss, isAffricate)) == {i}:
    for j in places:
      move(c['v',j], c['s',j], isAffricate)

  # Move palatovelars to palatal column if no collisions result.

  if all(j=='p' or not c[i,'p'] or not ANY(ss, isPalatalized) for (i,j), ss in c.items()):
    for j in places:
      for i in manners:
        move(c[i,'p'], c[i,j], isPalatalized)

  # Move labialized sounds to labiovelar column if among labialized
  # sounds, there is no more than one place of articulation for each
  # manner of articulation.

  if all(not MANY(filter(c[i,j], isLabialized) for j in manner) for i in places):
    for i in places:
      for j in manner:
        move(c[i,'q'], c[i,j], isLabialized)

  # Move w to velar if labiovelar column otherwise empty.

  if all(i=='x' or not c[i,'q'] for i in manner):
    move(c['x','v'], c['x','q'])

  ########
  # Lump #
  ########

  if lump:
    for i in manners:
      move(c[i,'b'], c[i,'l'])
      move(c[i,'v'], c[i,'q'])
      move(c[i,'u'], c[i,'f'])
      move(c[i,'u'], c[i,'g'])
      move(c[i,'u'], c[i,'x'])
    for j in places:
      move(c['x',j], c['r',j])
      move(c['x',j], c['t',j])
      move(c['e',j], c['i',j])

  ################################################
  # Create labels for non-empty rows and columns #
  ################################################

  # mannerLabels is a list of pairs, each pair denoting the
  # symbol and the label for each non-empty row.

  mannerLabels = [(i, defaultMannerLabels[i]) for
    i in manners if any(v[i,j] for j in places)]

  # Modify mannerLabels if necessary.

  # Are there affricates mixed in with stops?
  for i in "aesvp":
    if ANY(ANY(c[i,j], isAffricate) for j in places):
      mannerLabels[i] += '/affricate'

  # Are there non-plain stops?
  if ANY(c[i,j] for j in places for i in 'aevp'):
    # Are plain and voiced stops mixed together?
    if ANY(isVoiced(sound) for j in places for sound in c['s',j]):
      mannerLabels['s'] = 'plain/voiced@' + mannerLabels['s']
    else:
      mannerLabels['s'] = 'plain@' + mannerLabels['s']

  # placeLabels is a list of pairs, each pair denoting the
  # symbol and the label for each non-empty column.

  placeLabels = [(j, defaultPlaceLabels[j]) for
    j in places if any(v[i,j] for i in manners)]
