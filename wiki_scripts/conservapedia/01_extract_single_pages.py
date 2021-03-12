import json
import glob
import xml.etree.ElementTree as ET
import os.path

print("""
This script opens the set of pages downloaded in ./xmls and splits them
as individual pages in ./xml_pages.

It also writes a report in with all the IDs that were downloaded, 
the type of page (normal/redirect/disambiguation) and more.""")

with open("conservapedia_downloaded_pages.tsv", "w") as outreportf: 
	outreportf.write("Page type ({N}ormal/{R}edirect/{D}isambiguation)\tPageID\tPage Title\tRedirects to (if type is R)\n");
	for filename in glob.iglob("xmls/*.xml"):
		xmlfile = open(filename, "r")
		xml_content = xmlfile.readlines()
		xmlfile.close()
		#remove namespace crap
		xml_content[0] = "<mediawiki>"
		xml_content = "".join(xml_content)
		root = root = ET.fromstring(xml_content)
		for page in root.findall("page"):
			text = page.find('revision').find('text').text
			type = "N"
			title = page.find('title').text
			redirectsTo = ''
			pageID = page.find('id').text
			if "''' may refer to:\n" in text:
				type = "D"
				#f.write("Disambiguation:\t"+page.find('title').text + "\t" + page.find('id').text)
			if page.find('redirect') is not None:
				type = "R"
				redirectsTo = page.find('redirect').get('title')
			outreportf.write(type+'\t'+pageID+'\t'+title+'\t'+redirectsTo+'\n')

			individual_pagename = "xml_individual_pages/"+pageID+".xml"
			if os.path.exists(individual_pagename):
				continue
			with open(individual_pagename, "w") as outxmlfile:
				outxmlfile.write("<mediawiki>\n"+ET.tostring(page,encoding="unicode")+"\n</mediawiki>")
print("Report written to 'conservapedia_downloaded_pages.tsv'")