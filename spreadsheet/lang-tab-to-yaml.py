#!/usr/bin/env python
# coding: utf-8

# # Process a language tab to yaml v. 2.0
# 
# This notebook collects language tabs from the SAPhon [Tupian Nasal Typology Input](https://docs.google.com/spreadsheets/d/1dvXFvLIV4y84CglgjAl-ZVb09IuGazs1SzFO_UJpmnI/edit#gid=1164878023) spreadsheet and creates version 2.0 yaml output.

import spreadsheet
import os, re, sys
import unicodedata
import requests
from pathlib import Path
import pandas as pd
import yaml
import json
from jsonschema import validate, Draft202012Validator
from jsonschema.exceptions import ValidationError, ErrorTree
import math

downloads = Path.home() / 'Downloads'
langdir = Path('./newlangs/')
langdir.mkdir(parents=True, exist_ok=True)
(langdir / 'json').mkdir(parents=True, exist_ok=True)
yamldir = Path('../langs')


# ## Get Tupian input spreadsheet lang tabs
# 
# Collect the language tabs from the input spreadsheet into a dataframe, one row per lang tab.

ssdf = pd.DataFrame.from_records(list(spreadsheet.langsheets.values()))
ssdf['tabname'] = list(spreadsheet.langsheets.keys())
ssdf['yaml'] = ssdf['short'] + '.yaml'
ssdf = ssdf[ssdf['include']].reset_index(drop=True).drop('include', axis='columns')
assert(~ssdf['gid'].duplicated().any())
assert(~ssdf['tabname'].duplicated().any())


# ## Download `.tsv` files (optional)
# 
# The next cell is optional to download all lang tabs from the spreadsheet. Set `do_download` to `True` and execute the cell to do this task. For active work on a lang tab this step is not necessary and time-consuming.


do_download = False
if do_download:
    for row in ssdf[ssdf['include']].itertuples():
        r = requests.get(f'{spreadsheet.puburl}/pub?gid={row.gid}&single=true&output=tsv')
        r.encoding = 'utf-8'
        with open(langdir / f'{row.short}.tsv', 'w', encoding='utf-8') as out:
            out.write(r.text)


# ## Function definitions
# 
# Functions used to create version 2.0 yaml, work in progress.

langre = re.compile(
    r'''
    (?P<name>[^\[]+)
    (?P<iso>\[[^\]]+\])?
    ''',
    re.VERBOSE
)

def _clean(s):
    '''
    Clean string of extraneous markup.
    '''
    if s != None:
        s = s.strip().strip('{').strip('}').strip('[').strip(']').strip()
    return s

def split_morph_ids(mids):
    morphs = []
    if mids is None or mids == '' or mids.lower().strip() == 'none':
        return []
    for mid in spreadsheet.parse_with_delims(mids):
        try:
            d = {
                'morpheme_id': mid[0],
                'morpheme_type': mid[1],
                'underlying_form': mid[2],
#                'surface_forms': spreadsheet.parse_with_delims(mid[3].strip('{').strip('}')),
                'surface_forms': [
                    unicodedata.normalize('NFD', c.strip()) \
                        for c in mid[3].strip('{').strip('}').split(',')
                ],
                'gloss': mid[4]
            }
        except Exception as e:
            msg = f'Could not parse morpheme ids: {mid}: {e}'
            raise RuntimeError(msg)
        morphs.append(d)
    return morphs

def alloprocs(allos, procs, phoneme):
    '''
    Return zipped allophones and processes extracted from allophone list.
    '''
    allolist = [_clean(a) for a in allos.split(',')]
    proclist = [_clean(p) for p in procs.split(',')]
    mapping = {a: [] for a in allolist}

    try:
        assert(len(proclist) > 0)
    except AssertionError:
        sys.stderr.write(f'Invalid entry for phoneme {phoneme}, must have at least one allophone and process\n') 
    if (len(allolist) == 1):
        mapping[allolist[0]] = proclist
    else:
        for proc in proclist:
            m = spreadsheet.procre.match(proc)
            pgd = m.groupdict()
            try:
                phone = pgd['phone'].replace('-', '')
            except AttributeError:
                sys.stderr.write(f'Process {proc} must have an allophone prefix\n')
                continue
            procname = pgd['procsubtype'] if pgd['tag'] is None else pgd['tag'] + pgd['procsubtype']
            try:
                assert(phone in mapping.keys())
                mapping[phone].append(procname)
            except AssertionError:
                sys.stderr.write(f'{proc} does not map to an allophone\n')
    for a, proclist in mapping.items():
        if a == phoneme:
            try:
                assert(proclist == [])
            except AssertionError:
                if proclist == ['preservation']:
                    pass
                else:
                    sys.stderr.write(f'Identity allophone {a} should not have a process\n')
        else:
            try:
                assert(len(proclist) > 0)
            except AssertionError:
                sys.stderr.write(f'Non-identity allophone {a} must name at least one process\n')
    return [{'allophone': k, 'processnames': v} for k, v in mapping.items()]
 

def tsv2newyaml(tsvfile, v1):
    '''
    Make a new YAML dict from a Tupian input spreadsheet tab.
    '''
    tsvlang = spreadsheet.read_lang(tsvfile, strict=False)
    natclasses, flatnatclasses, catsymb = spreadsheet.check_natclasses(tsvlang)
    allophones, alloprocs = spreadsheet.check_allophones(tsvlang, flatnatclasses)
    morph_id_map = spreadsheet.check_morpheme_ids(tsvlang)
    spreadsheet.check_procs(tsvlang, flatnatclasses, morph_id_map, catsymb, alloprocs)
    # TODO: remainder should be per-doc (synthesis, ref)
    langdoc = {'info': {}, 'synthesis': {}, 'sources': []}
    for doc in [tsvlang['synthesis']] + tsvlang['ref']:
        is_synthesis = 'synthesis' in doc.keys()
#        doc = tsvlang['synthesis']
#        if 'lang' not in doc.keys():
#            return (None, None, None)
        if is_synthesis:
            name = _clean(doc['lang'])
            if '[' in name:
                sys.stderr.write(f'Language name for {name} should be cleaned up.\n')
            try:
                notes = doc['notes']
            except KeyError:
                notes = 'None'
            try:
                glottocode = _clean(doc['glottocode'])
            except KeyError:
                sys.stderr.write(f'Lang {name} missing glottocode field.\n')
                glottocode = TODO
            try:
                altnames = [_clean(c) for c in doc['altnames'].split(',')]
            except KeyError:
                sys.stderr.write(f'Lang {name} missing alternate_names field.\n')
                altnames = [TODO]
            try:
                iso_codes = [_clean(c) for c in doc['iso_codes'].split(',')]
            except KeyError:
                sys.stderr.write(f'Lang {name} missing iso_codes field.\n')
                iso_codes = [TODO]
            if v1 == {}:
                v1 = {
                    'info': {
                        'short_name': 'TODO',
                        'alternate_names': 'TODO',
                        'family': 'TODO',
                        'countries': ['TODO'],
                        'coordinates': [],
                    },
                    'synthesis': {
                        'tone': False,
                        'laryngeal_harmony': False
                    }
                }
            try:
                langdoc['info'] = {
    #                'doctype': 'synthesis',
                      'name': name,
                      'short_name': v1['info']['short_name'],
                      'alternate_names': altnames,
                      'glottolog_code': glottocode,
                      'iso_codes': iso_codes,
                      'family': v1['info']['family'],
                      'countries': v1['info']['countries'],
                      'coordinates': v1['info']['coordinates'],
                      'notes': 'None'
                }
                langdoc['synthesis'] = {
                      'summary': doc['synthesis'],
                      'notes': notes,
                      'natural_classes': [{'symbol': nc[0], 'members': nc[1:]} for nc in natclasses['synthesis']],
                      'phonemes': phonlist(allophones['synthesis']),
                      'morphemes': split_morph_ids(doc['morph_ids']),
                      'processdetails': doc['processes'],
                 # TODO: following from v1 and not mentioned in new YAML draft
    #!            'allophones': v1['allophones'],
    #!            'nasal_harmony': v1['nasal_harmony'],
                      'tone': v1['synthesis']['tone'],
                      'laryngeal_harmony': v1['synthesis']['laryngeal_harmony'],
                }
            except Exception as e:
                sys.stderr.write(f'Problem with doc {doc}.\n')
                raise e
        else:
            langdoc['sources'].append(
                {
                      'summary': doc['summary'],
                      'citation': [doc['source']],
                      'natural_classes': [{'symbol': nc[0], 'members': nc[1:]} for nc in natclasses[doc['source']]],
                      'phonemes': phonlist(allophones[doc['source']]),
                      'morphemes': split_morph_ids(doc['morph_ids']),
                      'processdetails': doc['processes'],
                 # TODO: following from v1 and not mentioned in new YAML draft
    #!            'allophones': v1['allophones'],
    #!            'nasal_harmony': v1['nasal_harmony'],
                }
            )
# Filter None values out of list values.
#!    listflds = (
#!        'alternate_names', 'iso_codes',
#!        'countries', 'coordinates', 'natural_classes',
#!        'morphemes', 'phonemes', 'processes',
#!        'triggers', 'notes'
#!    )
#!    for fld in listflds:
#!        sdoc[fld] = [v for v in sdoc[fld] if v is not None]
    return (langdoc, tsvlang, allophones)

def proclist_old(processes):
    '''
    Return a `processdetails` list from spreadsheet `processes` section.
    '''
    deets = []
    for proc in processes:
        procname = proc['proc_name'] if not '-' in proc['proc_name'] else proc['proc_name'][proc['proc_name'].index('-')+1:]
        deet = {
            'processname': procname,
            'processtype': proc['proc_type'],
            'description': proc['description'],
            'optionality': proc['optionality'],
            'directionality': proc['directionality'],
            'alternation_type': proc['alternation_type']
        }
        for fld in 'undergoers', 'triggers':
            if proc[fld] == 'NA':
                deet[fld] = [['NA'], {'type': 'TODO', 'positional_restrictions': 'TODO'}]
            elif isinstance(proc[fld], dict):
                data = proc[fld][fld]
            else:
                print(f'PROC: {proc}')
                data = proc[fld][0][fld]
            try:
                deet[fld] = [
                    [_clean(f) for f in data.split(',')],
                    {
                        'type': 'TODO',
                        'positional_restrictions': 'TODO'
                    }
                ]
            except:
                print(f'failed for {fld}: "{proc[fld]}"')
        for new, old in ('transparent', 'transparencies'), ('opaque', 'opacities'):
            deet[new] = proc[old][old]
        deets.append(deet)
    return deets

def _clean_procname(p):
    if p is None:
        return 'TODO: got None'
    else:
        return _clean(p if '-' not in p else p[p.index('-')+1:])

def phonlist(allophones):
    '''
    Return a `phonemes` list from an `allophone` set.
    '''
    phonemes = {}
    for pset in allophones:
        d = {}
        if len(pset) == 5:
            seg = pset[0]
            envs = {'phoneme': f'STRING MAPPING: "{pset}"'}
            print(f'STRING MAPPING: "{pset}"')
            continue
        elif len(pset) == 4:
            phoneme, allos, _psetenv, proc = pset
            phoneme = unicodedata.normalize('NFD', phoneme)
            allophones = alloprocs(allos, proc, phoneme)
            envs = []
            for env in spreadsheet.parse_env(pset[2]):
                try:
                    env['allophones'] = allophones
                except:
                    print(env)
                envs.append(env)
        elif len(pset) == 2:
            phoneme, allos = pset
            phoneme = unicodedata.normalize('NFD', phoneme)
            envs = [{
                'preceding': '', # TODO: NA or other empty value here?
                'following': '', # TODO: NA or other empty value here?
                'allophones': [
                    {
                        'processnames': [],
                        'allophone': unicodedata.normalize('NFD', _clean(a))
                    } for a in allos.split(',')
                ]
            }]
        else:
            sys.stderr.write(f'Unexpected phoneme set length for "{pset}".')
            continue
        try:
            phonemes[phoneme]['environments'] += envs
        except KeyError:
            phonemes[phoneme] = {'phoneme': phoneme, 'environments': envs}
    # TODO: sort phonemes
    return list(phonemes.values())

def yaml2newyaml(v1):
    '''
    Copy a version 1 YAML dict into version 2.
    '''
    sdoc = {
#        'doctype': 'synthesis',
        'info': {
          'name': v1['name'],
          'short_name': v1['short_name'],
          'alternate_names': v1['alternate_names'],
#          'glottolog_code': v1['name'], # TODO: new, check by hand
          'iso_codes': v1['iso_codes'],
#          'glottolog_codes': [], # TODO: new, need to be added by hand
          'family': v1['family'],
          'countries': v1['countries'],
          'coordinates': v1['coordinates'],
          'notes': v1['notes'], # TODO: not mentioned in new YAML draft
        },
        'synthesis': {
          'natural_classes': [], # TODO: new
          'morphemes': [], # TODO: new?
          'phonemes': [{'phoneme': p} for p in v1['phonemes']],
          'processdetails': [], # TODO: new?
          'triggers': [], # TODO: new?
          'transparent': [], # TODO: new?, include?
          'opaque': [], # TODO: new?, include?
         # TODO: following from v1 and not mentioned in new YAML draft
          'allophones': v1['allophones'],
          'nasal_harmony': v1['nasal_harmony'],
          'tone': v1['tone'],
          'laryngeal_harmony': v1['laryngeal_harmony'],
        }
    }
    # Filter None values out of list values.
    infolistflds = (
        'alternate_names', 'iso_codes', 
        'countries', 'coordinates', 'notes'
    )
    for fld in infolistflds:
        sdoc['info'][fld] = [v for v in sdoc['info'][fld] if v is not None]
    synthlistflds = ('natural_classes',
        'morphemes', 'phonemes', 'processdetails',
        'triggers'
    )
    for fld in synthlistflds:
        sdoc['synthesis'][fld] = [v for v in sdoc['synthesis'][fld] if v is not None]
    return sdoc

TODO = 'TODO'

def ss2refdoc(lang):
    pass

def ss2synthdoc(lang):
    '''
    Produce a synthesis yaml doc from a lang from the input spreadsheet.
    '''
    synth = lang['synthesis']
    langm = re.match(langre, synth['lang'])
    yd = {
        'doctype': 'synthesis',
        'name': langm['name'].strip(),
        'short_name': TODO,
        'alternate_names': TODO,
        'iso_codes': langm['iso']
    }
    return yd


# ## Read `.tsv` and v1 `.yaml` files
# 
# Download, read, and process lang tabs (and existing v. 1 yaml files, if they exist). Set one or more tab indexes in `rng` to be checked for errors. Set `use_cached` to `True` if you want to use a previously-downloaded `.tsv` file instead of downloading from the input spreadsheet.

nosynthesis = [
    12,
    21,
    25,
    32,
    35,
    37,
    43,
    44,
    47,
    48,
    50, # Siriono
    51,
    54, # Tapirapé
    57,
    63,
    65,
    67
]


with open('../saphonlang.schema.json', 'r') as sh:
    schema = json.load(sh)
validator = Draft202012Validator(schema)

use_cached = False
langs = {}
rng = [n for n in range(0, 67) if n not in nosynthesis]
print(f'Working on {len(rng)} lang tabs')
myerror = None
for row in ssdf.iloc[rng].itertuples():
    if (yamldir / row.yaml).exists():
        with open(yamldir / row.yaml, 'r', encoding='utf-8') as fh:
            v1docs = list(yaml.safe_load_all(fh))
            if math.isnan(v1docs[0]['coordinates'][0]['elevation_meters']):
                v1docs[0]['coordinates'][0]['elevation_meters'] = 'Unspecified'
        v1synth = yaml2newyaml(v1docs[0])
    else:
        v1synth = {}
    
    tsvfile = langdir / f'{row.short}.tsv'
    if use_cached is not True or not tsvfile.exists():
        print(f"Requesting '{row.tabname}' lang tab from index {row.Index} and caching at {tsvfile}.")
        r = requests.get(f'{spreadsheet.puburl}/pub?gid={row.gid}&single=true&output=tsv')
        r.encoding = 'utf-8'

        with open(tsvfile, 'w', encoding='utf-8') as out:
            # Replace Windows CRLF with Unix LF
            text = r.content.replace(b'\r\n', b'\n').decode('utf8')
            out.write(text)
    else:
        print(f"Reading from cached file {tsvfile} ({row.Index}).")
    try:
        v2synth, tsvlang, allophones = tsv2newyaml(tsvfile, v1synth)
        if tsvlang == None:
            sys.stderr.write(f'Skipping .json creation for {row.tabname}.\n\n')
            continue
    except Exception as e:
        v2synth = {}
        print(f'\n\nERROR: spreadsheet tab {row.tabname} failed.\n{e}\n\n')
#        raise e
        continue
    langs[row.short] = {
        'v1synth': v1synth,
        'v2synth': v2synth,
        'tsv': tsvlang['synthesis']
    }
    try:
        langjson = langdir / 'json' / f'{row.short}.json'
        with open(langjson, 'w', encoding='utf8') as out:
            json.dump(langs[row.short]['v2synth'], out, indent=2, ensure_ascii=False)
        print(f'Dumped json {row.short}.json')
    except Exception as e:
        sys.stderr.write(f'Failed to dump json {row.short}.json.\n')
    try:
        with open(langjson, 'r') as jh:
            langobj = json.load(jh)
#            tree = ErrorTree(validator.iter_errors(langobj))
            validate(instance=langobj, schema=schema)
    except ValidationError as e:
        myerror = e
        print(f'In json file {langjson}\njson path {e.json_path}\ngot value "{e.instance}"\nexpected {e.validator_value}')
