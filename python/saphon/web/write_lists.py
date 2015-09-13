from copy import copy
from util import *

# This is the representation of a table row.
class TableRow:
  def __init__(self, key, nameComp, name, iso_, familyStr, country_):
    assert key != None
    self.key = key              # for sorting purposes
    self.nameComp = nameComp
    self.name = name
    self.iso_ = iso_
    self.familyStr = familyStr
    self.country_ = country_

# The 4 functions below each take a language and yields one 
# or more rows in the table.
def rowsKeyedByName(lang):
  for name in [lang.name] + lang.nameAlt_:
    yield TableRow(
      normalize(name),
      lang.nameComp,
      name,
      lang.iso_,
      lang.familyStr,
      lang.country_)

def rowsKeyedByISO(lang):
  for iso in lang.iso_:
    yield TableRow(
      normalize(iso),
      lang.nameComp,
      lang.name,
      [iso] + [x for x in lang.iso_ if x != iso],
      lang.familyStr,
      lang.country_)
 
def rowsKeyedByFamily(lang):
  for family in [lang.familyStr]:
    yield TableRow(
      normalize(family) + ' ' + normalize(lang.name),
      lang.nameComp,
      lang.name,
      lang.iso_,
      family,
      lang.country_)

def rowsKeyedByCountry(lang):
  for country in lang.country_:
    yield TableRow(
      normalize(country) + ' ' + normalize(lang.name),
      lang.nameComp,
      lang.name,
      lang.iso_,
      lang.familyStr,
      [country] + [x for x in lang.country_ if x != country])

rowGenerator_ = [
  rowsKeyedByName,
  rowsKeyedByISO,
  rowsKeyedByFamily,
  rowsKeyedByCountry]

def writeLocal(saphonData, htmlDir, loc):
  metalang = loc.metalang_code
  column_ = loc.language_lists_columns
  altStr_ = ['', '-alt']
  altText_ = loc.language_lists_show_alternates
  sortStr_ = loc.language_lists_sort_method

  # Write a file for each permutation of sort method and hide/show alternates.
  for iSort in range(len(sortStr_)):
    sortStr = loc.language_lists_sort_method[iSort]
    rowGen = rowGenerator_[iSort]

    for iAlt in range(2): # 0 = hide alternates
      fo = open(htmlDir+'/'+metalang+'/'+sortStr_[iSort]+altStr_[iAlt]+'.php', 'w')
      fo.write(loc.language_lists_text)
      fo.write('<table class=index><tr>\n')

      # Write table headers
      for j in range(len(column_)):
        fo.write('<th>')
        if iSort == j:
          fo.write(column_[j] + '<br/>' + '<span><a href="' + 
            sortStr_[iSort] + altStr_[1-iAlt] + '.php">' + 
            altText_[iAlt] + '</a></span>')
        else:
          fo.write('<a href="' + sortStr_[j] + altStr_[iAlt] + '.php">' + 
            column_[j] + '</a>')
        fo.write('</th>')
      fo.write('<th></th>')

      # Gather rows
      if iAlt == 1:
        row_ = [row for lang in saphonData.lang_ for row in rowGen(lang)]
      else:
        row_ = [next(rowGen(lang)) for lang in saphonData.lang_]

      # Sort rows
      row_.sort(key=lambda row: row.key)

      # Write table rows
      for row in row_:
        fo.write('</tr><tr>\n')
        fo.write('<td><a href="inv/' + row.nameComp + '.html">' + row.name + '</a></td>')
        fo.write('<td>' + ', '.join(row.iso_) + '</td>')
        fo.write('<td>' + row.familyStr + '</td>')
        fo.write('<td>' + ', '.join(row.country_) + '</td>')
        fo.write('<td><a href="./?c=%s">%s</a></td>' % (row.iso_[0], loc.map.capitalize()))

      fo.write('</tr></table>\n')
      fo.write('</body>\n')
      fo.close()
