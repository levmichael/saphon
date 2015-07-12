import unicodedata as ud

# Turn a language name, etc, into a string with desirable collation
# properties.
def normalize(s):
  s2 = ud.normalize('NFKD', s)
  s3 = ''.join(c for c in s2 if not ud.combining(c))
  return s3.replace('ɨ', 'i').replace('ʔ', '').lower()
