# SAPhon v1.2.0

This repository holds the data that underlies the [South American Phonological Inventory Database](http://linguistics.berkeley.edu/~saphon/en/).  It also contains Python routines for reading, checking, and writing the data files.

## Data file format

The `data/` directory contains a file for each language in the database.  The files are [YAML](http://yaml.org) documents and are compatible with the [version 1.2 JSON schema](https://yaml.org/spec/1.2/spec.html). The character encoding of all files is UTF-8.

Each file comprises one or more documents. There are two types of documents that may be present: 1) a `synthesis` document that describes the phonological inventory of the language; 2) zero or more `ref` documents that contain information gathered from each of the reference materials. There must be exactly one `synthesis` document per yaml file and by convention should be the first document in the yaml file. Normally there should be at least one `ref` document per language and one per bibliographic reference.

Each document is terminated by a line consisting only of `---` or end-of-file.

Data consists of scalars, sequences, and mappings in YAML parlance, which correspond to Python scalars, lists, and dicts.

### The `synthesis` document

The `synthesis` document contains language metadata and describes the phonological inventory of the language as synthesized by the SAPhon project from the reference materials. There must be exactly one `synthesis` document per language file.

The top-level scalar fields of the `synthesis` document are described first:

* `doctype`: The document type. Must be `synthesis`.

* `name`: The preferred citation form of the name of the language, in an orthographic form suited to academic publications.  It may contain spaces, hyphens, diacritics, and non-Latin glyphs that would occur in the preferred orthographic representation, e.g. **Arára do Mato Grosso**, **Aʔɨwa**, **Ashéninka (Apurucayali dialect)**.

* `short_name`: The language name abbreviated to around 12 characters or less, to be used in tables and plots where space is tight.  Spaces, hyphens, diacritics, non-Latin glyphs are all permitted.

* `family`: This is the linguistic family of the language, or `Isolate` for linguistic isolates.

Eight fields contain simple sequences (lists) of scalar values:

* `phonemes`: A list of the phonemes of the language, using symbols from the International Phonetic Alphabet. This list is synthesized from the entries listed in the `ref` documents.

* `alternate_names`: A list of alternative or outdated names for the language.

* `iso_codes`: A sequence of ISO 639-3 codes for the language, or of our own devising when the ISO codes are inadequate. When we need to distinguish language varieties not distinguished by ISO 639-3, we add a three letter extension to the code with an underscore '\_' separator. Ordinarily the sequence contains only one code, but more values occur when multiple ISO codes refer to the same language (e.g. [Huaylas-Conchucos Quechua]('data/HuaylasCQ.txt' contains codes `qxn`, `qwh`).

* `countries`: A list of country names where the language is indigenous.

* `notes`: A list of notes relating to the language.

* `nasal_harmony`: Boolean indicating presence of nasal harmony (true) or not (false).

* `laryngeal_harmony`: Boolean indicating presence of laryngeal harmony (true) or not (false).

* `tone`: Boolean indicating presence of tone (true) or not (false).

Two fields contain sequences (lists) of mappings (dicts):

* `coordinates`: A list of the geographical coordinates for the language. Each entry in the list is a mapping of the fields:
  * `latitude`: The coordinate latitude, given to 3 decimal places.
  * `longitude`: The coordinate longitude, given to 3 decimal places.
  * `elevation_meters`: The elevation in meters, rounded to the nearest integer meter. May be omitted if unknown.

* `allophones`: A list of mappings of allophonic variants to phonemes in the language. Each entry in the list is a mapping of the fields:
  * `allophone`: The allophonic variant, as written in IPA.
  * `phoneme`: The phoneme corresponding to the allophonic variant. The `phoneme` must exactly match an entry in the `phonemes` list.

### `ref` documents

A `ref` document contains information summarized from a bibliographic reference. There should be one `ref` document for each reference.

The top-level scalar fields for `ref` documents are:

* `doctype`: The document type. Must be `ref`.

* `citation`: A bibliographic citation for the reference.

* `ref_notes`: A list of notes relating to the reference.

* `graphemes2phonemes`: A list of mappings of graphemes that appear in the reference document and the phoneme it corresponds with in the `synthesis` phonemes list. Each entry in the list is a mapping of the fields:
  * `grapheme`: The grapheme in the reference document.
  * `phoneme`: The phoneme corresponding to the grapheme, written in IPA. The `phoneme` must exactly match an entry in the `phonemes` list or be null.

* `ref_allophones`: A list of mappings of allophonic variants to phonemes in the language, as described and written in the reference document. Each entry in the list is a mapping of the fields:
  * `grapheme_allophone`: The allophonic variant.
  * `grapheme_phoneme`: The phoneme corresponding to the allophonic variant.

## Data entry conventions

YAML is a flexible format that allows for multiple styles of representing identical values. The preceding description of the data file format covers the semantics of the values, and this section describes in more detail the syntactic choices that should be followed when creating or editing language files. In most cases a different syntactic choice could have been made without altering the meaning of the data file, and the guidance in this section is to encourage consistency across language files.

* Quoted and unquoted string values are allowed in YAML syntax. Most field values in SAPhon do not require quotes, and the general practice is to omit them where they are not necessary. The exception is the `citation` field, which often requires surrounding quotes (because of embedded ':<space>' sequences), and which will usually be quoted even when quoting is not required.

* For the `ref` `doctype` the fields should be listed in the order:


1. `doctype`
1. `name`
1. `short_name`
1. `alternate_names`
1. `iso_codes`
1. `family`
1. `countries`
1. `coordinates`
    1. `latitude`
    1. `longitude`
    1. `elevation_meters`
1. `phonemes`
1. `allophones`
    1. `allophone`
    1. `phoneme`
1. `nasal_harmony`
1. `tone`
1. `laryngeal_harmony`
1. `notes`


* For the `synthesis` `doctype` the fields should be listed in the order:


1. `doctype`
1. `citation`
1. `graphemes2phonemes`
    1. `grapheme`
    1. `phoneme`
1. `ref_allophones`
    1. `grapheme_allophone`
    1. `grapheme_phoneme`
1. `ref_notes`

* The `phonemes` list is created as a single line of comma-separated values enclosed by square brackets. This is the YAML ['flow sequence' style](https://yaml.org/spec/current.html#id2542413). For example:

```yaml
phonemes: [p, b, t, d, ɖ, tʃ, k, ɡ, ʔ, m, n, ɲ, s, ʐ, ʃ, w, j, ɽ, i, a, u, ɨ]
```

* All other lists of scalar values are created as a series of entries identified by the entry indicator '-'. Indentation of each entry is two characters, including the entry indicator. This is the YAML ['block sequence' style](https://yaml.org/spec/current.html#id2543032).
 For example:

```yaml
countries:
- Brazil
- Guyana
```

* Lists of mappings are also written in the 'block sequence' style, with each mapping introduced by the entry indicator '-'. The individual mapping fields are on separate lines that are indented two characters, including the entry indicator. For example, a list of three mappings:

```yaml
ref_allophonemes:
- grapheme_allophone: b
  grapheme_phoneme: b
- grapheme_allophone: mb
  grapheme_phoneme: b
- grapheme_allophone: m
  grapheme_phoneme: m
```

* All fields are expected to have a value, and optional fields should be included even if empty. Empty fields that normally contain a list should have a single '-' on the line below the field name. Empty string fields are denoted by two single quotation marks: ''. The floating point field `elevation_meters` should have the value '.NAN' if no value is known.

