import main
from tqdm import tqdm

#TODO: Zwei Probleme: 1. bei gleichem shortie wird kein a... b... eingefügt. 2. Wenn ein paper zweimal in dem graph steht, dann wird es nur einmal entfernt
class BookshelfOfShame(main.BrainModule):
    def __init__(self, location, motherbib):
        self.location = location
        self.motherbib = motherbib
        literature_data, citation_data = self.read_input_file(location)
        self.shame_bib = self.handle_bibtex_part(literature_data)
        self.citation_graph = self.handle_graph_part(citation_data)
        self.counted_mention_dict = self._count_mentions_in_citation_graph()


    def read_input_file(self, location):
        lit = []
        cit = []
        discriminator = True
        for i, line in enumerate(open(location)):
            if line == "##\n":
                discriminator = False
            elif discriminator:
                lit.append(line)
            else:
                cit.append(line)


        return lit, cit


    def handle_bibtex_part(self, list_of_lines):
        record = []
        bib = main.open_empty_library()
        for i, line in enumerate(list_of_lines):
            if "quote = {" in line or "note = {" in line:
                record.append(line.replace(",\n", "").replace("\n", ""))
            else:
                record.append(line.replace(",\n", "").replace("\n", "").replace(", ", ""))
            if line == "}\n" or line == "}":
                typedict = {subclass.type_of_publication: subclass for subclass in
                            main.Publication.Publication.__subclasses__()}
                publication = typedict[record[0].split("{")[0][1:]](record, "READ_BIBTEX", bib)
                bib.append_publication(publication)
                record = []
        return bib


    def handle_graph_part(self, list_of_lines):
        graph = {}
        for line in list_of_lines:
            if ":" in line:
                if line.split(":")[0] == "":
                    motherpaper = ""
                else:
                    motherpaper = [paper for paper in self.motherbib.publications
                               if paper.short_identifier == line.split(":")[0]][0]

                daughters = []
                for unreadpaper in line.split(": ")[1].strip().split(", "):
                    daughters.append([paper for paper in self.shame_bib.publications if paper.short_identifier == unreadpaper][0])
                graph[motherpaper] = daughters
            else:
                daughters = []
                for unreadpaper in line.strip().split(", "):
                    daughters.append(
                    [paper for paper in self.shame_bib.publications if paper.short_identifier == unreadpaper][0])
                graph[None] = daughters
        return graph


    def _count_mentions_in_citation_graph(self):
        count_dict = {}
        for mother in self.citation_graph:
            for daughter in self.citation_graph[mother]:
                if daughter in count_dict:
                    count_dict[daughter] += 1
                else:
                    count_dict[daughter] = 1
        return count_dict


    def list_sorted(self):
        print("Index\tMentions\tPaper")
        for i, paper in enumerate(sorted(self.counted_mention_dict, key=lambda x:self.counted_mention_dict[x])[::-1]):
            print(str(i+1) + "\t" + str(self.counted_mention_dict[paper]) + "\t" + str(paper))


    def save_to_location(self, location):
        #TODO: Remove commented lines
        #self.shame_bib.export_as_bibtex(location, verbose=False)
        print("Saving the bookshelf of shame... ")
        self.shame_bib.export_as_bibtex(location)
        handle = open(location, "a")
        handle.write("##")
        #for part in self.citation_graph:
        for part in tqdm(self.citation_graph, desc="Saving the citation graph... ", unit=" ",
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} lines"):
            if part is None:
                handle.write("\n" +
                             ", ".join([paper.short_identifier for paper in self.citation_graph[part]]))
            elif self.citation_graph[part]:
                if isinstance(part, str):
                    handle.write("\n" + part + ": " +
                                 ", ".join([paper.short_identifier for paper in self.citation_graph[part]]))
                else:
                    handle.write("\n" + part.short_identifier + ": " +
                             ", ".join([paper.short_identifier for paper in self.citation_graph[part]]))
        print()


    def find_and_remove_paper(self, paper_to_remove):
        if paper_to_remove in self.shame_bib.publications:
            del self.shame_bib.publications[
                [i for i, paper in enumerate(self.shame_bib.publications) if paper_to_remove == paper][0]]
        for part in self.citation_graph:
            if paper_to_remove in self.citation_graph[part]:
                del self.citation_graph[part][
                    [i for i, paper in enumerate(self.citation_graph[part]) if paper_to_remove == paper][0]]
                if len(self.citation_graph[part]) == 0:
                    self.citation_graph.pop(part, None)
        self.counted_mention_dict = self._count_mentions_in_citation_graph()


    def save(self):
        self.save_to_location(self.location)


    def add_information_on_paper(self, paper):
        # Removing all mentions of _paper_ out of the self.citation_graph
        self.find_and_remove_paper(paper)
        if paper not in self.citation_graph:
            self.citation_graph[paper] = []

        ##Adding some more papers to the bookshelf of shame
        goOn = (input("Add a paper to the Bookshelf Of Shame? (y/n) ").lower() == "y")
        while goOn:
            self.shame_bib.add_a_publication()
            if self.shame_bib.latest_paper in self.motherbib.publications:
                print("Already in the motherbib.")
                del self.shame_bib.publications[-1]
                self.shame_bib.latest_paper = self.shame_bib.publications[-2]
            else:
                print(self.shame_bib.latest_paper)
                self.citation_graph[paper].append(self.shame_bib.latest_paper)
            self.save()
            goOn = (input("Add another paper to the Bookshelf Of Shame? (y/n) ").lower() == "y")

        self.counted_mention_dict = self._count_mentions_in_citation_graph()


    def add_paper(self, paper):
        self.find_and_remove_paper(paper)
        #TODO: Do I really need this "save"?
        #self.save()


    def add_without_mother(self, paper):
        self.shame_bib.add_publication_from_bibtex(paper.bibtex.split(",\n"))

        try:
            self.citation_graph[""].append(self.shame_bib.latest_paper)
        except KeyError:
            self.citation_graph[""] = [self.shame_bib.latest_paper]



#TODO: Sometimes, this just doesn't write a paper to the bos...