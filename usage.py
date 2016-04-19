import main as m

p = m.read_bibtex("<some location>/lit.bib")

print(p.publications)
p.list_publications()
p.list_keywords()
p.list_note_keywords()

p.quotes_with_keyword("GATC")
p.read_full_quote("GATC", 0)

p.latest_paper
p.latest_paper.list_keywords()

p.search_in_quotes("bacteria")


p.add_a_publication()
p.add_publication_with_doi("10.1093/femsre/fuv030")

p.latest_paper

p.latest_paper.add_a_quote()
p.latest_paper.add_a_quote_complex()

p.latest_paper.add_a_note()

p.save()
p.open_empty_library()
