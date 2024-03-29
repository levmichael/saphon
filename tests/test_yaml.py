#!/usr/bin/env python

import glob
import math
import yaml
from python.saphon.io import YAMLLang, normalizeIPA, readFeatList


def check_dictfld(fld, d):
    '''Check that a dict key exists and its value is not None.'''
    try:
        assert(d[fld] is not None)
    except AssertionError:
        raise AssertionError(f'Field `{fld}` must have an explicit value.')
    except KeyError:
        raise AssertionError(f'Field `{fld}` is missing.')


def assert_boolean(fld, d):
    '''Check a dict's boolean field for correctness.'''
    check_dictfld(fld, d)
    try:
        assert(isinstance(d[fld], bool))
    except AssertionError:
        raise AssertionError(f'Field `{fld}` value must be `True` or `False`.')


def assert_strfld(fld, d):
    '''Check a dict's string field for correctness.'''
    check_dictfld(fld, d)

    try:
        assert(d[fld].strip() != '')
    except AssertionError:
        raise AssertionError(f'Field `{fld}` must be non-empty.')


def check_strlist(fld, d):
    '''Check a list of strings in a dict value.'''
    check_dictfld(fld, d)
    for val in d[fld]:
        if val is None:
            continue
        try:
            assert(val.strip() != '')
        except AssertionError:
            raise AssertionError(f'Values in `{fld}` field must be non-empty.')


def check_graphemes2phonemes(doc, lang):
    '''Check graphemes2phonemes values.'''
    check_dictfld('graphemes2phonemes', doc)
    for mapping in doc['graphemes2phonemes']:
        if mapping is None:
            continue
        assert_strfld('grapheme', mapping)
        assert_strfld('phoneme', mapping)
        try:
            assert mapping['phoneme'] in lang.synthesis['phonemes']
        except AssertionError:
            raise AssertionError(
                f"Phoneme '{mapping['phoneme']}' for grapheme '{mapping['grapheme']}' does not match a value in the language 'phonemes' list."
            )


def check_ref_allophones(doc):
    '''Check ref_allophones values.'''
    check_dictfld('ref_allophones', doc)
    for mapping in doc['ref_allophones']:
        if mapping is None:
            continue
        assert_strfld('grapheme_allophone', mapping)
        assert_strfld('grapheme_phoneme', mapping)


def check_allophones(doc, lang):
    '''Check allophones values.'''
    check_dictfld('allophones', doc)
    for mapping in doc['allophones']:
        if mapping is None:
            continue
        assert_strfld('allophone', mapping)
        assert_strfld('phoneme', mapping)
        try:
            assert mapping['phoneme'] in lang.synthesis['phonemes']
        except AssertionError:
            raise AssertionError(
                f"Phoneme '{mapping['phoneme']}' for allophone '{mapping['allophone']}' does not match a value in the language 'phonemes' list."
            )


def check_coordinates(doc):
    '''Check coordinates values.'''
    check_dictfld('coordinates', doc)
    for mapping in doc['coordinates']:
        if mapping is None:
            continue
        for fld, max, min in (('latitude', 90, -90), ('longitude', 180, -180)):
            try:
                assert((mapping[fld] >= min) and (mapping[fld] <= max))
            except (AssertionError, TypeError):
                raise AssertionError(
                    f'Field `{fld}` must be in the range [{min} {max}]'
                )
            except KeyError:
                raise AssertionError(f'Field `{fld}` is missing.')
        try:
            assert(
                isinstance(mapping['elevation_meters'], int) or
                math.isnan(mapping['elevation_meters'])
            )
        except (AssertionError, TypeError):
            raise AssertionError(
                'Field `elevation_meters` must be an int or `.NAN` if unknown.'
            )
        except KeyError:
            raise AssertionError('Field `elevation_meters` missing.')


def check_ref(doc, lang):
    '''Check a `ref` document for correctness.'''
    assert_strfld('citation', doc)
    check_graphemes2phonemes(doc, lang)
    check_ref_allophones(doc)
    check_strlist('ref_notes', doc)


def check_synthesis(doc, lang):
    '''Check a `synthesis` document for correctness.'''
    assert_strfld('name', doc)
    assert_strfld('short_name', doc)
    check_strlist('alternate_names', doc)
    check_strlist('iso_codes', doc)
    assert_strfld('family', doc)
    check_strlist('countries', doc)
    check_coordinates(doc)
    check_strlist('phonemes', doc)
    check_allophones(doc, lang)
    assert_boolean('nasal_harmony', doc)
    assert_boolean('tone', doc)
    assert_boolean('laryngeal_harmony', doc)
    check_strlist('notes', doc)


def check_phonemes(phonemes, allowed):
    '''Check the `phonemes` list for bad values.'''
    err = ''
    for p in phonemes:
        try:
            allowed[normalizeIPA(p)]
        except KeyError as e:
            err += f'\nUnrecognized phoneme "{e.args[0]}".'
    if err != '':
        raise RuntimeError(err + '\n')

def docs_by_doctype(docs):
    '''Return synthesis and ref docs separately.'''
    synth = None
    refs = []
    for doc in docs:
        try:
            assert(doc['doctype'] in ('synthesis', 'ref'))
        except AssertionError:
            raise AssertionError(f"Unrecognized doctype \'{doc['doctype']}\'")
        except KeyError:
            raise AssertionError('Found a document with no `doctype`.')
        if doc['doctype'] == 'synthesis':
            try:
                assert(synth is None)
            except AssertionError:
                raise AssertionError('Multiple synthesis documents found')
            synth = doc
        elif doc['doctype'] == 'ref':
            refs.append(doc)
    return (synth, refs)


def check_yaml(fname, feat_info):
    '''Check docs read from a yaml file for correctness and completeness.'''
    lang = YAMLLang(fname)
    assert(lang.synthesis is not None)
    assert(lang.refs != [])
    check_synthesis(lang.synthesis, lang)
    # The keys of feat_info.order() are valid IPA phonemes.
    check_phonemes(lang.synthesis['phonemes'], feat_info.order())
    for ref in lang.refs:
        check_ref(ref, lang)


def test_read_yaml():
    errors = ''
    featInfo = readFeatList('resources/ipa-table.txt')
    yamlfiles = glob.glob('langs/*.yaml')
    min_expected = 300
    try:
        assert(len(yamlfiles) > min_expected)
    except AssertionError:
        raise AssertionError(
            f'Expected to find at least {min_expected} yaml files and found {len(yamlfiles)}'
        )
    for fname in yamlfiles:
        try:
            check_yaml(fname, featInfo)
        except Exception as e:
            errors += f'Error in {fname}: {e}\n'
    try:
        assert(errors == '')
    except AssertionError:
        print(errors)
        raise AssertionError(errors)
