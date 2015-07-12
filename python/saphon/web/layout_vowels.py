import collections

# Takes a list of vowels and returns a layout (v), row labels
# (heightLabels), and column labels (backnessLabels).

def layoutVowels(vowels, lump):

  # v, the vowel layout, is a dict whose keys are pairs of chars, 
  # denoting height and backness, and whose values are lists of IPA
  # symbols.

  v = collections.defaultdict(list) 

  # Populate v with the initial layout.

  for vowel in vowels:
    assert isVowel(vowel)
    v[height(vowel) + backness(vowel)].append(v)

  #####################################
  # Attempt adjustments to the layout #
  #####################################

  # Collapse mid-high, mid, mid-low if there is no opposition
  # at any backness.

  if none(many(v[i,j] for i in '345') for j in backnesses):
    for j in backnesses:
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

  if none(v['1',j] and v['2',j] for j in backnesses):
    for j in backnesses:
      move(v['1',j], v['2',j])

  # Move near-high to high if there is no opposition at any
  # backness.

  if none(v['7',j] and v['6',j] for j in backnesses):
    for j in backnesses:
      move(v['7',j], v['6',j])

  ########
  # Lump #
  ########

  if lump:
    for j in backnesses:
      move(v['7',j], v['6',j])
      move(v['1',j], v['2',j])
      move(v['4',j], v['5',j])
      move(v['4',j], v['3',j])

  ################################################
  # Create labels for non-empty rows and columns #
  ################################################
  
  # heightLabels is a list of pairs, each pair denoting the 
  # symbol and the label for each non-empty row.

  heightLabels = [(i, defaultHeightLabels[i]) for
    i in heights if any(v[i,j] for j in backnesses)]

  # backnessLabels is a list of pairs, each pair denoting the 
  # symbol and the label for each non-empty column.

  backnessLabels = [(j, defaultBacknessLabels[j]) for
    j in backnesses if any(v[i,j] for i in backnesses)]

  return (v, heightLabels, backnessLabels)
