import sys

if len(sys.args) < 3:
   print('write.py SAPHON_DIR HTML_DIR')
   sys.exit(1)

saphon_dir, html_dir = sys.args[1:3]

saphon_data = saphon.readSaphonFiles(saphon_dir)

module_names = (
  'write_inventories',
  'write_lists',
  'write_phonemes',
  'write_saphon_php',
  'write_lang_xml')

for mn in module_names:
  m = __import__(mn)
  print('Writing ' + m.file_out
  m.write(saphon_data, html_dir)
