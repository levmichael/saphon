# -*- coding: utf-8 -*-

import sys
import re
import yaml
import pandas as pd
sys.path.append('..')
from python.saphon.io import YAMLLang, normalizeIPA, readFeatList
from vocab import natcat, proc_vocab

# Get allowed phoneme symbols.
featInfo = readFeatList('../resources/ipa-table.txt')
allowed_phon = featInfo.order()

# Process regex
procre = re.compile(
    r'(?P<tag>(MPP|XMP|XWP)=)?(?P<phone>[^-]+-)?(?P<procsubtype>(?P<proc>[^:]+)(?P<subtype>:.+)?)'
)

# Map spreadsheet field names to yaml field names.
# TODO: yaml field names are not yet defined and need to match the yaml standard
fields = {
    'lang_md': {
        'synthesis': 'synthesis',           # TODO: synthesis only
        'date completed': 'date_completed', # TODO: synthesis only 
        'language': 'lang',
        'source': 'source',                 # TODO: ref only
        'data inputter': 'data_inputter',
        'summary': 'summary',
        'notes': 'notes',
        'include in saphon': 'include_in_saphon'
    },
    'phon_md': {
        'natural classes': 'natclass',      # TODO: tapiete uses 'natural classes' in synth doc, and mbya uses 'segments'
        'segments': 'natclass',
        'allophones': 'allophones',
        'page numbers': 'allo_page_num', # subfield of 'allophones'
        'analytical framework': 'analytical_framework',
        'morpheme ids': 'morph_ids'
    },
    'proc_md': {
        'page numbers': 'page_num',
        'process name': 'proc_name',
        'process type': 'proc_type',
        'prose description': 'description',
        'optionality': 'optionality',
#        'optioanlity': 'optionality',
        'prose descrption': 'description',
        'directionality': 'directionality',
        'domain': 'domain',
        'alternation type': 'alternation_type',
        'transparencies': 'transparencies',
        'opacities': 'opacities',
    },
    'proc_md_sub': {   # subfields for triggers/undergoers
        'undergoers': 'undergoers',
        'triggers': 'triggers',   # can be repeated
        'type': 'type',
        'morpheme class': 'morph_class',
        'morpheme ids': 'morph_ids', # also in phon_md
        'positional restriction wrt constituent': 'wrt', # Undergoers only
        'location of trigger wrt domain': 'wrt'  # Triggers only
    }
}

def read_lang(infile):
    '''
    Read a language's input data from a .tsv file.

    Returns
    -------

    lang: dict
    Dictionary of docs for a language. The keys are doc identifiers (ref source or 'synthesis'), and
    the values are dicts of doc metadata.
    '''
    text = ''
    with open(infile, 'r', encoding='utf-8') as fh:
        text = fh.read()
    docs = re.split('Doctype:\s*\t', text)[1:]  # Element 0 is an empty string

    lang = {'synthesis': {}, 'ref': [] }
    for d in docs:
        if d.startswith('Reference'):
            lang['ref'].append(parse_doc(d))
        elif d.startswith('Synthesis'):
            lang['synthesis'] = parse_doc(d)
        else:
            raise RuntimeError("Unrecognized document type. Must be 'Reference' or 'Synthesis'.")
    if lang['synthesis'] == {}:
        sys.stderr.write(f'No synthesis found in lang file {infile}.\n')
    if lang['ref'] == []:
        sys.stderr.write(f'No ref docs found in lang file {infile}.\n')
    return lang

def parse_md(lines, fmap):
    '''
    Parse metadata from a section of text lines.

    Returns
    -------
    d: dict
    A dictionary in which the keys are the first tab-separated element from each
    line, and the line remainders are the dict values.
    '''
    d = {}
    for l in lines:
        try:
            k, v = l.split('\t', 1)
        except Exception as e:
            sys.stderr.write(f"Could not split line '{l}': {e}\n\n")
            continue
        k = k.strip().strip(':').lower()
        try:
            d[fmap[k]] = v
        except KeyError:
            sys.stderr.write(f"No match for field '{k}'. Parse possibly incorrect.")
    return d

def parse_proc(t, fmap, fmap_sub):
    '''
    Parse metadata from a section of process text lines.

    Returns
    -------

    d: dict
    A dictionary in which the keys are the process field names and the values are the
    line remainders.
    '''
    d = {}
    if t == '':
        return d
    undergoers = {}  # single undergoer per process
    triggers = []    # multiple triggers per process
    trigger = {}     # a single trigger
    subtype = ''
    for l in t.split('\n'):
        k = ''
        try:
            k, v = l.split('\t', 1)
        except Exception as e:
            if l.strip() != '':
                sys.stderr.write(f"Could not split line '{l}': {e}\n\n")
            continue
        k = k.strip().strip(':').lower()
        try:
            fld = fmap[k]
            curdict = d
        except KeyError:
            try:
                fld = fmap_sub[k]
            except KeyError:
                sys.stderr.write(f"No match for field '{k}'. Parse possibly incorrect.\n")
            if fld == 'undergoers':
                curdict = undergoers
            elif fld == 'triggers':
                if trigger != {}:
                    triggers.append(trigger)
                    trigger = {}
                curdict = trigger
        curdict[fld] = v
    d['undergoers'] = undergoers
    d['triggers'] = triggers
    triggers.append(trigger)
    return d
        
def parse_doc(d):
    '''
    Parse a language document, either a ref source doc or synthesis doc.

    Returns
    -------
    d: dict
    A dictionary of doc metadata combining the general language metadata,
    phon inventory metadata, and process metadata.
    '''
    # 1. Remove all indentation at the beginning of a line.
    # 2. Reduce multiple consecutive tabs to a single tab.
    # 3. Remove line-final tabs.
    d = re.sub(r'^\t+', '', d, flags=re.MULTILINE)
    d = re.sub(r'\t\t+', '\t', d)
    d = re.sub(r'\t$', '', d, flags=re.MULTILINE)
    d = re.sub(f'\n\s*\n', '\n\n', d, flags=re.MULTILINE)
    sections = d.split('\n\n')
    lang_md = parse_md(sections[0].split('\n')[1:], fields['lang_md'])
    phon_md = parse_md(sections[1].split('\n'), fields['phon_md'])
    proc_md = []
    for s in sections[2:]:
        d = parse_proc(s, fields['proc_md'], fields['proc_md_sub'])
        if d != {}:
            proc_md.append(d)
    return lang_md | phon_md | {'processes': proc_md}

def delim_iter(line, opendelim='{', closedelim='}'):
    '''
    Return an Iterator that successively returns indexes into delimited content
    found in a line.
    
    Yields
    ------
    A tuple of:
    
    openpos: integer
    The integer index of the opening delimiter.
    
    closepos: integer
    The integer index of the closing delimiter.
    
    level: integer
    Nesting depth of the delimiters indexed by openpos and closepos.
    
    Example
    -------
    
    The string '{{a}}' would yield (0, 4, 0) and (1, 3, 1).
    '''
    stack = []
    for m in re.finditer(r'[{}{}]'.format(opendelim, closedelim), line):
        pos = m.start()
        if line[pos-1] == '\\':
            # skip escape sequence
            continue

        c = line[pos]

        if c == opendelim:
            stack.append(pos+1)

        elif c == closedelim:
            if len(stack) > 0:
                prevpos = stack.pop()
                yield (prevpos, pos, len(stack))
            else:
                # error
                raise RuntimeError(
                    f"encountered extraneous closing quote at pos {pos}: '{line[pos:]}'"
                )

    if len(stack) > 0:
        for pos in stack:
            raise RuntimeError(
                f"expecting closing quote to match open quote starting at: '{line[pos-1:]}'"
            )

def split_outside_delims(line, splitter=',', opendelim='{', closedelim='}'):
    '''
    Split string on `splitter` if not between delimiters. This preserves delimited strings
    containing `splitter` that are embedded in a line.

    Returns
    -------

    splits: list
    A list of strings found by splitting on `splitter`. Delimited strings that contain
    `splitter` are preserved without splitting internally.
    '''
    delims = []
    for openpos, closepos, _ in delim_iter(line, opendelim=opendelim, closedelim=closedelim):
        delims.append([openpos, closepos])

    splitpos = []
    for m in re.finditer(r'[{}]+'.format(splitter), line):
        add_split = True
        pos = m.start()
        for d in delims:
            if pos >= d[0] and pos <= d[1]:
                add_split = False
                break
        if add_split is True:
            splitpos.append(pos)
    splits = []
    last = None
    for i, p in enumerate(splitpos):
        first = 0 if i == 0 else splitpos[i-1]+1
        last = splitpos[i]
        splits.append(line[first:last].strip())
    if last is not None:
        splits.append(line[last+1:].strip())
    return splits

def parse_with_delims(s):
    '''
    Parse a string that may contain delimiters into its constituents.

    Returns
    -------

    splits: list
    A list of substrings split on ','. Substrings delimited by '{}' are preserved whole,
    and no split occurs on a ',' internal to a delimited substring.
    '''
    # Ensure first/last delimiters of are at level 0.
    s = re.sub(r'^{{+', '{', s)
    s = re.sub(r'}}+$', '}', s)
    splits = []
    for openpos, closepos, level in delim_iter(s):
        if level == 0:
            tpl = s[openpos:closepos]
            splits.append(split_outside_delims(tpl))
    if splits == []:
        return [s]
    else:
        return splits
    

def check_procs(l, natclass_map, morph_id_map, catsymb, alloprocs):
    '''Check processes for each doc.'''
    for doc in [l['synthesis']] + l['ref']:
        if doc == {}:
            continue
        docid = 'synthesis' if 'synthesis' in doc else doc['source']
        ids = natclass_map[docid] + morph_id_map[docid] + catsymb[docid]
        for proc in doc['processes']:
            m = re.match(procre, proc['proc_type'])
            try:
                assert(m is not None)
            except AssertionError:
                msg = f'Could not parse proc_type {proc["proc_type"]}) ' \
                      f'for {docid}\n\n'
                sys.stderr.write(msg)
            try:
                assert(m.group('proc') in proc_vocab)
            except AssertionError:
                msg = f'Process type {m.group("proc")} (from {proc["proc_type"]}) not in proc_vocab ' \
                      f'for {docid}\n\n'
                sys.stderr.write(msg)
            try:
                proc_name = f'{m.group("tag") or ""}{m.group("phone") or ""}{m.group("proc")}'
                assert(
                    proc['proc_name'].startswith(proc_name + ':') or
                    proc['proc_name'] == proc_name
                )
            except AssertionError:
                msg = f'Process type {proc["proc_name"]} does not match type {m.group("proc")} (from {proc["proc_type"]}) ' \
                      f'for {docid}\n\n'
                sys.stderr.write(msg)
            try:
                assert(proc['proc_name'] in alloprocs[docid])
            except AssertionError:
                msg = f'Process name {proc["proc_name"]} not used by any allophones ' \
                      f' for {docid}\n\n'
                sys.stderr.write(msg)
            for fld in ['transparencies', 'opacities', 'undergoers']:
                if fld == 'undergoers':
                    try:
                        vals = [
                            k for k in split_outside_delims(
                                proc[fld][fld].strip(), splitter='\s,', opendelim='(', closedelim=')'
                            ) if (not k.startswith('(')) and (not k.endswith(')'))
                        ]
                    except Exception as e:
                        msg = f"Error in Undergoers '{proc[fld][fld].strip()}'. " \
                              f" for {docid}\n"
                        sys.stderr.write(msg)
                        print(e, file=sys.stderr)
                        sys.stderr.write('\n')
                    v = proc[fld][fld].strip()
                else:
                    vals = [k.strip() for k in proc[fld].strip().split(',')]
                    v = proc[fld].strip()
                if v in ['NA', 'None', 'Uncertain', 'Unspecified']:
                    try:
                        assert(v != 'Uncertain' or docid == 'synthesis')
                        assert(v != 'Unspecified' or docid != 'synthesis')
                    except AssertionError:
                        allowed_type = 'ref' if docid == 'synthesis' else 'synthesis'
                        msg = f"{fld} value '{v}' allowed only in {allowed_type} " \
                              f"'{', '.join(ids)}' for {docid}\n\n"
                        sys.stderr.write(msg)
                    try:
                        assert(v != 'None' or m.group('proc') in ('LDNH', 'LDOH', 'LNsyll') )
                    except AssertionError:
                        msg = f"{fld} value '{v}' allowed only for procs 'LDNH', 'LDOH', 'LNsyll' " \
                              f"'{', '.join(ids)}' for {docid}\n\n"
                        sys.stderr.write(msg)
                    try:
                        assert(v != 'NA' or m.group('proc') in ('LN', 'LO', 'BN', 'BO', 'SN', 'SO', 'LNsyll', 'hnasalization') )
                    except AssertionError:
                        msg = f"{fld} value '{v}' allowed only for procs 'LN', 'LO', 'BN', 'BO', 'SN', 'SO', 'LNsyll', 'hnasalization' " \
                              f"'{', '.join(ids)}' for {docid}\n\n"
                        sys.stderr.write(msg)
                    continue
                for s in vals:
                    s = s.strip()
                    try:
                        assert(normalizeIPA(s) in ids)
                    except AssertionError:
                        msg = f"{fld} value '{s}' ({s.encode('utf8')}) not in Natural Classes/Segments/Morpheme IDs " \
                              f"'{', '.join(ids)}' for {docid}\n\n"
                        sys.stderr.write(msg)

def check_morpheme_ids(l):
    '''
    Check morph_id field for each doc and verify that it is a 5-ple or 'None'.

    Returns
    -------

    morph_ids: dict of lists
    A dictionary in which the keys are a doc identifier, and the values are the list of morph ID
    identifiers (the first element of a Morph ID set) found in the doc.
    '''
    morph_ids = {}
    for doc in [l['synthesis']] + l['ref']:
        if doc == {}:
            continue
        docid = 'synthesis' if 'synthesis' in doc else doc['source']
        doc_morph_ids = []
        try:
            mid2check = parse_with_delims(doc['morph_ids'])
        except Exception as e:
            msg = f"Error in Morpheme IDs list {doc['morph_ids']}. " \
                  f" for {docid}\n"
            sys.stderr.write(msg)
            print(e, file=sys.stderr)
            sys.stderr.write('\n')
        for m_id in mid2check:
            if isinstance(m_id, str):
                try:
                    assert(m_id.strip() == 'None')
                except AssertionError:
                    msg = f"Expected 5-ple or 'None' for morph_id. Got string '{m_id}' " \
                          f"for {docid}\n\n"
                    sys.stderr.write(msg)
                continue
            try:
                assert(isinstance(m_id, list))
                assert(len(m_id) == 5)
            except AssertionError:
                msg = f"Expected 5-ple for morph_id. Got {len(m_id)}-ple '{m_id}' " \
                      f"for {docid}\n\n"
                sys.stderr.write(msg)
            doc_morph_ids.append(normalizeIPA(m_id[0].strip()))
        morph_ids[docid] = doc_morph_ids
    return morph_ids

def check_char(c):
    '''
    Check the validity of a phon character.

    Returns
    -------
    c: str
    The character in its normalized form.
    '''
    if c.strip().startswith('//') and c.strip().endswith('//'):
        return c.strip()  # Ad-hoc reference-specific archiphoneme; do not check for validity.
    else:
        c = normalizeIPA(c.strip())
    try:
        # c must be in ipa-table.txt (allowed_phon) or must be an integer (tone value)
        assert(c in allowed_phon or c.isdigit())
    except AssertionError:
        sys.stderr.write(f'Character {c} ({c.encode("utf-8")}) is not in ipa-table.txt.\n\n')
    return c

def check_natclass(nc):
    '''
    Check a single Natural Class set, e.g. "{T, p, t, k}".

    Returns
    -------

    clean: list of lists
    List of lists of normalized phone symbols. Each inner list has the natural class category
    symbol as its first element, and the remaining elements are the phone symbols.

    flat: list
    A flattened list of all normalized phone symbols.

    catsymb: str
    The category symbol of the natural class, e.g. 'T'.
    '''
    clean = []
    flat = []
    try:
        symb = normalizeIPA(nc[0].strip().strip('/'))  # Remove '//' from archiphonemes.
        assert(symb in natcat)
        clean.append(normalizeIPA(nc[0].strip()))
    except AssertionError:
        sys.stderr.write(f'Natural Class symbol "{nc[0]}" not recognized.\n\n')
    for el in nc[1:]:
        if el.startswith('{') and el.endswith('}'):
            clean.append('{' + ', '.join([check_char(c) for c in el[1:-1].split(',')]) + '}')
            flat.extend([check_char(c) for c in el[1:-1].split(',')])
        else:
            clean.append(check_char(el))
            flat.append(check_char(el))
    return (clean, flat, nc[0])

def check_allophones(l, flatnatclasses):
    '''
    Check the allophone pairs of each doc and verify that the first member of each pair is
    in the doc's Natural Classes or Segments list.
    '''
    docallo = {}
    docprocs = {}
    for doc in [l['synthesis']] + l['ref']:
        if doc == {}:
            continue
        docid = 'synthesis' if 'synthesis' in doc else doc['source']
        proc_names = proc_vocab
        for p in doc['processes']:
            try:
                proc_names.append(p['proc_name'])
            except KeyError:
                continue
        natclass = flatnatclasses[docid]
        
        allophones = []
        procs = []
        try:
            allos2check = parse_with_delims(doc['allophones'])
        except Exception as e:
            msg = f"Error in allophone list {doc['allophones']}. " \
                  f"'{', '.join(natclass)}' for {docid}\n"
            sys.stderr.write(msg)
            print(e, file=sys.stderr)
            sys.stderr.write('\n')
        for a in allos2check:
            try:
                assert(normalizeIPA(a[0]) in natclass)
            except AssertionError:
                msg = f"Allophone '{a[0]}' ({a[0].encode('utf8')}) not in Natural Classes/Segments " \
                      f"'{', '.join(natclass)}' for {docid}\n\n"
                sys.stderr.write(msg)
            try:
                assert(len(a) in [2, 4, 5])
            except AssertionError:
                msg = f"Expected 2-ple, 4-ple, or 5-ple for allophones. Got {len(a)}-ple '{a}' " \
                      f"for {docid}\n\n"
                sys.stderr.write(msg)
            if len(a) in (4, 5):
                outputs = [c.strip() for c in a[1].strip('{').strip('}').split(',')]
                if len(a) == 5:
                    try:
                        assert(a[2].startswith('/') and a[2].endswith('/'))
                    except AssertionError:
                        msg = f"Allophone string mapping input value '{a[2]}' must be enclosed by '/'" \
                              f" for {docid}\n\n"
                        sys.stderr.write(msg)
                aproc = a[-1].strip()
                # aproc can be a list of process names, so process list if necessary and
                # check each value separately.
                if aproc.startswith('{') and aproc.endswith('}'):
                    procs2check = aproc[1:-1].split(',')
                else:
                    procs2check = [aproc]
                for pn in procs2check:
                    pn = pn.strip()
                    procs.append(pn)
                    try:
                        m = re.match(procre, pn)
                        assert(m is not None)
                        assert(m.group('proc') in proc_names)
                        if m.group('phone') is not None and m.group('phone') != '':
                            procs.append(m.group('proc'))
                            if m.group('tag') is not None and m.group('tag') != '':
                                procs.append(m.group('tag') + m.group('proc'))
                            if m.group('subtype') is not None and m.group('subtype') != '':
                                procs.append(m.group('procsubtype'))
                                if m.group('tag') is not None and m.group('tag') != '':
                                    procs.append(m.group('tag') + m.group('procsubtype'))
                    except AssertionError:
                        msg = f"Allophone proc_name '{pn.strip()}' does not match available Process names " \
                              f"'{', '.join(proc_names)}' for {docid}\n\n"
                        sys.stderr.write(msg)
                    if m.group('phone') is not None:
                        phone = m.group('phone').replace('-', '')
                        try:
                            assert(phone in outputs)
                        except AssertionError:
                            msg = f'Phone "{phone}" ({phone.encode("utf8")}) in allophone process {pn} does not match any allophone ouptuts in "{outputs}" ' \
                                  f' for {docid}\n\n'
                            sys.stderr.write(msg)
            allophones.append(a)
        docallo[docid] = allophones
        docprocs[docid] = procs
    return (docallo, docprocs)

def check_natclasses(l):
    '''
    Check the Natural Classes sets of each doc, e.g. "{T, p, t, k}, {N, m, n}, {V, i, e, a, u, o}".

    Returns
    -------

    A tuple of:

    docnatclasses: dict of lists of lists
    A dictionary in which the keys are doc identifiers and the values are the lists of natural
    class sets in the doc. Each set is a list of category symbol and normalized phon symbol, e.g.
    {
      'synthesis': [
        ['T', 'p', 't', 'k'],
        ['N', 'm', 'n'],
        ['V', 'i', 'e', 'a', 'u', 'o']
      ],
      'refsource...': [
        ...
      ]
    }

    docflatnatclasses: dict of lists
    A dictionary in which the keys are doc identifiers and the values are the flattened lists
    of normalized phon symbols in the doc, e.g.
    {
      'synthesis': ['p', 't', 'k','m', 'n', 'i', 'e', 'a', 'u', 'o'],
      'refsource...': [...]
    }

    doccatsymb: dict of lists
    A dictionary in which the keys are doc identifiers and the values are the flattened lists
    of category symbols in the doc, e.g.
    {
      'synthesis': ['T', 'N', 'V'],
      'refsource...': [...]

    }
    '''
    docnatclasses = {}
    docflatnatclasses = {}
    doccatsymb = {}
    for doc in [l['synthesis']] + l['ref']:
        if doc == {}:
            continue
        docid = 'synthesis' if 'synthesis' in doc else doc['source']
        nclasses = []
        flats = []
        catsymb = []
        try:
            nc2check = parse_with_delims(doc['natclass'])
        except Exception as e:
            msg = f"Error in Natural Class list {doc['natclass']}. " \
                  f" for {docid}\n"
            sys.stderr.write(msg)
            print(e, file=sys.stderr)
            sys.stderr.write('\n')
        for nclass in nc2check:
            nc = check_natclass(nclass)
            nclasses.append(nc[0])
            flats.extend(nc[1])
            catsymb.append(nc[2])
        docnatclasses[docid] = nclasses
        docflatnatclasses[docid] = flats
        doccatsymb[docid] = catsymb
    return (docnatclasses, docflatnatclasses, doccatsymb)

def read_procmap(procfile='proc_defs.tsv'):
    '''
    Read the `proc_defs.tsv` file derived from Jasper's spreadsheet for
    updating process names in allophone lists.
    '''
    return pd.read_csv(
        procfile,
        sep='\t',
        encoding='utf-8',
        header=None, names=('code', 'suggested'),
        dtype={'code': str, 'suggested': str}
    )

def get_allophone_df(lang, doc):
    '''
    Return the allophones list from a language doc as a dataframe.

    Parameters
    -------

    lang: a lang dict as returned by read_lang()
    doc: 'synthesis' or integer index of source doc as found in
         lang['ref']
    Returns
    -------

    allodf: dataframe of phone, allophone, env, process columns
    msg: string detailing which lang and doc were selected
    '''
    if doc == 'synthesis':
        allostr = lang['synthesis']['allophones']
        lname = lang['synthesis']['lang']
        doctype = ''
        src = 'synthesis'
    else:
        allostr = lang['ref'][int(doc)]['allophones']
        lname = lang['ref'][int(doc)]['lang']
        doctype = 'ref '
        src = lang['ref'][int(doc)]['source']
    try:
        df = pd.DataFrame.from_records(
            [a for a in parse_with_delims(allostr)],
            columns=['phone', 'allophone', 'env', 'proc']
        ).fillna('')
    except ValueError:
        # 'String mapping' 5-tuple. The third column should really be
        # 'input' for these, but we call it 'env' for consistency with
        # non-string mapping allophone sets.
        df = pd.DataFrame.from_records(
            [a for a in parse_with_delims(allostr)],
            columns=['phone', 'allophone', 'env', 'output', 'proc']
        ).fillna('')
    return \
        df, \
        f"""
You have selected allophones for:
  language: {lname}
  {doctype}document: {src}
  allophones to be merged: {allostr}
"""

def parse_allo_proc(s):
    '''
    Parse the allophone list from Jasper's text file that contains
    suggested new process names identified by id numbers.
    '''
    # Move proc numbers from outside of delimiter '{' to inside so that they
    # don't get dropped by parse_with_delims().
    s = re.sub(r'#?(?P<procnum>\d+){', '{' + '\g<procnum>', s)

    newprocdf = pd.DataFrame.from_records(
        [a for a in parse_with_delims(s.strip())],
        columns=['numphone', 'allophone', 'env', 'proc']
    ).fillna('')
    newprocdf = pd.concat(
        [
            newprocdf,
            newprocdf['numphone'].str.extract(r'(?P<procid>\d*)(?P<phone>.+)')
        ],
        axis='columns'
    ).drop('numphone', axis='columns')[['phone', 'allophone', 'env', 'proc', 'procid']]
    return newprocdf.merge(
        read_procmap(),
        how='left',
        left_on='procid',
        right_on='code'
    ).drop('code', axis='columns').fillna('')

def merge_allo_with_suggestions(allodf, allo_newproc):
    '''
    Merge allophone dataframe from a lang doc with new process names as
    suggested in Jasper's text file. Return as a new dataframe.
    '''
    newprocdf = parse_allo_proc(allo_newproc)
    mergedf = pd.merge(
        allodf,
        newprocdf,
        how='outer',
        on=('phone', 'allophone', 'env'),
        suffixes=('_orig', '_newproc')
    ).fillna('')
    mergedf['determined'] = mergedf['suggested']
    mergedf.loc[mergedf['determined'] == '', 'determined'] = mergedf.loc[mergedf['determined'] == '', 'proc_orig']
    return mergedf
