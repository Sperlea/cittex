
# 11.04.16
# This is a tool for literature - or rather citation organization. It is based on the widely used bibtex format, which
# makes it easy to use it with applications such as Latex. Quotes are in the center of this program. The user can append
# notes and quotes to every publication and these quotes and notes are indexed by keywords, contain a short summary and
# the text of the quote, all as provided by the user.


import Publication
import requests
import textwrap
import unicodedata
import arxiv2bibtex
from collections import Counter
import isbnlib
from isbnlib.registry import bibformatters
from textblob import TextBlob as tb
from tqdm import tqdm
import math


class Library(object):
    def __init__(self, papers, keywords, nkeywords, loc):
        self.textblobcorpus = []
        self.publications = papers
        self.keywords = keywords
        self.note_keywords = nkeywords
        self.location = loc
        self.typedict = {subclass.type_of_publication: subclass for subclass in Publication.Publication.__subclasses__()}

        if papers:
            self.latest_paper = self.publications[len(self.publications) - 1]
        self.brainmodules = []

    def add_brainmodule(self, brainmodule):
        self.brainmodules.append(brainmodule)

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
        self.add_publication_from_bibtex(bibtex)

    def add_publication_from_arxiv(self, arxivid):
        bibtex = arxiv2bibtex.arxiv2bib([arxivid])[0]
        bibtex = bibtex.bibtex().replace(bibtex.id+",", bibtex.authors[0].split(" ")[-1] + "_" + bibtex.year + ",")
        self.add_publication_from_bibtex([b for b in bibtex.split(",\n")])

    def add_publication_from_bibtex(self, bibtex):
        try:
            if "@techreport{" in bibtex[0]:
                bibtex = self._turn_techreport_to_type(bibtex, Publication.Article)

            new_paper = self.typedict[bibtex[0].split("{")[0][1:]](bibtex, "READ_BIBTEX", self)
            if not self._already_contains_publication(new_paper):
                oldshorties = [b.short_identifier for b in self.publications if new_paper.short_identifier in b.short_identifier]
                if oldshorties:
                    try:
                        oldletter = new_paper.short_identifier.split("_")[1][4]
                        newshort_identifier = new_paper.short_identifier[:-1] + chr(ord(oldletter)+1)
                    except IndexError:
                        newshort_identifier = new_paper.short_identifier +"a"
                    new_paper.bibtex = new_paper.bibtex.replace(new_paper.short_identifier, newshort_identifier)

                    self.add_publication_from_bibtex(new_paper.bibtex.split(",\n"))
                else:
                    self.append_publication(new_paper)
            else:
                print("This paper is already in the Library.")
                self.latest_paper = new_paper
        except TypeError:
            print("ERROR: This doi couldn't be resolved. Skipping...")

    def add_publication_from_isbn(self, isbn):
        isbnlib.config.add_apikey("isbndb", "2TCD2CVI")
        bibtex = bibformatters['bibtex']

        data = isbnlib.meta(isbn, "isbndb")
        for part in data:
            if not data[part]:
                data[part] = input("Missing Value! Please input value for the field " + part + ". ")
        data["ISBN-13"] = data["Authors"][0].split(", ")[0] + "_" + str(data["Year"])

        new_bibtex = bibtex(data).replace("  ", "").replace("\n ", "\n").split("\n")
        self.add_publication_from_bibtex(new_bibtex)

    def save(self):
        self.export_as_bibtex(self.location)
        for bm in self.brainmodules:
            bm.save()

    def _already_contains_publication(self, new_paper):
        found = False
        for piece in self.publications:
            if piece.short_identifier == new_paper.short_identifier:
                if piece.title.upper().replace(".", "") == new_paper.title.upper().replace(".", ""):
                    found = True
                    break
        return found

    def export_as_bibtex(self, location, verbose = True):
        handle = open(location, "w")
        for paper in tqdm(self.publications, desc = "Saving as BIBTEX... ", unit = " paper", disable = not verbose,
            bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} paper"):
            handle.write(paper.as_bibtex_with_quotes())
        print()

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
            print(counter + 1, ".", paper.authors, paper.year, "--", paper.title)

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
        print(textwrap.fill(self.keywords.words[chosen_keyword][index].text, 100))

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
        if doi:
            print(doi)
            self.add_publication_with_doi(doi)
            for bm in self.brainmodules:
                bm.add_paper(self.latest_paper)
        else:
            arxivid = input("Please input arxiv ID. If no doi is available, leave empty. ")
            if arxivid:
                self.add_publication_from_arxiv(arxivid)
                for bm in self.brainmodules:
                    bm.add_paper(self.latest_paper)
            else:
                isbn = input("Please input ISBN-13. If no doi is available, leave empty. ")
                if isbn:
                    self.add_publication_from_isbn(isbn)
                    for bm in self.brainmodules:
                        bm.add_paper(self.latest_paper)
                else:
                    type_short = input("Type of publication. 'a' for article, 'b' for book, 'i' for inbook: ")
                    if type_short is 'a':
                        new_publication = Publication.Article(None, "READ_BIBTEX_INPUT", self)
                    elif type_short is 'b':
                        new_publication = Publication.Book(None, "READ_BIBTEX_INPUT", self)
                    elif type_short is "i":
                        new_publication = Publication.InBook(None, "READ_BIBTEX_INPUT", self)
                    else:
                        new_publication = Publication.Publication(None, "READ_BIBTEX_INPUT", self)

                    if not self._already_contains_publication(new_publication):
                        self.append_publication(new_publication)
                        for bm in self.brainmodules:
                            bm.add_paper(new_publication)
                    else:
                        print("This paper is already in the Library.")
                        self.latest_paper = new_publication

    #TODO: Write a function that plots the authors as network. But also count the number of non-connected networks.

    def _turn_techreport_to_type(self, bibtex, new_type):
        bibtex.insert(1, "\tjournal = {bioRxiv}")
        fields = [line.strip().split(" = ")[0] for line in bibtex]

        if len([part for part in new_type.required_fields if part in fields]) == 4:
            bibtex[0] = bibtex[0].replace("techreport", new_type.type_of_publication)

        return bibtex

    def find_double_keywords(self):
        for i, paper in enumerate(self.publications):
            print(i, paper)
            for j, quote in enumerate(paper.quotes):
                doubles = [kword for kword in Counter(quote.keywords.split(", "))
                           if Counter(quote.keywords.split(", "))[kword] > 1]
                if doubles:
                    print(doubles)

    def update_brain_modules(self, paper):
        for bm in self.brainmodules:
            bm.add_information_on_paper(paper)

    def plot_years(self):
        import matplotlib.pyplot as plt
        import seaborn as sns

        years = [int(pub.year) for pub in self.publications]
        plt.hist(years, bins=(max(years) - min(years)) + 1)
        plt.show()

    def loop_through_fulltext_quotes(self, chosen_keyword):
        print("Chosen keyword: " + chosen_keyword)
        for counter, cit in enumerate(self.keywords.words[chosen_keyword]):
            print(str(counter) + " of " + str(len(self.keywords.words[chosen_keyword])))
            print("Summary: " + self.keywords.words[chosen_keyword][counter].summary)
            print("Keywords: " + self.keywords.words[chosen_keyword][counter].keywords)
            print("Paper: " + str(self.keywords.words[chosen_keyword][counter].publication))
            print("Short: " + self.keywords.words[chosen_keyword][counter].publication.short_identifier)
            print(textwrap.fill(self.keywords.words[chosen_keyword][counter].text, 100))
            input("(enter)")
            print("")

    def get_quoteless_papers(self):
        return [paper for paper in self.publications if len(paper.quotes) == 0]

    def remove_paper(self, paper):
        papernumber = [i for i, pap in enumerate(self.publications) if pap == paper][0]

        del self.publications[papernumber]

    def move_quoteless_papers_to_bookshelf_of_shame(self):
        bos = [brain for brain in self.brainmodules if getattr(brain, "add_without_mother", None)][0]

        for i, pub in enumerate(self.get_quoteless_papers()[::-1]):
            answer = input("Do you want to keep '" + pub.title + "'? (y/n) ")
            if answer == "y":
                bos.add_without_mother(pub)
            else:
                None
            self.remove_paper(pub)
        self.save()



class Citation(object):
    def __init__(self, block_of_text, publication, key):
        if publication.is_booklike:
            self.publication = publication
            self.summary = block_of_text[0]
            self.keywords = block_of_text[1]
            self.logic = block_of_text[2]
            self.pages = block_of_text[3]
            self.text = block_of_text[4]
            publication.Biblio.textblobcorpus.append(tb(self.text))
            for word in self.keywords.split(", "):
                key.add_word(word, self)
        else:
            self.publication = publication
            self.summary = block_of_text[0]
            self.keywords = block_of_text[1]
            self.logic = block_of_text[2]
            self.text = block_of_text[3]
            publication.Biblio.textblobcorpus.append(tb(self.text))
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

    def __hash__(self):
        return hash(str(self.text))

    def _to_bibtex_string(self):
        line = "\tquote = {" + self.summary + "__" + self.keywords + "__" + self.logic + "__"
        try:
            line +=  self.pages + "__" + self.text.replace("\n", "") + "},"
        except:
            line += self.text.replace("\n", "") + "},"
        return line

    def _in_list(self):
        return "\t" + self.__repr__().replace("\n", "\n\t")

    def _add_logic(self, line):
        self.logic = line


class Note(Citation):
    def __init__(self, block_of_text, publication, key):
        #TODO: Wirklich super.init implementieren.
        self.summary = block_of_text[1]
        self.keywords = block_of_text[2]
        self.publication = publication
        self.text = block_of_text[3]
        for word in self.keywords.split(", "):
            key.add_word(word, self)

    def _to_bibtex_string(self):
        return "\tnotes = {" + self.summary + "__" + self.keywords + "__" + self.text.replace("\n", "") + "},"


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

    def replace_keyword(self, old_kw, new_kw):
        for citation in self.words[old_kw]:
            citation.keywords = citation.keywords.replace(old_kw, new_kw)
            citation.keywords = ", ".join(list(set(citation.keywords.split(", "))))

        self.words[new_kw].extend(self.words.pop(old_kw))
        self.words[new_kw] = list(set(self.words[new_kw]))


class NoteKeywords(Keywords):
    def __init__(self):
        self.words = {}


class BrainModule():
    ## A sort of API for brain modules, which will be able to be added to a literature organizer and standard functions
    # will automatically call functions that are implemented in the modules

    def save(self):
        raise NotImplementedError

    def add_information_on_paper(self, paper):
        raise NotImplementedError

    def add_paper(self, paper):
        raise NotImplementedError


def read_bibtex(location):
    file = open(location, "r")
    record = []
    bib = open_empty_library(location, key=Keywords())
    for i, line in enumerate(file):
        if "quote = {" in line or "notes = {" in line:
            record.append(line.replace(",\n", "").replace("\n", ""))
        else:
            record.append(line.replace(",\n", "").replace("\n", "").replace(", ", ""))
        if line == "}\n" or line == "}":
            publication = bib.typedict[record[0].split("{")[0][1:]](record, "READ_BIBTEX", bib)
            bib.append_publication(publication)
            record = []
    return bib


def open_empty_library(location = None, key = Keywords(), nkey = NoteKeywords()):
    return Library([], key, nkey, location)


def caseless_equal(left, right):
    return unicodedata.normalize("NFKD", left.casefold()) == unicodedata.normalize("NFKD", right.casefold())
