
# map locations
def write(saphonData, htmlDir):
  fo = open(htmlDir + '/lang.xml', 'w')
  fo.write('<markers>\n')
  for l in saphonData.lang_:
    fo.write( '  <marker title="' + l.name + '" ' +
      'iso_code="' + l.iso_[0] + '" ' +
      'language="' + l.name + '" ' +
      'family="' + l.familyStr + '" ' +
      'labeltype="type1\" ' +
      'link="http:inv/' + l.nameComp + '.html" ' +
      'lat="' + str(l.geo_[0].lat) + '" ' +
      'lng="' + str(l.geo_[0].lon) + '"/>\n')
  fo.write( '</markers>\n')
  fo.close()
