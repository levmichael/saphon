import sys, os
import saphon.io

if len(sys.argv) < 3:
   print('write.py SAPHON_DIR HTML_DIR')
   sys.exit(1)

saphonDir, htmlDir = sys.argv[1:3]

saphonData = saphon.io.readSaphonFiles(saphonDir)

generationModules = [__import__(m) for m in (
  #'write_inventories',
  #'write_phonemes',
  'write_lists',
  'write_saphon_php',
  'write_lang_xml')]

localizationModules = [__import__(m) for m in
  ('en', 'es', 'pt')]

# Create directories
os.makedirs(htmlDir, exist_ok=True)
for locMod in localizationModules:
  os.makedirs(htmlDir + '/' + locMod.metalang_code, exist_ok=True)

# Create HTML files 
for genMod in generationModules:
  if hasattr(genMod, 'write'):
    genMod.write(saphonData, htmlDir)
  if hasattr(genMod, 'writeLocal'):
    for locMod in localizationModules:
      genMod.writeLocal(saphonData, htmlDir, locMod)
