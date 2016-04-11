# cittex
This is a tool for literature - or rather quote organization. It saves and reads the widely used bibtex format, which makes it easy to use it with applications such as Latex. 
Using DOIs or manual input, the user can add publications and books to the internal library. These publications can be decorated with notes and quotes, which contain a short summary, keywords, sometimes a page number, and the full text of the quote or note.
These quotes and notes can then be searched, listed and grouped by topic/keyword. This makes it easy to collect information on a set of topics from a diverse rage of publications. 

## Installation & Requirements. 
Cittex uses python3. No installation is needed.

## Usage. 
As of right now, there is only command line usage supported. Usage of IPython is recommended for command completion. 
As an example of usage, usage.py is provided. 
In order to use the program, the main.py script must be loaded. It will load the Publication.py script.

####Commands
#####Open/Load/Save Library
*open_empty_library(location = None)* -- Opens an empty library. If you know where you'll want to save this library to, you can enter a location.

*read_bibtex(location)* -- Opens a library by reading a bibtex file from the provided location.

*export_as_bibtex(location)* -- Saves the library and all the notes and quotes attached to the publications in it to the provided locaton.

*save()* -- Saves the library and all the notes and quotes attached to the publications in it to the location that it was loaded from.

#####Inspect Library
*list_publications()* -- Lists all publications that are present in the Library.

*list_authors()* --  Lists all the authors whose work is present in the bibliography.

*list_keywords()* -- Lists the keywords that are attached to quotes from the publications in the bibliography.

*list_note_keywords()* -- Lists the keywords that are attached to notes from the publications in the bibliography.'

*add_a_publication()* -- Is used to add a paper to the bibliography via doi or manually.


#####Inspect quotes and notes

*quotes_with_keyword(keyword)* -- Lists all quotes that have the chosen keyword attached to them.

*quotes_with_note_keyword(kexword)* -- Lists all notes that have the chosen keyword attached to them.

*read_full_quote(keyword, index)* -- Shows the full quote specified by the chosen keyword and the index. Chosen keyword and index must be separated by " ".

*read_full_note(keyword, index)* -- Shows the full note specified by the chosen keyword and the index. Chosen keyword and index must be separated by " ".

*search_in_quotes(query)* -- Searches for an exact hit of the query in all of the quotes' texts.

*search_in_notes(query)* -- Searches for an exact hit of the query in all of the notes' texts.

#####Methods of Publications

*list_keywords()* and *list_note_keywords()* -- Lists the keywords for the quotes or the notes for this publication.

*add_a_quote()* and *add_a_note()* -- Adds a quote or note to the paper. 
