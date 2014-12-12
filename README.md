# SAPhon v1.1.3

This repository holds the data that underlies the [South American Phonological Inventory Database](http://linguistics.berkeley.edu/~saphon/en/).  It also contains Python routines for reading, checking, and writing the data files.

## Data file format

The `data/` directory contains a file for each language in the database.  The files are in Unicode (UTF-8) and are formatted simply, with a field on each line.  Unlike XML files, they are human-readable and easy to manipulate with UNIX command line tools such as `grep` and `diff`.

In general, each line has the form `key: value`.  The first colon in the line delimits the key.  Whitespace on either side of the colon is ignored.  The value is everything that follows, until the end of the line.

Possible keys are as follows.  Numerical codes indicate whether the key can occur zero or more times (0+), one or more times (1+), zero or one times (0-1), or whether it must occur exactly once (1).

* `name` (1): The preferred citation form of the name of the language, in an orthographic form that is suited to academic publications.  It contains spaces, hyphens, diacritics, and non-Latin glyphs that would occur in the preferred orthographic representation, e.g. **Arára do Mato Grosso**, **Aʔɨwa**, **Ashéninka (Apurucayali dialect)**.

* `name.short (1)`: The language name abbreviated to around 12 characters or less, to be used in tables and plots where space is tight.  Spaces, hyphens, diacritics, non-Latin glyphs are all permitted.

* `name.alt (0+)`: An alternative or outdated name for the language.

* `name.comp (1)`: A form of the language name that is for manipulation by computer programs.  The following requirements are strictly observed.  The name is no longer that 12 characters, and consists of just the 26 letters of English.  Lower and upper case letters are both permitted, but there are no spaces, hyphens, diacritics, or punctuation of any sort.  This name is identical to the base of the filename, which is `<name.comp>.txt`.  For this reason, the name will be unique, even after case is ignored, since some filesystems ignore case.

* `code` (1+): This is the ISO 639-3 code for the language, or a code of our own devising when the ISO code is inadequate.  When we need to distinguish varieties not distinguished by ISO 639-3, we add a three letter extension to the code.  This field may be repeated when multiple ISO codes refer to the same language.

* `family` (1): This is the linguistic family of the language, or `Isolate` for linguistic isolates.

* `country` (1+): A country that the language is indigenous to.

* `geo` (1+): This a geographical coordinate for the language, of the form `<latitude> <longitude> <elevation>`.  Fractions of a degree in latitude and longitude are given to 3 decimal places.  Elevation is in meters, rounded to the nearest meter.  Elevation may be omitted, if unknown.

* `feat` (1+): IPA symbols for the phonemes of the language, separated by spaces.  These may be listed over multiple instances of this field, or can be listed all at once.

* `bib` (0+): A bibliographic citation.

* `note` (0+): A note.
