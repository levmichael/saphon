#Checklist for updating language files

When adding phonotactic information for languages, we should also update the phonological inventories to reflect our new conventions for data harvesting. For now, these files should be .txt files titled with the computer name of the language and stored in the [data_updated](https://github.com/whdc/saphon/tree/master/data_updated) folder on GitHub since they will not be released in our next version of the site. Later, these files will be merged with the language files in the [data](https://github.com/whdc/saphon/tree/master/data) folder on GitHub. You should start with a file that is a copy of the current .txt file for the language and make updates from there to include the following pieces of information. 


##Phoneme Inventories##

**Citations**: Each feature in the inventory should be accompanied by a citation of the format `{AuthorlastnameYear:pg}` with no space between the inventory segment and the accompanying citation. 

**Loanword Phonemes**: To the extent that we can determine if any phonemes are specific to loanwords, this should be indicated by placing the segment in parentheses `( )`. The citation accompanying the segment should indicate where we found evidence that this is only a loan phoneme.

**Surface-phonological segments**: If any segment is determined to be lacking "underlyingly" but relevant for the purposes of phonotactics, this surface-phonological segment should be included in the phoneme inventory and enclosed in square brackets `[ ]`. 

**Original inventories**: For each source listed in the `bib:` section of the language file, please scan and/or create a PDF of the page(s) containing the full consonant and vowel inventory. Files should be titled `computername-inventory-authorlastname-year.pdf`. For now, please email the files to contribute.saphon@gmail.com to be uploaded later to the department server. 


##Notes##

For any cases where the phoneme inventories we list are not identical to those listed in the source(s), a note should indicate the correspondences between our inventory and the published one(s). Additionally, this public note should outline why we made the analytical choices we did. 


##Phonotactics##

Phonotactic information should be added according to the conventions established in [PhonotacticDataConventions.md](https://github.com/whdc/saphon/blob/master/PhonotacticDataConventions.md)
