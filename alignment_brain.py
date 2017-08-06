import main
import os

class AlignmentBrain(main.BrainModule):
    #Writes a table in which algorithms are described.


    def __init__(self, table_location, motherbib):
        self.library = motherbib
        self.info = self.read_info(table_location)
        self.location = table_location


    def read_info(self, location):
        self.data = []
        for i, line in enumerate(open(location)):
            if i == 0:
                self.description = line.strip().split("\t")
            else:
                ##TODO: Throw an error if the paper is not findable
                thispaper = [paper for paper in self.library.publications
                             if paper.short_identifier == line.strip().split("\t")[1]][0]
                thisline = [line.strip().split("\t")[0], thispaper]
                for j, part in enumerate(line.strip().split("\t")[2:]):
                    if part == "None":
                        thisline.append(None)
                    elif self.description[j+2].split("(")[1][0] == "b":
                        thisline.append(part == "True")
                    elif self.description[j+2].split("(")[1][0] == "i":
                        thisline.append(int(part))
                    elif self.description[j + 2].split("(")[1][0] == "f":
                        thisline.append(float(part))
                    elif self.description[j + 2].split("(")[1][0] == "s":
                        thisline.append(part)
                self.data.append(thisline)


    def save_to_location(self, location):
        handle = open(location, "w")
        handle.write("\t".join(self.description))
        for line in self.data:
            handle.write("\n" + line[0] + "\t" + str(line[1].short_identifier))
            for i, part in enumerate(line[2:]):
                handle.write("\t" + str(part))


    def add_algorithm(self, paper = None):
        def ask_for_input_for_field(alg_name, category):
            answer = input("Input information on '" + category + "' for algorithm " + alg_name + ". ")
            if category.split("(")[1][0] == "b":
                return answer == "True"
            elif category.split("(")[1][0] == "i":
                return int(answer)
            elif category.split("(")[1][0] == "f":
                return float(answer)
            elif category.split("(")[1][0] == "s":
                return answer


        name = input("Name of the algorithm? ")
        newline = [name]
        if paper:
            newline.append(paper)
        else:
            papershortie = input("Please input the short ID of the resp. paper. ")
            newline.append([p for p in self.library.publications if p.short_identifier == papershortie][0])

        for i, part in enumerate(self.description[2:]):
            newline.append(ask_for_input_for_field(name, part))

        new_categories = False
        goOn = (input("Add a new category for this algorithm? (y/n) ").lower() == "y")
        if goOn:
            new_category = True
        else:
            new_category= False
        while goOn:
            newcategory = self.add_category()
            newline.append(ask_for_input_for_field(name, newcategory))
            goOn = (input("Add another new category for this algorithm? (y/n) ").lower() == "y")
        self.data.append(newline)

        return new_categories


    def add_category(self):
        answer = input("What field, what category do you want to add? ")
        type = input("Choose a type? (b/i/f/s) ")
        self.description.append(answer + "(" + type + ")")
        self.update_categories()
        return answer + "(" + type + ")"


    def update_categories(self):
        for i, line in enumerate(self.data):
            if len(self.data[i]) < len(self.description) or self.data[i][::-1] == None:
                answer = input("What is the property of '" + self.data[i][0] + "' in the category '" + str(self.description[-1]) + "'? ")
                self.data[i].append(answer)


    def save(self):
        #TODO: This seems to be broken....
        self.save_to_location(self.location)


    def add_information_on_paper(self, paper):
        goOn = (input("Add an algorithm for this paper? (y/n) ").lower() == "y")
        new_category = False
        while goOn:
            self.add_algorithm(paper=paper)
            goOn = (input("Add another algorithm for this paper? (y/n) ").lower() == "y")


    def add_paper(self, paper):
        None


#lib = main.read_bibtex("/home/sperlea/Uni/Masterarbeit/lit.bib")
#ab = AlignmentBrain("/home/sperlea/stuff/writing/alignments/infosammlung/info", lib)
#ab.add_information_on_paper(lib.latest_paper)
#ab.save_to_location("/home/sperlea/stuff/writing/alignments/infosammlung/info_2")
