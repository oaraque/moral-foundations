
#load wikipedia page titles in wiki_pages and redirects in wiki_redirects
wiki_pages = {}
wiki_redirects = {}
with open('all_wiki_pages.tsv','r') as file:
	next(file) #skip header
	for line in file:
		#try:
			fields = line.strip().split("\t")
			if len(fields)<3:
				continue
			id = fields[0]
			is_redirect = fields[1]
			wikititle = fields[2]
			if is_redirect=='1':
				wiki_redirects[wikititle]=str(id)
			else:
				wiki_pages[wikititle]=str(id)
		#except:
		#	print('An exception has occurred')

print("Wikipedia titles loaded\n");

#create file for distinguishing between
#1. Exact matches (title wiki = title conservapedia)
#2. Conservapedia entry matches a wikipedia redirect
#3.  Conservapedia redirect matches a wikipedia entry
outfile = open('conserva_wiki_matches.tsv','w')
outfile.write('Conservapedia title\tConservapedia id\tExact_match\tConserva exact 2 Wiki redirect\tConserva redirects 2 Wiki exact\n')

#avoiding the redirect2redirect cause there can be many redirects in both resources
#and in general because I don't want to deal with it :P


with open('conservapedia_pages+redirects.tsv','r') as file:
	next(file) #skip header
	for line in file:
		fields = line.strip().split("\t")
		Cpageid=fields[0]
		Ctitle=str(fields[1])
		CtitleWiki = Ctitle.replace(" ","_")  #conservapedia title have spaces!
		from_ids = []
		from_titles = []
		outfile.write(Ctitle+'\t'+str(Cpageid)+'\t')
		if len(fields)>2:
			from_ids = fields[2].split("|")
			from_titles = fields[3].split("|")

		#check if title in wikipedia title
		if CtitleWiki in wiki_pages:
			outfile.write(wiki_pages[CtitleWiki]+'\t')
		else:
			outfile.write('NULL\t')

		#check if conservapedia page has matching wikipedia redirect
		if CtitleWiki in wiki_redirects:
			outfile.write(wiki_redirects[CtitleWiki]+'\t')
		else:
			outfile.write('NULL\t')
		
		#a redirect in conservapedia matches a title in wikipedia (might happen multiple times for same Ctitle, check output!)
		redirects = ""
		for alternativeCtitle in from_titles:
			alternativeCtitleWiki = alternativeCtitle.replace(" ","_")
			if alternativeCtitleWiki in wiki_pages:
				redirects = redirects + "|" + wiki_pages[alternativeCtitleWiki]
		if redirects == "":
			redirects = "NULL"
		else:
			redirects = redirects[1:]
		outfile.write(redirects+'\n')
outfile.close()