metalang_code = 'pt'
metalang = 'Português'
head_first = True

consonants = 'consoantes'

bilabial = 'bilabial'
labial = 'labial'
labiodental = 'labiodental'
labio__dental = 'labio-<br/>dental'
dental = 'dental'
alveolar = 'alveolar'
post_alveolar = 'pós-alveolar'
post__alveolar = 'pós-<br/>alveolar'
retroflex = 'retroflexa'
palatal = 'palatal'
velar = 'velar'
post_velar = 'pós-velar'
pvus = 'pós-velar/<br/>não especificada'
labiovelar = 'labiovelar'
labio__velar = 'labio-<br/>velar'
uvular = 'uvular'
pharyngeal = 'faringal'
glottal = 'glotal'
unspe__cified = 'não espe-<br/>cificada'

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
ejective = 'ejectiva'
creaky = 'laringealizada'
plain = 'surda'
voiced = 'sonora'
aspirated = 'aspirada'
prenasalized = 'pré-nasal'
implosive = 'implosiva'

vowels = 'vogais'

high = 'fechada/alta'
near_high = 'quase fechada'
mid_high = 'semifechada'
mid = 'média'
mid_low = 'semiaberta'
near_low = 'quase aberta'
low = 'aberta/baixa'

front = 'anterior'
central = 'central'
back = 'posterior'

unrounded = 'não arredondada'
rounded = 'arredondada'

suprasegmental = 'suprasegmental'
tone = 'tom'
laryngeal_harmony = ' harmonia laringeal'
nasal_harmony = 'harmonia nasal'

other_names = 'outros nomes'
geographical_location = 'localização geográfica'
location = 'localização'
language_code = 'código de língua'
family = 'família'
notes = 'notas'
bibliography = 'bibliografia'

map = 'mapa'

language_lists_text = """
<?php include("header-title.php"); ?>
<?php include("nav-languages.php"); ?>
<div id="content">
<h5> Listas de Línguas </h5>
<p>
Para facilitar a procura do inventário que lhe interesse, a
informação da tabela pode ser organizada segundo o nome da
língua, código da língua, família linguística ou país. Se não
escolher uma categoria, a tabela será organizada automaticamente
por nome de línguas. Para mudar o tipo da organização, selecione
uma categoria do cabeçalho da coluna.
</p><p>
Para examinar um inventário de uma língua particular, selecione
o nome da língua na primeira coluna da esquerda.
</p><p>
Os códigos de língua que utilizamos na base de dados de SAPhon
são os códigos ISO 639-3, com a exceção dos casos onde: 1)
ISO 639-3 não tem um código para a língua; ou 2) necessitamos
distinguir variedades não distinguidos por ISO 639-3. Neste
caso, adicionamos uma extensão de três letras ao código.
</p>
</div><br/>
"""

language_lists_sort_method = (
  "por-nome",
  "por-iso",
  "por-familia",
  "por-pais")

language_lists_columns = (
  "Nome de língua",
  "Código",
  "Família",
  "País")

language_lists_show_alternates = (
  "Mostrar opções",
  "Esconder opções")

find_by_phonemes_phonemes = "fonemas"

find_by_phonemes_text = """
<h5>Encontrar língua por fonemas</h5>
<p>Com este instrumento de procura, pode encontrar línguas por especificar quais  fonemas são presentes nos seus inventários fonológicos e/ou por especificar quais       fonemas são ausentes dos seus inventários.</p>

<p>Para incluir fonemas num inventário, ou para excluí-los, clique na tabela      abaixo. Para incluir um fonema particular no inventário, clique no símbolo apropriado   do AFI na tabela abaixo para que vire azul, como assim: <span class="demo yes">t</     span>. Para excluir um fonema particular do inventário, clique no símbolo apropriado do AFI duas vezes para que vire vermelho, como assim: <span class="demo no">t</span>.      Clicar em um símbolo do AFI uma terceira vez vai excluí-lo completamente da seleção.    Observe também que pode clicar no botão RESET na quina esquerda para baixo da tabela    para excluir todos os símbolos.</p>

<p>O grupo de línguas que corresponde ao inventário que especificou aparece       abaixo da tabela. Este grupo de línguas consiste nas línguas cujos inventários          fonológicos possuam os fonemas em azul e faltem os em vermelho.</p>

<p>A configuração padrão da tabela exclui os segmentos muito raros. Para incluir  todos os segmentos na tabela, inclusive os mais raros, clique o botão MOSTRAR MAIS      FONEMAS no fundo da tabela.  <a id=scroller href="#">Role para baixo para ver mais      informação.</a></p>
"""

find_by_phonemes_more_phonemes = "MOSTRAR MAIS FONEMAS"

find_by_phonemes_fewer_phonemes = "MOSTRAR MENOS FONEMAS"

find_by_phonemes_reset = "RESET"

find_by_phonemes_matches = "Correspondentes"

none = "nenhum"
