# Author: Michael Pollack

import json
import os, sys
from pathlib import Path
import uuid
import unicodedata

with open('../resources/ipa.json', 'r', encoding='utf-8') as ipa_file:
    ipa = json.load(ipa_file)

def normalizeIPA(s):
  return unicodedata.normalize('NFD', s)

#Generates a dictionary that maps phonemes to their category codes for easy access
def flip_ipa(ipa):
    new_map = {}
    scraped_order = []
    for category in ipa:
        for symbol in category["symbols"]:
            new_map[symbol["symbol"]] = category["category"]
            scraped_order.append(symbol["symbol"])
    return new_map, scraped_order

#Dictionary flipper to ensure mappings only have to be done once
def flip_dict(original_dict):
    flipped_dict = {}
    for key, value in original_dict.items():
        flipped_dict[value] = key    
    return flipped_dict

places = {
    "Bilabial": "b",
    "Labiodental": "l",
    "Dental": "d",
    "Alveolar": "a",
    "Postalveolar": "o",
    "Retroflex": "r",
    "Palatal": "p",
    "Velar": "v",
    "Uvular": "u",
    "Pharyngeal": "f",
    "Glottal": "g",
    "Other": "q",
    "Special": "x"
    }

manners = {
    "Stop": "s",
    "Aspirated stop": "a",
    "Fricative": "f",
    "Affricate": "aff",
    "Nasal": "n",
    "Nasal compound": "p",
    "Trill": "r",
    "Tap, Flap": "t",
    "Lateral": "l",
    "Approximant": "x",
    "Implosive": "i",
    "Extra": "e"
}

heights = {
    "High": "7",
    "Low-High": "6",
    "High-Mid": "5",
    "Mid": "4",
    "Low-Mid": "3",
    "High-Low": "2",
    "Low": "1",
}

backness = {
    "Front": "f",
    "Center": "c",
    "Back": "b"
}

abbreviations = {
    "BN": "Nasal Boundary",
    "BO": "Oral Boundary",
    "LDNH": "Long Distance Nasal Harmony",
    "LDOH": "Long Distance Oral Harmony",
    "LN": "Local Nasalization",
    "LNsyll": "Long Distance Nasal Assimilation",
    "LO": "Local Oralization",
    "PNV": "Post Nasal Voicing"
}

ipa_flipped, scraped_order = flip_ipa(ipa)
places_flipped = flip_dict(places)
manners_flipped = flip_dict(manners)
heights_flipped = flip_dict(heights)
backness_flipped = flip_dict(backness)
lost_phonemes = set()

def new_index(indices: set):
    index_hash = str(uuid.uuid4())
    while index_hash in indices:
        index_hash = str(uuid.uuid4())
    indices.add(index_hash)
    return index_hash

def generate_ipa_subsets(phonemes):
    consonant_subset = {
        "manners": {},
        "places": {}
    }
    vowels_subset = {
        "heights": {},
        "backness": {}
    }
    category_set = set()
    for phoneme in phonemes:
        if phoneme in ipa_flipped:
            category_set.add(ipa_flipped[phoneme])
        else:
            normalized_phoneme = normalizeIPA(phoneme)
            if normalized_phoneme in ipa_flipped:
                category_set.add(ipa_flipped[normalized_phoneme])
            else:
                lost_phonemes.add(phoneme)

    #Determines the rows and columns needed for this table
    for cat in category_set:

        #Other Consonants
        if cat[0] == "c":
            if len(cat) > 4:
                manner_name = "Affricate"
            else:
                manner_name = manners_flipped[cat[1]]
            place_name = places_flipped[cat[2]]
            consonant_subset["manners"][manner_name] = set()
            consonant_subset["places"][place_name] = set()
        
        #Vowels
        elif cat[0] == "v":
            height_name = heights_flipped[cat[1]]
            backness_name = backness_flipped[cat[2]]
            vowels_subset["heights"][height_name] = set()
            vowels_subset["backness"][backness_name] = set()
    
    #Creates the sets used to map each phoneme to a cell
    these_lost_phonemes = set()
    for phoneme in phonemes:
        if phoneme not in ipa_flipped:
            normalized_phoneme = normalizeIPA(phoneme)
            if normalized_phoneme in ipa_flipped:
                this_cat = ipa_flipped[normalized_phoneme]
            else:

                #TODO: Handle lost phonemes
                these_lost_phonemes.add(phoneme)
                continue

        else:
            this_cat = ipa_flipped[phoneme]
        if this_cat[0] == "c":
            if len(this_cat) > 4:
                consonant_subset["manners"]["Affricate"].add(phoneme)
            else:  
                consonant_subset["manners"][manners_flipped[this_cat[1]]].add(phoneme)
            consonant_subset["places"][places_flipped[this_cat[2]]].add(phoneme)
        elif this_cat[0] == "v":
            vowels_subset["heights"][heights_flipped[this_cat[1]]].add(phoneme)
            vowels_subset["backness"][backness_flipped[this_cat[2]]].add(phoneme)

    return consonant_subset, vowels_subset, these_lost_phonemes

def generate_ipa_chart(phonemes: set, allophones: dict, subset: dict, consonant: bool):
    if consonant:
        title = "Consonants"
        col, subCol = places, "places"
        row, subRow = manners, "manners"
    else:
        title = "Vowels"
        col, subCol = backness, "backness"
        row, subRow = heights, "heights"
    html = f"<h2>{title}</h2><table>"
    html += "<tr><th></th>" + "".join(f"<th>{x}</th>" for x in col if x in subset[subCol]) + "</tr>"
    pure_allophones = set(allophones.keys()) - phonemes
    for y in row: 
        if y in subset[subRow]:
            html += f"""
            <tr id="{y}"><th>{y}</th>
            """
            for x in col:
                if x in subset[subCol]:
                    html += f"<td>"
                    these_symbols = subset[subRow][y] & subset[subCol][x]
                    voiced, unvoiced = [], []
                    for symbol in these_symbols:

                        #TODO: Handle lost phonemes
                        if symbol in ipa_flipped:
                            normalized_symbol = symbol

                        else:
                            normalized_symbol = normalizeIPA(symbol)
                        if ipa_flipped[normalized_symbol][3] == "u":
                            unvoiced.append(symbol)
                        else:
                            voiced.append(symbol)
                    ordered = unvoiced + voiced
                    for symbol in ordered:
                        if symbol in pure_allophones:
                            html += f"""
                            <span id="{symbol}" class="visible-allophone"> {symbol} </span>
                            """
                        else: 
                            html += f"""
                            <span id="{symbol}" class="visible-phoneme"> {symbol} </span>
                            """
                    html += f"</td>"
            html += "</tr>"
    html += "</table>"
    return html

def generate_html_body(lang, template, processes, process_map, phonemes, allophones, indices, num_references=0):
    info = lang['info']
    iso_code = ', '.join(info['iso_codes']) if info['iso_codes'] != [] else 'N/A'
    coordinates = info['coordinates']
    if coordinates in ( None, [], [{}] ):
        coords = '<div class=value>N/A</div>'
    else:
        coords = ''
        for coord in coordinates:
            elev = f'; {coord["elevation_meters"]} meters' if coord['elevation_meters'] is not None else ''
            coords += f'<div class=value>{coord["latitude"]}° {coord["longitude"]}°{elev}</div>'
    consonant_subset, vowel_subset, these_lost_phonemes = generate_ipa_subsets(phonemes | set(allophones.keys()))
    html_content = f"""
    <div class=entry>
    """
    if num_references != 0:
        html_content += f"""
        <hr>
        <h1>Document</h1>
        """
    html_content += f"""
    <h1>{info['name']}</h1>
    <div class=field><div class=key>Alternate name(s)</div><div class=value>{", ".join(info['alternate_names'])}</div></div>
    <div class=field><div class=key>ISO code(s)</div><div class=value>{iso_code}</div></div>
    <div class=field><div class=key>Glottolog code</div><div class=value>{info['glottolog_code']}</div></div>
    <div class=field><div class=key>Location</div>{coords}</div></div>
    <div class=field><div class=key>Family</div><div class=value>{info['family']}</div></div>
    """
    html_content += generate_ipa_chart(phonemes, allophones, consonant_subset, True)
    html_content += generate_ipa_chart(phonemes, allophones, vowel_subset, False)

    if template['natural_classes'] != []:
        html_content += f"<h2>Natural classes</h2><table>"
        html_content += '<tr><th>Symbol</th><th>Members</th></tr>\n'
        for nc in template['natural_classes']:
            html_content += f'<tr><td>{nc["symbol"]}</td><td>{", ".join(nc["members"])}</td></tr>\n'
        html_content += '</table>\n'

    #TODO: Handle Lost Phonemes
    if len(these_lost_phonemes) != 0:
        html_content += f"""
        <div class=field><h2>Lost Phonemes</h2>{these_lost_phonemes}</div>
        """

    html_content += f"""
    <div class=field><h2>Processes</h2>{processes}</div>
    <div class=field><h2>Process Details</h2>{process_detail_scraper(template.get("processdetails", []), process_map, indices)}</div>
    """
    try:
        html_content += f"""
          <div class=field><h2>Citation</h2>{'<br />'.join(template['citation'])}</div>
        """
    except KeyError:
        pass

    html_content += f"""
    <div class=field><h2>Summary</h2><p>{template['summary']}</p></div>
    <div class=field><h2>Notes</h2><p>{template['notes']}</p></div>
    """
    return html_content

def generate_synthesis_html(lang, filename):
    synth = lang['synthesis']
    global_dropdown_indices = set()
    process_map = generate_process_map(synth.get("processdetails", []))
    processes, phonemes, allophones = process_scraper(synth.get("phonemes", []), process_map, global_dropdown_indices)
    html_content = f"""
    <html>
    <head> 
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="stylesheet" type="text/css" href="../../lang_info.css" />
    <script type="text/javascript"> {initialize_script(allophones)} </script>
    </head>
    <body onload="initialize()">
    """
    html_content += generate_html_body(lang, synth, processes, process_map, phonemes, allophones, global_dropdown_indices)
    html_content += f"""
    <div class=field><h2><a href="/en/ref_inv/{filename}">References</h2></div>
    """

    json_ready = json.dumps(list(global_dropdown_indices))
    html_content += f"""
    </div>
    <div class="hidden" id="globalDropdownIndices" data-set='{json_ready}'></div> 
    </body>
    </html>
    """
    return html_content

def generate_ref_html(lang, filename):
    global_dropdown_indices = set()
    #TODO: Make allophones work here
    allophones = {}
    html_content = f"""
    <html>
    <head> 
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="stylesheet" type="text/css" href="../../lang_info.css" />
    <script type="text/javascript"> {initialize_script(allophones)} </script>
    <h1>Reference Documents: {lang['info'].get("name", "")}</h1>
    </head>
    <body onload="initialize()">
    """
    for ref in lang['sources']:
        process_map = generate_process_map(ref.get("processdetails", []))
        processes, phonemes, allophones = process_scraper(ref.get("phonemes", []), process_map, global_dropdown_indices)
        html_content = html_content + generate_html_body(lang, ref, processes, process_map, phonemes, allophones, global_dropdown_indices, True)

    json_ready = json.dumps(list(global_dropdown_indices))
    html_content += f"""
    </div>
    <div class="hidden" id="globalDropdownIndices" data-set='{json_ready}'></div> 
    </body>
    </html>
    """
    return html_content

def highlight_phonemes_script(allophones):
    json_friendly = {allophone: list(phonemes) for allophone, phonemes in allophones.items()}
    json_allophones = json.dumps(json_friendly)
    html_content = """
    function highlight_phonemes() {
    """
    html_content += f"""
        allophones = {json_allophones};
    """
    #TODO: figure out why background-color doesn't come through in 'highlight' class
    html_content += """ 
        Object.keys(allophones).forEach(id => {
            const span = document.getElementById(id);
            if (span != null) {
                span.addEventListener('mouseover', function () {
                    allophones[id].forEach(associatedId => {
                        document.getElementById(associatedId).classList.add('highlight');
                    });
                });
                span.addEventListener('mouseout', function () {
                    allophones[id].forEach(associatedId => {
                        document.getElementById(associatedId).classList.remove('highlight');
                    });
                });
            }
        });
    }
    """
    return html_content

def dropdown_script():
    process_hider = """
    function dropdown() {
        const global_dropdown_indices_span = document.getElementById("globalDropdownIndices");
        const global_dropdown_indices_raw = global_dropdown_indices_span.getAttribute("data-set");
        const global_dropdown_indices_array = JSON.parse(global_dropdown_indices_raw);
        for (var i = 0; i < global_dropdown_indices_array.length; i += 1) {
            let this_mother = "mother-" + global_dropdown_indices_array[i];
            let this_child = "child-" + global_dropdown_indices_array[i];
            let mother_span = document.getElementById(this_mother);
            let child_span = document.getElementById(this_child);
            mother_span.addEventListener("click", function () {
                if (child_span.style.display === "none" || child_span.style.display === "") {
                    child_span.style.display = "inline";
                } else {
                    child_span.style.display = "none";
                }
            });
        }
    }
    """
    return process_hider

def initialize_script(allophones):
    html_content = dropdown_script()
    # html_content += highlight_phonemes_script(allophones)
    # html_content += """
    # function initialize() {
    #     dropdown();
    #     highlight_phonemes();
    # }
    # """
    html_content += """
    function initialize() {
        dropdown();
    }
    """
    return html_content

def process_scraper(phonemes, process_map, indices):
    phoneme_set = set()
    allophone_map = {}
    mappings =  {}
    for phoneme in phonemes:
        this_phoneme = phoneme["phoneme"]
        phoneme_set.add(this_phoneme)
        mappings[this_phoneme] = []
        for environment in phoneme["environments"]:
            if type(environment) == dict:
                for allophone in environment["allophones"]:
                    this_allophone = allophone["allophone"]
                    if this_allophone != this_phoneme:
                        index_hash = new_index(indices)
                        process_id = "mother-" + index_hash
                        process_name_id = "child-" + index_hash
                        if this_allophone in allophone_map:
                            allophone_map[this_allophone].add(this_phoneme)
                        else:
                            allophone_map[this_allophone] = {this_phoneme}
                        processes = ""
                        for k in range(len(allophone["processnames"])):
                            this_process = allophone["processnames"][k]
                            if this_process in process_map:
                                this_process = process_map[this_process]
                            processes += this_process
                        process = f"""
                        <span class="process" id="{process_id}">/{this_phoneme}/ &#8594; [{this_allophone}] / {environment["preceding"]}_{environment["following"]} </span> <span class="processname" id="{process_name_id}"> <br> {processes} </span>
                        """
                        mappings[this_phoneme].append(process)
    html_content = f"""
    <div class="processtable"><table><tr><th>Phoneme</th><th>Processes</th></tr>
    """
    for mapping in scraped_order:
        if mapping in mappings and mappings[mapping] != []:
            html_content += f"""
            <tr><th> /{mapping}/ </th><td>
            """
            for index, process in enumerate(mappings[mapping]):
                html_content += f"""
                {process} <br>
                """
                if index != len(mappings[mapping]) - 1:
                    html_content += "<br>"
            
            html_content = html_content[:-4]
            html_content += f"""
            </td></tr>
            """
    html_content += f"""
    </table></div>
    """
    return html_content, phoneme_set, allophone_map


def segments_morphemes_and_other_fun(category):
    segNA = False
    morphNA = False
    segments = category["segments"]
    if type(segments) != list:
        if segments == {}:
            segments = []
        else:
            segments = [segments]
    morphemes = category["morphemes"]  
    if type(morphemes) != list:
        if morphemes == {}:
            morphemes = []
        else:
            morphemes = [morphemes]
    segment_units = ""
    morpheme_units = ""
    html_content = f"""
    <span class="process-descriptor-sub">Segments: </span>
    """
    if segments == [] or (len(segments) == 1 and ((segments[0]["units"] == [] or segments[0]["units"] == ["NA"] or segments[0]["units"] == [""]) and (segments[0]["positional_restrictions"] == "" or segments[0]["positional_restrictions"] == "NA"))):
        segNA = True
        html_content += f"""
        <span class="process-descriptor-sub">NA</span><br><br>
        """
    else: 
        html_content += "<br>"
        for segment in segments:
            seg_u_list = segment["units"]
            pos_res_list = segment["positional_restrictions"]
            if len(seg_u_list) > 1:
                segment_units += "{"
            for i in range(len(seg_u_list)):
                segment_units += seg_u_list[i]
                if i < len(seg_u_list) - 1:
                    segment_units += ", "
            if len(seg_u_list) > 1:
                segment_units += "}"
            html_content += f"""
            <span class="process-descriptor-sub">&nbsp;&nbsp;&nbsp;&nbsp;-Units: </span><span class="process-description"> {segment_units} </span><br>
            <span class="process-descriptor-sub">&nbsp;&nbsp;&nbsp;&nbsp;-Positional Restrictions: </span><span class="process-description"> {pos_res_list} </span><br><br>
            """
    html_content += f"""
    <span class="process-descriptor-sub">Morphemes: </span>
    """
    if morphemes == [] or (len(morphemes) == 1 and ((morphemes[0]["units"] == [] or morphemes[0]["units"] == ["NA"] or morphemes[0]["units"] == [""]) and (morphemes[0]["positional_restrictions"] == "" or morphemes[0]["positional_restrictions"] == "NA"))):
        morphNA = True
        html_content += f"""
        <span class="process-descriptor-sub">NA</span><br><br>
        """
    else:
        html_content += "<br>"
        for morpheme in morphemes:
            morph_u_list = morpheme["units"]
            pos_res_list = morpheme["positional_restrictions"]
            for i in range(len(morph_u_list)):
                morpheme_units += morph_u_list[i]
                if i < len(morph_u_list) - 1:
                    morpheme_units += ", "
            html_content += f"""
            <span class="process-descriptor-sub">&nbsp;&nbsp;&nbsp;&nbsp;-Units: </span><span class="process-description"> {morpheme_units} </span><br>
            <span class="process-descriptor-sub">&nbsp;&nbsp;&nbsp;&nbsp;-Positional Restrictions: </span><span class="process-description"> {morpheme["positional_restrictions"]} </span><br><br>
            """
    if segNA and morphNA:
        return "NA"
    else:
        return html_content
    
def generate_process_map(processes):
    process_map = {}
    prefix_count = {}
    for process in processes:
        process_name = process["processname"]
        process_prefix = process_name[:process_name.find(":")] if process_name.find(":") != -1 else process_name
        simple_name = abbreviations[process_prefix] if process_prefix in abbreviations else process_name
        this_count = prefix_count[process_prefix] + 1 if process_prefix in prefix_count else 1
        prefix_count[process_prefix] = this_count
        simple_name += " " + str(this_count)
        process_map[process_name] = simple_name
    return process_map

def process_detail_scraper(processes, process_map, indices):
    html_content = ""
    for process in processes:
        process_name = process["processname"]
        simple_name = process_map[process_name]
        process_type = process["processtype"]
        summary = process["summary"]
        optionality = process["optionality"]
        directionality = process["directionality"]
        alternation_type = process["alternation_type"]
        domain = process["domain"]
        undergoers = segments_morphemes_and_other_fun(process["undergoers"])
        triggers = segments_morphemes_and_other_fun(process["triggers"])
        transparent = segments_morphemes_and_other_fun(process["transparent"])
        opaque = segments_morphemes_and_other_fun(process["opaque"])
        html_content += f"""
        <span class="process-title">{simple_name}</span>
        <div><table class="processDescTable">
        <tr><th><span class="process-descriptor">Abbreviation: </span></th><td><span class="process-description"> {process_name} </span></td></tr>
        <tr><th><span class="process-descriptor">Type: </span></th><td><span class="process-description"> {process_type} </span></td></tr>
        <tr><th><span class="process-descriptor">Description: </span></th><td><span class="process-description"> {summary} </span></td></tr>
        <tr><th><span class="process-descriptor">Optionality: </span></th><td><span class="process-description"> {optionality} </span></td></tr>
        <tr><th><span class="process-descriptor">Directionality: </span></th><td><span class="process-description"> {directionality} </span></td></tr>
        <tr><th><span class="process-descriptor">Alternation Type: </span></th><td><span class="process-description"> {alternation_type} </span></td></tr>
        <tr><th><span class="process-descriptor">Domain: </span></th><td><span class="process-description"> {domain} </span></td></tr>
        <tr><th><span class="process-descriptor">Undergoers: </span></th><td>
        """
        if undergoers != "NA":
            index_hash = new_index(indices)
            html_content += f"""
            <button class="dropdown-button" id={"mother-" + index_hash}> &#9660 </button>
            <span class="pd-subsection" id={"child-" + index_hash}> {undergoers} </span></td></tr>
            """
        else: 
            html_content += f"""
            <span class="na"> NA </span></td></tr>
            """
        html_content += f"""
        <tr><th><span class="process-descriptor">Triggers: </span></th><td>
        """
        if triggers != "NA":
            index_hash = new_index(indices)
            html_content += f"""
            <button class="dropdown-button" id={"mother-" + index_hash}> &#9660 </button>
            <span class="pd-subsection" id={"child-" + index_hash}> {triggers} </span></td></tr>
            """
        else: 
            html_content += f"""
            <span class="na"> NA </span><br></td></tr>
            """
        html_content += f"""
        <tr><th><span class="process-descriptor">Transparent: </span></th><td>
        """
        if transparent != "NA":
            index_hash = new_index(indices)
            html_content += f"""
            <button class="dropdown-button" id={"mother-" + index_hash}> &#9660 </button>
            <span class="pd-subsection" id={"child-" + index_hash}> {transparent} </span></td></tr>
            """
        else: 
            html_content += f"""
            <span class="na"> NA </span></td></tr>
            """
        html_content += f"""
        <tr><th><span class="process-descriptor">Opaque: </span></th><td>
        """
        if opaque != "NA":
            index_hash = new_index(indices)
            html_content += f"""
            <button class="dropdown-button" id={"mother-" + index_hash}> &#9660 </button>
            <span class="pd-subsection" id={"child-" + index_hash}> {opaque} </span></td></tr>
            """
        else: 
            html_content += f"""
            <span class="na"> NA </span></td></tr>
            """
        html_content += f"""
        </table></div>
        <br><br>
        """
    return html_content

def process_templates_from_folder(input_folder, synth_output_folder, ref_output_folder):
    synth_output_folder.mkdir(parents=True, exist_ok=True)
    ref_output_folder.mkdir(parents=True, exist_ok=True)

    for fname in input_folder.glob('*.json'):
        print(f'Working on {fname}')
        with open(fname, 'r', encoding='utf-8') as file:
            lang = json.load(file)
            output_file = f"{fname.with_suffix('.html').name}"

            html_content = generate_synthesis_html(lang, output_file)
            with open(synth_output_folder / output_file, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
                print(f"Generated Synthesis HTML file: {synth_output_folder / output_file}")

            ref_html_content = generate_ref_html(lang, output_file)
            with open(ref_output_folder / output_file, 'w', encoding='utf-8') as ref_html_file:
                ref_html_file.write(ref_html_content)
            print(f"Generated Reference HTML file: {ref_output_folder / output_file}")
    print(lost_phonemes)

# Specify the folder containing template files and the output folder for HTML files
#input_folder = Path(sys.argv[1])
#synth_output_folder = Path('en/synth_inv')
#ref_output_folder = Path('en/ref_inv')
# Run the script to process all template files in the specified folder and save the HTML files in the output folder
#process_templates_from_folder(input_folder, synth_output_folder, ref_output_folder)
