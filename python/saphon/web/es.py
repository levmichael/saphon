metalang_code = 'es'
metalang = 'Español'
head_first = True
 
consonants = 'consonantes'
 
bilabial = 'bilabial'
labial = 'labial'
labiodental = 'labiodental'
labio__dental = 'labio-<br/>dental'
dental = 'dental'
alveolar = 'alveolar'
post_alveolar = 'post-alveolar'
post__alveolar = 'post-<br/>alveolar'
retroflex = 'retrofleja'
palatal = 'palatal'
velar = 'velar'
post_velar = 'post-velar'
pvus = 'post-velar/<br/>no especificada'
labiovelar = 'labiovelar'
labio__velar = 'labio-<br/>velar'
uvular = 'uvular'
pharyngeal = 'faringeal'
glottal = 'glotal'
unspe__cified = 'no espe-<br/>cificada'
 
stop = 'oclusiva'
affricate = 'africada'
fricative = 'fricativa'
nasal = 'nasal'
approximant = 'aproximante'
trill = 'vibrante multiple'
tap_flap = 'vibrante simple'
lateral = 'lateral'
attf = 'approx./vibrante'
 
glottalized = 'glotalizada'
ejective = 'eyectiva'
creaky = 'laringealizada'
plain = 'sorda'
voiced = 'sonora'
aspirated = 'aspirada'
prenasalized = 'prenasalizada'
implosive = 'implosiva'
 
vowels = 'vocales'
 
high = 'cerrada'
near_high = 'casi cerrada'
mid_high = 'semicerrada'
mid = 'intermedia'
mid_low = 'semiabierta'
near_low = 'casi abierta'
low = 'abierta'
 
front = 'anterior'
central = 'central'
back = 'posterior'
 
unrounded = 'no redondeada'
rounded = 'redondeada'
 
suprasegmental = 'suprasegmental'
tone = 'tono'
laryngeal_harmony = 'armonía laringeal'
nasal_harmony = 'armonía nasal'
 
other_names = 'otros nombres'
geographical_location = 'localización geográfica'
location = 'localización'
language_code = 'código de lengua'
family = 'familia'
notes = 'notas'
bibliography = 'bibliografía'
 
map = 'mapa'

language_lists_text = """
<?php include("header-title.php"); ?>
<?php include("nav-languages.php"); ?>
<div id="content">
<h5> Listas de Lenguas </h5>
<p>
Para facilitar la búsqueda del inventario que le interese, la
información de la tabla puede ser organizada a partir del nombre
de la lengua, código de la lengua, familia lingüística, o país. Si no
escoge una categoría, la tabla será organizada por nombre de lenguas.
Para cambiar el tipo de organización, seleccione una categoría del
encabezamiento de las columnas.
</p><p>
Para examinar un inventario en particular, seleccione el nombre de
la lengua en primera columna de la izquierda.
</p><p>
Los códigos de lengua que usamos en la base de datos de SAPhon son
los códigos ISO 639-3, excepto en los casos que: 1) ISO 639-3 no
tiene un código para la lengua;  2) necesitamos distinguir variedades
que no son distinguidas por ISO 693-3, en estos casos le añadimos
una extensión de tres letras al código.
</p>
</div><br/>
"""

language_lists_sort_method = (
  "por-nombre",
  "por-iso",
  "por-familia",
  "por-pais")

language_lists_columns = (
  "Nombre de la lengua",
  "Código",
  "Familia",
  "País")

language_lists_show_alternates = (
  "Mostrar opciones",
  "Esconder opciones")

find_by_phonemes_phonemes = "fonemas"

find_by_phonemes_text = """
<h5>Encuentre lenguas mediante fonemas</h5>
Esta herramienta para búsquedas le permite encontrar lenguas por
medio de la especificación de fonemas en los respectivos inventarios
fonológicos y/o la especificación de lenguas cuyos fonemas se
encuentren ausentes de sus respectivos invenatarios. </p>

<p>
Para incluir o excluir fonemas en algún inventario haga click en la tabla
que se encuentra abajo. Para incluir algún fonema particular en el
inventario, haga click en el símbolo correspondiente en el símbolo de
la AFI en la tabla que se encuentra abajo y de manera que se torna
azul, así: <span class="demo yes">t</span>.
Para excluir un fonema del inventario, haga click en el
símbolo de la AFI correspondiente de manera que se ponga rojo,
así: <span class="demo no">t</span>.
Si hace click en un símbolo de la AFI por tercera vez anulará
la selección por completo. Note que también puede hacer click en el
botón de REINICIAR que se encuentra en el área inferior a la derecha
para anular todas sus selecciones. </p>

<p>
El conjunto de lenguas correspondiente al inventario que ha
especificado aparece debajo de la tabla. Este grupo de lenguas
consiste en las lenguas cuyos inventarios fonológicos incluyen
las formas en azul y excluyen las formas rojas. </p>

<p>
La configuración
automática de la tabla exclude segmentos raros. Para incluir a todos
los segmentos en la tabla, incluso los muy raros, haga click en el botón
nombrado MOSTRAR MAS FONEMAS localizada en la parte inferior de
la tabla. <a id=scroller href="#">Para ver mas mueva el cursor
a la parte inferior de la tabla.</a></p>
"""

find_by_phonemes_more_phonemes = "MOSTRAR MAS FONEMAS"

find_by_phonemes_fewer_phonemes = "MOSTRAR MENOS FONEMAS"

find_by_phonemes_reset = "REINICIAR"

find_by_phonemes_matches = "Coincidencias"

none = "ninguno"
