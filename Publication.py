import main
import unicodedata
import difflib
from collections import Counter


class Publication(object):

    def __init__(self, value, type_of_input, biblio, required, optional):
        self.Biblio = biblio
        self.quotes = []
        self.notes = []

        self.required_fields = required
        self.optional_fields = optional

        if type_of_input == "READ_BIBTEX":
            self._create_from_bibtex(value)
            self.short_identifier = self._lookup_short_identifier()
        elif type_of_input == "READ_BIBTEX_INPUT":
            self._bibtex_from_user_input()
            self._create_from_bibtex(self.bibtex)
            self.short_identifier = self._lookup_short_identifier()

    def __str__(self):
        if self.title[-1] != ".":
            name = self.title + "."
        else:
            name = self.title
        return name + " " + self.authors + "; " + self.year

    def __repr__(self):
        if self.title[-1] != ".":
            name = self.title + "."
        else:
            name = self.title
        return name + " " + self.authors + "; " + self.year

    def __eq__(self, other):
        # Equality is assessed by comparing the shorties - the short identifier.
        return self.short_identifier == other.short_identifier

    def __hash__(self):
        return hash(str(self))

    def list_keywords(self):
        print("Keywords in the paper: \n\t" + str(self))
        keywords = []
        for quote in self.quotes:
            for word in quote.keywords.split(", "):
                keywords.append(word)
        keywords = (list(set(keywords)))

        for i, key in enumerate(keywords):
            print(i, key)

    def list_note_keywords(self):
        print("Note keywords in the paper: \n\t" + str(self))
        keywords = []
        for note in self.notes:
            for word in note.keywords.split(", "):
                keywords.append(word)
        keywords = (list(set(keywords)))

        for i, key in enumerate(keywords):
            print(i, key)

    def add_a_quote(self):
        if self.is_booklike:
            summary = input("Please input summary: ")
            keywords = input("Please input keywords, separated by ', ': ")
            text = self._multi_input("Please input quote: ")
            self._new_quote(summary, keywords, "", text)
        else:
            summary = input("Please input summary: ")
            keywords = input("Please input keywords, separated by ', ': ")
            pages = input("Pages of the quote, separated by '--': ")
            text = self._multi_input("Please input quote: ")
            self._new_quote(summary, keywords, pages, text)

    def add_a_note(self):
        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        text = self._multi_input("Please input quote: ")
        self._new_note(summary, keywords, text)

    def _lookup_short_identifier(self):
        if self.bibtex:
            tmp = self.bibtex.split("\n")[0].replace("@" + self.type_of_publication + "{", "")
            return tmp[:len(tmp)-1]
        else:
            return None

    def _bibtex_from_user_input(self):
        self.fields = {}
        for reqfield in self.required_fields:
            self.fields[reqfield] = input(reqfield + ": ")

        for optfield in self.optional_fields:
            answer = input(optfield + " or 'n' to skip: ")
            if answer != "n" and answer != "":
                self.fields[optfield] = answer

        first_author = self.fields["author"].split(" and ")[0]
        shortie = (first_author.split(" ")[len(first_author.split(" "))-1] + "_" + self.fields["year"])

        self.bibtex = "@" + self.type_of_publication + "{" + shortie + "\n"
        for i, __ in enumerate(list(self.fields.values())):
            self.bibtex += "\t" + list(self.fields.keys())[i] + " = {" + list(self.fields.values())[i] + "}\n"
        self.bibtex += "}"

    def _create_from_bibtex(self, value):
        if value[0] == "@":
            value = value.split("\n")
        self.short_identifier = value[0].split("{")[1].split(",")[0]
        self.fields = {}
        for line in value:
            if " = " in line:
                key = line.split(" = ")[0].replace("\t", "")
                val = line.split(" = ")[1].replace("{", "").replace("}", "")
                if val[len(val)-1] == ",":
                    val = val[:len(val)-1]
                if key in self.fields:
                    self.fields[key].append(val)
                else:
                    self.fields[key] = [val]

        for field in self.required_fields:
            if field == "author":
                setattr(self, "authors", self.fields[field][0])
            else:
                setattr(self, field, self.fields[field][0])

        self.bibtex = self._bibtex_from_record_without_quotes(",\n".join(value))
        if "quote" in self.fields:
            self._add_quotes_from_bibtex(self.fields["quote"])
        if "note" in self.fields:
            self._add_notes_from_bibtex(self.fields["note"])

    def _bibtex_from_record_without_quotes(self, value):
        nv = value.split("\tquote")[0]
        if nv[len(nv)-1] is not "}":
            nv += "}"
        return nv

    def _add_quotes_from_bibtex(self, array_of_quotes):
        for q in array_of_quotes:
            self.quotes.append(main.Citation(q.split("__"), self, self.Biblio.keywords))

    def _add_notes_from_bibtex(self, array_of_notes):
        for q in array_of_notes:
            self._new_note(q.split("__")[0], q.split("__")[1], q.split("__")[2])

    def as_bibtex_with_quotes(self):
        if self.bibtex:
            bibtex = self.bibtex
            bibtex = bibtex[:(len(bibtex)-2)] + ","
            for q in self.quotes:
                bibtex += "\n" + q._to_bibtex_string()
            for n in self.notes:
                 bibtex += "\n" + n._to_bibtex_string()
        else:
            bibtex = "@" + self.type_of_publication + "{" + self.short_identifier + "\n\tdoi = {" + self.doi + "},\n" \
                            "\tyear = {" + self.year + "},\n"\
                            "\tvolume = {" + self.volume + "},\n"\
                            "\tnumber = {" + self.number + "},\n\tpages = {" + self.pages + "},\n"\
                            "\tauthor = {" + self.authors + "},\n\ttitle = {" + self.title + "},\n"\
                            "\tjournal = {" + self.journal + "},"
            for q in self.quotes:
                bibtex += "\n" + q._to_bibtex_string()
            for n in self.notes:
                bibtex += "\n" + n._to_bibtex_string()
        bibtex += "\n}\n"
        return bibtex

    def _new_quote(self, summary, keywords, pages, text):
        if self.is_booklike:
            new_quote = main.Citation([summary, keywords, ".", pages, text], self, self.Biblio.keywords)
        else:
            new_quote = main.Citation([summary, keywords, ".", text], self, self.Biblio.keywords)
        self.quotes.append(new_quote)

    def _new_note(self, summary, keywords, text):
        new_note = main.Note([summary, keywords, ".", text], self, self.Biblio.note_keywords)
        self.notes.append(new_note)

    def _multi_input(self, prompt):
        print(prompt)
        input_list = []
        while True:
            input_str = input(">")
            if input_str == "":
                break
            else:
                input_list.append(input_str)
        return " ".join(input_list)

    def remove_note(self, index_of_note):
        new_list_of_notes = []
        for i, note in enumerate(self.notes):
            if i == index_of_note:
                erase_this = (input("Do you really want to erase the note \"" + self.notes[i].summary + "\"? (y/n)" ) == "y")
                if not erase_this:
                    new_list_of_notes.append(note)
            else:
                new_list_of_notes.append(note)
        self.notes = new_list_of_notes

    def list_notes(self):
        for i, note in enumerate(self.notes):
            print(i, note._in_list())

    def list_quotes(self):
        for i, quote in enumerate(self.quotes):
            print(i, quote._in_list())

##from here on, this is more experimental

    def add_a_quote_complex(self):
        # This is a more elaborate function to add quotes to the Publication - with an easy spelling corrector. These
        # additions make it neccesary to add the keywords one-by-one.
        summary = input("Please input summary: ")
        more_keywords = True
        #keywords = []

        keywords = self._read_keywords_from_summary(summary)

        while more_keywords:
            new_keyword = input("Please input one keyword or leave empty: ")

            if new_keyword == "":
                more_keywords = False
            else:
                new_keyword = self._keyword_wrong_case(new_keyword)
                new_keyword = self._keyword_similar(new_keyword)
                keywords.append(new_keyword)

            try:
                predicted_keyword = self._predict_next_keyword(new_keyword, keywords)
                if predicted_keyword:
                    keywords.append(predicted_keyword)
            except KeyError:
                None

        keywords = list(set(keywords))
        text = self._multi_input("Please input quote: ")
        if self.is_booklike:
            pages = input("Pages of the quote, separated by '--': ")
            self._new_quote(summary, ", ".join(keywords), pages, text)
        else:
            self._new_quote(summary, ", ".join(keywords), None, text)

    def _keyword_wrong_case(self, keyword):
        words = [word for word in self.Biblio.keywords.words if keyword != word and caseless_equal(keyword, word)]

        if words:
            answer = input("You typed \"" + keyword + "\", but do you mean \"" + words[0] + "\"? (y/n)  ")
            if answer.lower() == "y":
                return words[0]
            else:
                return keyword
        else:
            return keyword

    def _keyword_similar(self, keyword):
        sorted_words = sorted([word for word in self.Biblio.keywords.words],
                              key = lambda x: sum([i[0] != ' ' for i in difflib.ndiff(keyword, x)]) / 2)
        relevant_word = sorted_words[0]

        if sum([i[0] != ' ' for i in difflib.ndiff(keyword, relevant_word)]) / 2 < 3 and relevant_word != keyword:
            answer = input("You typed \"" + keyword + "\", but do you mean \"" + relevant_word + "\"? (y/n)  ")
            if answer.lower() == "y":
                return relevant_word
            else:
                return keyword
        else:
            return keyword

    def _predict_next_keyword(self, query_keyword, already_present_keywords):
        size = len(self.Biblio.keywords.words[query_keyword])
        all_keywords = []
        for cit in self.Biblio.keywords.words[query_keyword]:
            words = [word for word in cit.keywords.split(", ") if word != query_keyword]
            all_keywords.extend(words)

        word_counter = Counter(all_keywords)

        try:
            if word_counter[sorted([w for w in word_counter], key = lambda x: word_counter[x])[::-1][0]] > size / 3:
                if word_counter.most_common(2)[1][0] not in already_present_keywords:
                    use_predicted_word = (
                        input("Do you want to add the keyword \"" + word_counter.most_common(2)[1][0] + "\"" + "? (y/n) " ).lower()
                        == "y")
                    if use_predicted_word:
                        return word_counter.most_common(2)[1][0]
                    else:
                        return None
                else:
                    return None
            else:
                return None #is falsy, so you could just check for the output of this function with an easy if clause
        except IndexError:
            return None

    def _read_keywords_from_summary(self, summary):
        kwords_in_summary = [kw for kw in self.Biblio.keywords.words if kw.lower() in summary.lower()]
        use_these_keywords = [ [kw] + [self._predict_next_keyword(kw, kwords_in_summary)] for kw in kwords_in_summary if "y" == input("Use the keyword '" + kw + "', found in summary (y/n)? ").lower()]
        use_these_keywords = [item for sublist in use_these_keywords for item in sublist if item]

        return use_these_keywords



def caseless_equal(left, right):
    return unicodedata.normalize("NFKD", left.casefold()) == unicodedata.normalize("NFKD", right.casefold())


class Article(Publication):
    required_fields = ["author", "title", "journal", "year"]
    optional_fields = ["volume", "number", "pages", "month"]
    is_booklike = False
    type_of_publication = "article"

    def __init__(self, value, type_of_input, biblio):
        super(Article, self).__init__(value, type_of_input, biblio, self.required_fields, self.optional_fields)

class Book(Publication):
    required_fields = ["author", "title", "publisher", "year"]
    optional_fields = ["volume", "series", "address", "edition", "month", "key"]
    type_of_publication = "book"
    is_booklike = True

    def __init__(self, value, type_of_input, biblio):
        super(Book, self).__init__(value, type_of_input, biblio, self.required_fields, self.optional_fields)

class InProceedings(Publication):
    required_fields = ["author", "title", "booktitle", "year"]
    optional_fields = ["editor", "pages", "organization", "publisher", "address", "month", "key"]
    is_booklike = False
    type_of_publication = "InProceedings"

    def __init__(self, value, type_of_input, biblio):
        super(InProceedings, self).__init__(value, type_of_input, biblio, self.required_fields, self.optional_fields)

class InBook(Publication):
    required_fields = ["author", "title", "pages", "publisher", "year"]
    optional_fields = ["volume", "series", "address", "edition", "editor", "month", "key"]
    is_booklike = True
    type_of_publication = "Inbook"

    def __init__(self, value, type_of_input, biblio):
       super(InBook, self).__init__(value, type_of_input, biblio, self.required_fields, self.optional_fields)