metalang_code = 'en'
metalang = 'English'
head_first = False

consonants = 'consonants'
 
bilabial = 'bilabial'
labial = 'labial'
labiodental = 'labiodental'
labio__dental = 'labio-<br/>dental'
dental = 'dental'
alveolar = 'alveolar'
post_alveolar = 'post-alveolar'
post__alveolar = 'post-<br/>alveolar'
retroflex = 'retroflex'
palatal = 'palatal'
velar = 'velar'
post_velar = 'post-velar'
pvus = 'post-velar/<br/>unspecified'
labiovelar = 'labiovelar'
labio__velar = 'labio-<br/>velar'
uvular = 'uvular'
pharyngeal = 'pharyngeal'
glottal = 'glottal'
unspe__cified = 'unspe-<br/>cified'
 
stop = 'stop'
affricate = 'affricate'
fricative = 'fricative'
nasal = 'nasal'
approximant = 'approximant'
trill = 'trill'
tap_flap = 'tap, flap'
lateral = 'lateral'
attf = 'approx./trill/tap/flap'
 
glottalized = 'glottalized'
ejective = 'ejective'
creaky = 'creaky'
plain = 'plain'
voiced = 'voiced'
aspirated = 'aspirated'
prenasalized = 'prenasalized'
implosive = 'implosive'
 
vowels = 'vowels'
 
high = 'high'
near_high = 'near high'
mid_high = 'mid-high'
mid = 'mid'
mid_low = 'mid-low'
near_low = 'near low'
low = 'low'
 
front = 'front'
central = 'central'
back = 'back'
 
unrounded = 'unrounded'
rounded = 'rounded'
 
suprasegmental = 'suprasegmental'
tone = 'tone'
laryngeal_harmony = 'laryngeal harmony'
nasal_harmony = 'nasal harmony'
 
other_names = 'other names'
geographical_location = 'geographical location'
location = 'location'
language_code = 'language code'
family = 'family'
notes = 'notes'
bibliography = 'bibliography'
 
map = 'map'

language_lists_text = """
<?php include("header-title.php"); ?>
<?php include("nav-languages.php"); ?>
<div id="content">
<h5> Language Lists </h5>
<p>
The table below can be sorted by Language name, Language code, Family,
or Country, to facilitate locating the inventory that interests
you. If no sort is chosen, it is automatically sorted by Language
Name; to change the sort, click on the relevant column heading.
</p><p>
In order to view an inventory for a particular language, click
on the language name in the leftmost column.  To view the
location of the language in the Map Browse function, click
the ‘Map’ link in the rightmost column.
</p><p>
The language codes that we employ in the SAPhon database are ISO
639-3 codes, except in those cases where: 1) ISO 639-3 does not
have a code for the language; or 2) we need to distinguish varieties
not distinguished by ISO 639-3, in which case we add a three letter
extension to the code.
</p>
</div><br/>
"""

language_lists_sort_method = (
  "by-name",
  "by-iso",
  "by-family",
  "by-country")

language_lists_columns = (
  "Language Name",
  "Code",
  "Family",
  "Country")

language_lists_show_alternates = (
  "Show alternates",
  "Hide alternates")

find_by_phonemes_phonemes = "phonemes"

find_by_phonemes_text = """
<h5>Find language by phonemes</h5>
<p>This search tool allows you to find languages by specifying which phonemes are present in their phonological inventories and/or by specifying phonemes which phonemes  are absent from their inventories.</p>

<p>To include phonemes in an inventory, or to exclude them, click on the chart    below.  To include a particular phoneme in the inventory, click on the appropriate IPA  symbol in the chart below, so that it turns blue, like this: <span class="demo yes">t</span>.  To exclude a particular phoneme from the inventory, click on the appropriate    IPA symbol twice, so that it turns red, like this: <span class="demo no">t</span>.      Clicking on an IPA symbol a third time will deselect it entirely. Note also that you    can click on the RESET label in the lower right hand corner of the table to deselect    all symbols.</p>

<p>The set of languages that matches the inventory that you have specified        appears below the table. This set of languages consists of the languages whose          phonological inventories possess the phonemes in blue and lack the ones in red.</p>

<p>The default setting of the table excludes very rare segments. To include all   segments in the table, including very rare ones, click the SHOW MORE PHONEMES label at  the bottom of the table.
<a id=scroller href="#">Scroll down to see more.</a>
</p>
"""

find_by_phonemes_more_phonemes = "SHOW MORE PHONEMES"

find_by_phonemes_fewer_phonemes = "SHOW FEWER PHONEMES"

find_by_phonemes_reset = "RESET"

find_by_phonemes_matches = "Matches"

none = "none"
