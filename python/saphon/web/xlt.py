
# Translates string s into meta-language given by loc.  s may
# maximally be a list of adjectives followed by a list of bare
# nouns, e.g.:
#
#    ejective/creaky@stop/affricate
#
# loc.head_first is consulted to determine the order of words
# in the output.

def xlt(loc, s):

  # Translate a term by looking it up in loc.
  def xltWord(term):
    return loc.__dict__[term]

  # Translate terms separated by slashes.
  def xltSlash(terms):
    return '/'.join(xltWord(term) for term in terms.split('/'))

  # Translate sets of terms separated by at-sign.
  phrase = [xltSlash(terms) for terms in s.split('@')]

  # Reorder if applicable
  if len(phrase) == 2 and loc.head_first:
    out = phrase[1] + ' ' + phrase[0]
  else:
    out = ' '.join(phrase)

  return out

def Xlt(loc, s):
  return xlt(loc, s).capitalize()
