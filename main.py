
# 11.04.16
# This is a tool for literature - or rather citation organization. It is based on the widely used bibtex format, which
# makes it easy to use it with applications such as Latex. Quotes are in the center of this program. The user can append
# notes and quotes to every publication and these quotes and notes are indexed by keywords, contain a short summary and
# the text of the quote, all as provided by the user.


import Publication
import requests

class Library(object):
    def __init__(self, papers, keywords, nkeywords, loc):
        self.publications = papers
        self.keywords = keywords
        self.note_keywords = nkeywords
        self.location = loc
        if papers:
            self.latest_paper = self.publications[len(self.publications) - 1]

    def append_publication(self, publication):
        self.publications.append(publication)
        self.latest_paper = publication

    def list_years(self):
        yearlist = []
        for paper in self.publications:
            yearlist.append(paper.year)
        return yearlist

    def get_oldest_publication(self):
        min_year = 3000
        oldest_paper = None
        for paper in self.publications:
            if int(paper.year) < min_year:
                min_year = int(paper.year)
                oldest_paper = paper
        print(oldest_paper)

    def add_publication_with_doi(self, doi):
        bibtex = self._get_bibtex_from_internet(doi)

        if "@article{" in bibtex[0]:
            new_paper = Publication.Article(bibtex, "READ_BIBTEX", self)
        elif "@book{" in bibtex[0]:
            new_paper = Publication.Book(bibtex, "READ_BIBTEX", self)
        else:
            print("I don't know what this is.")
            new_paper = Publication.Publication(bibtex, "READ_BIBTEX", self)
        # TODO: Write a test that makes sure that the paper is not yet in Bibliography.papers
        self.publications.append(new_paper)
        self.latest_paper = new_paper

    def save(self):
        self.export_as_bibtex(self.location)

    def export_as_bibtex(self, location):
        handle = open(location, "w")

        for i, paper in enumerate(self.publications):
            print("Written " + str(i+1) + " of " + str(len(self.publications)) + " publications as BIBTEX")
            print(paper.title)
            handle.write(paper.as_bibtex_with_quotes())

    def search_in_quotes(self, query):
        counter = 0
        for paper in  self.publications:
            for cit in paper.quotes:
                if query in cit.text:
                    print("Query: " + query + " - hit " + str(counter))
                    print(cit)
                    print()
                    counter += 1

    def search_in_notes(self, query):
        counter = 0
        for paper in self.publications:
            for note in paper.notes:
                if query in note.text:
                    print("Query: " + query + " - hit " + str(counter))
                    print(note)
                    print()
                    counter += 1

    def _get_bibtex_from_internet(self, doi):
        bibtex_text = self._doi2bibtex(doi)
        if "title = {" in bibtex_text:
            output = []
            for line in bibtex_text.split(",\n"):
                output.append(line)
            return output

    def _doi2bibtex(self, doi):
        # Gets the information about a given publication from the internet in bibtex format
        # adapted from http://www.michelepasin.org/blog/2014/12/03/dereference-a-doi-using-python/
        self.headers = {'accept': 'application/x-bibtex'}
        if doi.startswith("http://"):
            url = doi
        else:
            url = "http://dx.doi.org/" + doi
        r = requests.get(url, headers=self.headers)
        return r.text

    def list_publications(self):
        'Lists the publications that are saved in the bibliography.'
        for counter, paper in enumerate(self.publications):
            print(counter+1, ".", paper.authors, paper.year, "--", paper.title)

    def list_keywords(self):
        'Lists the keywords that are attached to quotes from the publications in the bibliography.'
        output = []
        for keyword in self.keywords.words:
            output.append(keyword + "\t -- Number: " + str(len(self.keywords.words[keyword])))

        output = sorted(output, key=lambda v: v.upper())
        for counter, line in enumerate(output):
            print(counter, line)

    def list_note_keywords(self):
        'Lists the keywords that are attached to notes from the publications in the bibliography.'
        output = []
        for keyword in self.note_keywords.words:
            output.append(keyword + "\t -- Number: " + str(len(self.note_keywords.words[keyword])))
        output = sorted(output, key=lambda v: v.upper())
        for counter, line in enumerate(output):
            print(counter, line)

    def list_authors(self):
        'Lists all the authors whose work is present in the bibliography.'
        def is_this_author_new(this_author_list, this_author):
            output = True
            for aut in this_author_list:
                if aut[0] == this_author:
                    output = False
                    break
            return output

        def add_paper_to_author(this_author_list, this_author, this_paper):
            for counter, __ in enumerate(this_author_list):
                if this_author_list[counter][0] in this_author:
                    tmp = this_author_list[counter][1] + ", " + this_paper.short_identifier
                    this_author_list[counter] = (this_author_list[counter][0], tmp)
            return this_author_list

        author_list = []
        for paper in self.publications:
            for author in paper.authors.split(" and "):
                author = author.split(" ")[len(author.split(" "))-1]
                if is_this_author_new(author_list, author):
                    author_list.append((author, paper.short_identifier))
                else:
                    author_list = add_paper_to_author(author_list, author, paper)

        print("Found " + str(len(author_list)) + " authors in " + str(len(self.publications)) + " publications.")
        for line in sorted(author_list):
            print(line[0] + "\t- " + line[1])

    def quotes_with_keyword(self, chosen_keyword):
        'Lists all quotes that have the chosen keyword attached to them.'
        print("Chosen keyword: " + chosen_keyword)
        for counter, cit in enumerate(self.keywords.words[chosen_keyword]):
            print(counter, cit.summary, "\t||\t" + cit.publication.short_identifier + "\t||\t" + cit.publication.title)

    def quotes_with_note_keyword(self, chosen_keyword):
        'Lists all notes that have the chosen keyword attached to them.'
        print("Chosen note keyword: " + chosen_keyword)
        for counter, cit in enumerate(self.note_keywords.words[chosen_keyword]):
            print(counter, cit.summary, "\t||\t" + cit.publication.short_identifier + "\t||\t" + cit.publication.title)

    def read_full_quote(self, chosen_keyword, index):
        'Shows the full quote specified by the chosen keyword and the index. Chosen keyword and index must be separated by " ".'
        print("Chosen keyword: " + chosen_keyword)
        print("Summary: " + self.keywords.words[chosen_keyword][index].summary)
        print("Keywords: " + self.keywords.words[chosen_keyword][index].keywords)
        print("Paper: " + str(self.keywords.words[chosen_keyword][index].publication))
        print("Short: " + self.keywords.words[chosen_keyword][index].publication.short_identifier)
        print(self.keywords.words[chosen_keyword][index].text)

    def read_full_note(self, chosen_keyword, index):
        'Shows the full note specified by the chosen keyword and the index. Chosen keyword and index must be separated by " ".'
        print("Chosen keyword: " + chosen_keyword)
        print("Summary: " + self.note_keywords.words[chosen_keyword][index].summary)
        print("Keywords: " + self.note_keywords.words[chosen_keyword][index].keywords)
        print("Paper: " + str(self.note_keywords.words[chosen_keyword][index].publication))
        print("Short: " + self.note_keywords.words[chosen_keyword][index].publication.short_identifier)
        print(self.note_keywords.words[chosen_keyword][index].text)

    def show_publications_with_keyword(self, chosen_keyword):
        print("Chosen keyword: " + chosen_keyword)
        relevant_papers = []
        for cit in self.keywords.words[chosen_keyword]:
            relevant_papers.append(cit.paper)
        output = list(set(relevant_papers))

        for counter in range(0, len(output)):
            print(counter, output[counter])

    def add_a_publication(self):
        'Is used to add a paper to the bibliography via doi or manually'
        doi = input("Please input doi. If no doi is available, leave empty. ")
        print(doi)
        if doi:
            self.add_publication_with_doi(doi)
        else:
            type_short = input("Type of publication. 'a' for article, 'b' for book, 'i' for inbook: ")
            if type_short is 'a':
                new_publication = Publication.Article(None, "READ_BIBTEX_INPUT", self)
            elif type_short is 'b':
                new_publication = Publication.Book(None, "READ_BIBTEX_INPUT", self)
            else:
                new_publication = Publication.Publication(None, "READ_BIBTEX_INPUT", self)
            # TODO: Write a test that makes sure that the paper is not yet in Bibliography.papers
            self.append_publication(new_publication)


class Citation(object):
    def __init__(self, block_of_text, publication, key, type_of_input):
        if type_of_input == "BIBTEX":
            if publication.type_of_publication == "article":
                self.summary = block_of_text.split("__")[0]
                self.keywords = block_of_text.split("__")[1]
                self.publication = publication
                self.text = block_of_text.split("__")[3]
                for word in self.keywords.split(", "):
                    key.add_word(word, self)
            elif publication.type_of_publication == "book":
                self.summary = block_of_text.split("__")[0]
                self.keywords = block_of_text.split("__")[1]
                self.publication = publication
                self.pages = block_of_text.split("__")[2]
                self.text = block_of_text.split("__")[3]
                for word in self.keywords.split(", "):
                    key.add_word(word, self)
        elif type_of_input == "USER":
            if publication.type_of_publication == "article":
                self.summary = block_of_text[1]
                self.keywords = block_of_text[2]
                self.publication = publication
                self.text = block_of_text[4]
                for word in self.keywords.split(", "):
                    key.add_word(word, self)
            elif publication.type_of_publication == "book":
                self.summary = block_of_text[1]
                self.keywords = block_of_text[2]
                self.publication = publication
                self.pages = block_of_text[3]
                self.text = block_of_text[4]
                for word in self.keywords.split(", "):
                    key.add_word(word, self)

    def __repr__(self):
        output = "Summary: " + self.summary + "\nKeywords: " + self.keywords
        try:
            output += "\nPages: " + self.pages + "\nPaper: " + str(self.publication) + "\n" + self.text
        except:
            output += "\nPaper: " + str(self.publication) + "\n" + self.text
        return output

    def __eq__(self, other):
        return self.text is other.text

    def _to_bibtex_string(self):
        line = "\tquote = {" + self.summary + "__" + self.keywords + "__"
        try:
            line +=  self.pages + "__" + self.text.replace("\n", "") + "},"
        except:
            line += self.text.replace("\n", "") + "},"
        return line


class Note(Citation):
    def __init__(self, block_of_text, publication, key, type_of_input):
        if type_of_input == "BIBTEX":
            self.summary = block_of_text.split("__")[0]
            self.keywords = block_of_text.split("__")[1]
            self.publication = publication
            self.text = block_of_text.split("__")[2]
            for word in self.keywords.split(", "):
                key.add_word(word, self)
        elif type_of_input == "USER":
            self.summary = block_of_text[1]
            self.keywords = block_of_text[2]
            self.publication = publication
            self.text = block_of_text[3]
            for word in self.keywords.split(", "):
                key.add_word(word, self)

    def _to_bibtex_string(self):
        return "\tnote = {" + self.summary + "__" + self.keywords + "__" + self.text.replace("\n", "") + "},"


class Keywords(object):
    def __init__(self):
        self.words = {}

    def add_word(self, word, quote):
        if word in self.words:
            self.words[word].append(quote)
        else:
            self.words[word] = [quote]

    def overwrite(self, words):
        self.words = words


class Note_Keywords(Keywords):
    def __init__(self):
        self.words = {}


def read_bibtex(location):
    file = open(location, "r")
    record = []
    bib = open_empty_library(location)
    for i, line in enumerate(file):
        if "quote = {" in line or "note = {" in line:
            record.append(line.replace(",\n", "").replace("\n", ""))
        else:
            record.append(line.replace(",\n", "").replace("\n", "").replace(", ", ""))
        if line == "}\n" or line == "}": #line == "}" or
            if "@article" in record[0]:
                publication = Publication.Article(record, "READ_BIBTEX", bib)
            elif "@book" in record[0]:
                publication = Publication.Book(record, "READ_BIBTEX", bib)
            else:
                publication = Publication.Publication(record, "READ_BIBTEX", bib)
            bib.append_publication(publication)
            record = []
    return bib


def open_empty_library(location = None, key = Keywords(), nkey = Note_Keywords()):
    return Library([], key, nkey, location)