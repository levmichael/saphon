#Data Entry Conventions

General formatting - each item in a field separated by spaces (no spaces within the item), reference for each data point enclosed in curly braces of the format `{autorlastnameYEAR:pg}`, items found only in load words enclosed in parentheses `()`, private notes from data collection and decision making kept in a separate file with the title `ComputerName-Phonotactic-Notes.txt`
**Note:** We still need to think about representing frequency information.

`syllable` (0-1): This is a list of all of the possible syllable types listed by the author. All syllables consist of a string of `C`s and `V`s. Long vowels are represented with the long vowel diacritic `ː`. `VV` indicates a sequence of two distinct vowels rather than a long vowel. 

`syllable.inf` (0-1): This is a list of possible syllable types inferred from the data in the source. All content of this field follows the same conventions as the `syllable` field. 

`onset.initial` (0-1): This is a list of all possible onset segments in word initial position as stated by the author. Each possible segment or cluster is separated by spaces. The possibility of onsetless syllables is represented by the string `null`. 

`onset.initial.inf` (0-1): This field contains a list of word-initial onset segments as inferred from the data in the source. The data is formatted as in the `onset.initial` field.

`onset.medial` (0-1): This is a list of all possible onset segments in word medial position as stated by the author. Each possible segment or cluster is separated by spaces. The possibility of word-medial onsetless syllables is represented by the string `null`. 

`onset.medial.inf` (0-1): This field contains a list of word-medial onset segments as inferred from the data in the source. The data is formatted as in the `onset.medial` field.

`onset.general` (0-1): This field contains a general inventory of all possible onset segments as given by the author. This field is only filled if there is no discussion of word-initial versus word-medial onsets. The data follows the same conventions as in the `onset.initial` and `onset.medial` fields.
**Note:** I’m not sure if this is actually how we would like to represent this type of data. I can see there being situations where an author states the possible onsets in the language but makes no distinctions based on where they can appear in the word. In this case, I think we may want to have a place to put that sort of data. I don’t want to automatically populate both the `onset.initial` and `onset.medial` fields if we don’t have explicit information to tell us that the given onsets can occur in both positions. At the same time, I’d rather not discard the information and have to rely solely on the exhaustiveness of our search of the data to infer where possible onsets occur and potentially not find some of the listed segments altogether. 

`nucleus` (0-1): This is a list of all segments that can form the nucleus of the syllable, as stated by the author.

`nucleus.inf` (0-1): This is a list of segments than can form the nucleus of the syllable, as inferred from the data in the source.

`coda.medial` (0-1): This field contains a list of all possible codas in word-medial position, as stated by the author. All coda segments or clusters are separated by spaces. The possibility of a word-medial syllable that does not have a coda is represented by the string `null`. 
**Note:** in our meeting we discussed the possibility of representing languages that do not allow codas with the string `none`. However, I now realize that upon adopting the convention `null` to refer to coda-less (or onset-less) syllables, this `none` convention may be unnecessary. If a language only allows `null` codas and has no other coda segments listed, this could be interpreted as meaning that no coda segments are allowed. Do we ever see the need to distinguish between these two? I think that this may actually be a better convention for at least the inferred coda field. This way, we don’t have to make an exhaustive statement about the prohibition of codas. We can just make the statement that we found only coda-less syllables. After all, all we can really do in the case of inferred inventories is note the presence, not the definite absence, of anything. 

`coda.medial.inf` (0-1): This field contains a list of codas in word-medial position, as inferred from the data in the source. The data follows the same conventions as in the `coda.medial` field. 

`coda.final` (0-1): This is a list of all possible codas in word-final position, as stated by the author. All coda segments or clusters are separated by spaces. The possibility of a word-final syllable that does not have a coda is represented by the string `null`. 

`coda.final.inf` (0-1): This is a list of codas in word-final position, as inferred from the data in the source. The data follows the same conventions as in the `coda.final` field. 

`coda.general` (0-1): This field contains a general inventory of all possible coda segments as given by the author. This field is only filled if there is no discussion of word-medial versus word-final codas. The data follows the same conventions as in the `coda.medial` and `coda.final` fields.
**Note:** See the discussion under the `onset.general` field. 

`min.word` (0-1): This field contains information on the size of the minimum phonological word as stated by the author. This field contains strings of numbers and letters. The letter `s` refers to syllables and `m` refers to moras. The letter is be preceded by a number indicating how many of these units must minimally be present to form a phonological word. For example, `2s` would indicate a bisyllabic minimum word.
**Note:** We may also want to considering including the possible repair strategies to fulfill this requirement, such as vowel lengthening, etc.

`min.word.inf` (0-1): This field contains information on the size of the minimum phonological word as inferred from the data in the source. The data follows the same conventions as in the `min.word` field.
**Note:** I don’t anticipate often having inferred information on minimum word requirements. If this isn’t discussed by the author, we may not want to deal with it. I include this field only because in Mawayana, the actual minimum word clearly differed from that stated in several places by the author.

`max.word` (0-1): This field contains information on the maximum size of the phonological word as stated by the author. This field contains strings of numbers and letters. The letter `s` refers to syllables and `m` refers to moras. The letter is preceded by a number indicating how many of these units can maximally be present in a phonological word. For example, `4s` would indicate a four syllable maximum word.

`max.word.inf` (0-1): This field contains information on the maximum size of the phonological word, as inferred from the data in the source. The data follows the same conventions as in the `max.word` field. 
**Note:** Once again, I don’t anticipate including this field very often, but see the note on `min.word.inf` for a possible scenario that could potentially apply here in the future. 

`stress` (0-1): This field contains information on the stress system of the language, as stated by the author. Feet can be left-aligned `LA` or right-aligned `RA`. Feet can also be either quantity-sensitive `QS` or quantity-insensitive `QI`. Additionally feet can be trochees `T` or iambs `I`. These letters are concatenated into a single string. For example, a system that has left-aligned quantity-sensitive trochees is represented as `LAQST`. 
**Note:** This is just a suggestion on how we may want to classify and represent these systems. We should also come up with a convention for how to represent where primary stress falls in the word, whether secondary stress exists, and which syllables, if any, are extrametrical.

`stress.inf` (0-1): This field contains information on the stress system of the language as inferred from the data in the source. The data in this field follows the same conventions as in the `stress` field.

`note.phonotactic` (0+): This is a note on the phonotactics of the language that will be made public.

`note.inventory` (0+): This is a public note on the phonological inventory (etc.) of the language (really any information included in the original SAPhon). This field will be generated from the current `note` field. 
