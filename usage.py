import main as m

p = m.read_bibtex("<some location>/lit.bib")


print(p.publications)
p.list_publications()
p.list_keywords()
p.list_note_keywords()
p.quotes_with_keyword("GATC")
p.read_full_quote("GATC", 0)
