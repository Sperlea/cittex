import main

class Publication(object):
    # TODO: Make it easily possible to change the information of a given quote/note!
    def __init__(self, value, type_of_input, biblio):
        self.Biblio = biblio
        self.quotes = []
        self.notes = []
        if type_of_input == "DOI":
            self.doi = value
            self._create_from_bibtex(self._get_bibtex_from_internet(), "")
            self.short_identifier = self._lookup_short_identifier()
        elif type_of_input == "READ_BIBTEX":
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
        def _multi_input(prompt):
            print(prompt)
            input_list = []
            while True:
                input_str = input(">")
                if input_str == "":
                    break
                else:
                    input_list.append(input_str)
            return " ".join(input_list)

        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        text = _multi_input("Please input quote: ")
        self._new_quote(summary, keywords, "", text)

    def add_a_note(self):
        def _multi_input(prompt):
            print(prompt)
            input_list = []
            while True:
                input_str = input(">")
                if input_str == "":
                    break
                else:
                    input_list.append(input_str)
            return " ".join(input_list)

        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        text = _multi_input("Please input quote: ")
        self._new_note(summary, keywords, "", text)

    def _lookup_short_identifier(self):
        if self.bibtex:
            tmp = self.bibtex.split("\n")[0].replace("@" + self.type_of_publication + "{", "")
            return tmp[:len(tmp)-1]
        else:
            return None

    def _bibtex_from_user_input(self):
        self.type_of_publication = input("Type of publication.")
        self.fields = {"title": input("Title of the paper: "),
                      # Authors need to be in the format $Lastname$, $initials of first names$ and $next_lastname$ etc.
                      "author": input("Names of the authors, separated by ' and ': "),
                      "year": input("Year of publication: "),
                      "journal": input("Name of journal: "),
                      "volume": input("Volume of the issue: "),
                      "number": input("Number of the issue: "),
                      "pages": input("Page numbers the article is on, separated by '--': "),
                      "doi": "None",
                      }

        first_author = self.fields["author"].split(" and ")[0]
        shortie = (first_author.split(" ")[len(first_author.split(" "))-1] + "_" + self.fields["year"])

        self.bibtex = "@" + self.type_of_publication + "{" + shortie + ",\n"
        for i, __ in enumerate(list(self.fields.values())):
            self.bibtex += "\t" + list(self.fields.keys())[i] + " = {" + list(self.fields.values())[i] + "},\n"
        self.bibtex += "}"

    def _create_from_bibtex(self, value):

        def dict_to_fields():
            self.title = self.fields["title"][0]
            self.year = self.fields["year"][0]
            self.authors = self.fields["author"][0]
            value[len(value)-1] = value[len(value)-1].replace("\n}", ",\n}")
            self.bibtex = self._bibtex_from_record_without_quotes(",\n".join(value))
            self.journal = self.fields["journal"][0]
            try:
                self.volume = self.fields["volume"][0]
            except:
                self.volume = ""
            try:
                self.number = self.fields["number"][0]
            except:
                self.number = ""
            try:
                self.pages = self.fields["pages"][0]
            except:
                self.pages = ""
            self.doi = self.fields["doi"][0]

        if value[0] == "@":
            value = value.split("\n")
        self.type_of_publication = value[0].split("{")[0].replace("@", "")
        self.short_identifier = value[0].split("{")[1].split(",")[0]

        try:
            self.title = self.fields["title"]
            self.year = self.fields["year"]
            self.authors = self.fields["author"]
            self.journal = self.fields["journal"]
            try:
                self.volume = self.fields["volume"]
            except:
                self.volume = ""
            try:
                self.number = self.fields["number"]
            except:
                self.number = ""
            try:
                self.pages = self.fields["pages"]
            except:
                self.pages = ""
            self.doi = "None"
        except:
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
        dict_to_fields()

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
            self._new_quote(q.split("__")[0], q.split("__")[1], "", q.split("__")[2])

    def _add_notes_from_bibtex(self, array_of_notes):
        for q in array_of_notes:
            self._new_note(q.split("__")[0], q.split("__")[1], "", q.split("__")[2])

    def as_bibtex_with_quotes(self):
        if self.bibtex:
            bibtex = self.bibtex
            bibtex = bibtex[:(len(bibtex)-2)]
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
        new_quote = main.Citation([" ", summary, keywords, pages, text], self, self.Biblio.keywords, "USER")
        self.quotes.append(new_quote)

    def _new_note(self, summary, keywords, pages, text):
        new_note = main.Note([" ", summary, keywords, pages, text], self, self.Biblio.note_keywords, "USER")
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

class Article(Publication):

    def __init__(self, value, type_of_input, biblio):
        self.type_of_publication = "article"
        self.Biblio = biblio
        self.quotes = []
        self.notes = []
        if type_of_input == "READ_BIBTEX":
            self._create_from_bibtex(value)
            self.short_identifier = self._lookup_short_identifier()
        elif type_of_input == "READ_BIBTEX_INPUT":
            self._bibtex_from_user_input()
            self._create_from_bibtex(self.bibtex)
            self.short_identifier = self._lookup_short_identifier()

    def _create_from_bibtex(self, value):

        def dict_to_fields():
            self.title = self.fields["title"][0]
            self.year = self.fields["year"][0]
            self.authors = self.fields["author"][0]
            value[len(value)-1] = value[len(value)-1].replace("\n}", ",\n}")
            self.journal = self.fields["journal"][0]
            try:
                self.volume = self.fields["volume"][0]
            except:
                self.volume = ""
            try:
                self.number = self.fields["number"][0]
            except:
                self.number = ""
            try:
                self.pages = self.fields["pages"][0]
            except:
                self.pages = ""
            self.doi = self.fields["doi"][0]

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
        dict_to_fields()
        self.bibtex = self._bibtex_from_record_without_quotes(",\n".join(value))
        if "quote" in self.fields:
            self._add_quotes_from_bibtex(self.fields["quote"])
        if "note" in self.fields:
            self._add_notes_from_bibtex(self.fields["note"])

    def add_a_quote(self):
        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        text = self._multi_input("Please input quote: ")
        self._new_quote(summary, keywords, "", text)

    def add_a_note(self):
        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        text = self._multi_input("Please input quote: ")
        self._new_note(summary, keywords, "", text)

    def _bibtex_from_user_input(self):
        self.fields = {"title": input("Title of the paper: "),
                    # Authors need to be in the format $Lastname$, $initials of first names$ and $next_lastname$ etc.
                      "author": input("Names of the authors, separated by ' and ': "),
                      "year": input("Year of publication: "),
                      "journal": input("Name of journal: "),
                      "volume": input("Volume of the issue: "),
                      "number": input("Number of the issue: "),
                      "pages": input("Page numbers the article is on, separated by '--': "),
                        "doi": "None",
        }

        first_author = self.fields["author"].split(" and ")[0]
        shortie = (first_author.split(" ")[len(first_author.split(" "))-1] + "_" + self.fields["year"])

        self.bibtex = "@" + self.type_of_publication + "{" + shortie + ",\n"
        for i, __ in enumerate(list(self.fields.values())):
            self.bibtex += "\t" + list(self.fields.keys())[i] + " = {" + list(self.fields.values())[i] + "},\n"
        self.bibtex += "}"

class Book(Publication):
    def __init__(self, value, type_of_input, biblio):
        self.type_of_publication = "book"
        self.Biblio = biblio
        self.quotes = []
        self.notes = []
        if type_of_input == "READ_BIBTEX":
            self._create_from_bibtex(value)
            self.short_identifier = self._lookup_short_identifier()
            #print(self.bibtex)
        elif type_of_input == "READ_BIBTEX_INPUT":
            self._bibtex_from_user_input()
            self._create_from_bibtex(self.bibtex)
            self.short_identifier = self._lookup_short_identifier()

    def _create_from_bibtex(self, value):
        def dict_to_fields():
            self.title = self.fields["title"][0]
            self.year = self.fields["year"][0]
            self.authors = self.fields["author"][0]
            self.publisher = self.fields["publisher"][0]
            try:
                self.editor = self.fields["editor"][0]
            except:
                self.editor = ""
            try:
                self.volume = self.fields["volume"][0]
            except:
                self.volume = ""
            try:
                self.number = self.fields["number"][0]
            except:
                self.number = ""
            try:
                self.edition = self.fields["edition"][0]
            except:
                self.edition = ""
            self.doi = self.fields["doi"][0]

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
        dict_to_fields()
        self.bibtex = self._bibtex_from_record_without_quotes(",\n".join(value))
        if "quote" in self.fields:
            self._add_quotes_from_bibtex(self.fields["quote"])
        if "note" in self.fields:
            self._add_notes_from_bibtex(self.fields["note"])

    def add_a_quote(self):
        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        pages = input("Pages of the quote, separated by '--': ")
        text = self._multi_input("Please input quote: ")
        self._new_quote(summary, keywords, pages, text)

    def add_a_note(self):
        summary = input("Please input summary: ")
        keywords = input("Please input keywords, separated by ', ': ")
        pages = input("Pages of the quote, separated by '--': ")
        text = self._multi_input("Please input quote: ")
        self._new_note(summary, keywords, pages, text)

    def _bibtex_from_user_input(self):
        self.fields = {"title": input("Title of the book: "),
                    # Authors need to be in the format $Lastname$, $initials of first names$ and $next_lastname$ etc.
                      "author": input("Names of the authors, separated by ' and ': "),
                      "editors": input("Names of the editors, separated by ' and ': "),
                      "year": input("Year of publication: "),
                      "publisher": input("Name of publisher: "),
                      "isbn": input("ISBN of the book: "),
                       "doi" : "None",
        }

        first_author = self.fields["author"].split(" and ")[0]
        shortie = (first_author.split(" ")[len(first_author.split(" "))-1] + "_" + self.fields["year"])

        self.bibtex = "@" + self.type_of_publication + "{" + shortie + ",\n"
        for i, __ in enumerate(list(self.fields.values())):
            self.bibtex += "\t" + list(self.fields.keys())[i] + " = {" + list(self.fields.values())[i] + "},\n"
        self.bibtex += "}"

    def _add_quotes_from_bibtex(self, array_of_quotes):
        for q in array_of_quotes:
            self._new_quote(q.split("__")[0], q.split("__")[1], q.split("__")[2], q.split("__")[3])