import xml.etree.ElementTree as ET
import glob
import pdb
import os.path

for xmlfile in glob.glob('*.xml'):
#	print(xmlfile)
	mytree = ET.parse(xmlfile);
	root = mytree.getroot()

	for page in root.iter('page'):
		#page/id
		id =  page.find('id').text
#		print('\t'+str(id))
		text = page.find('revision').find('text').text
		outfilename = 'wikimarkup/'+str(id)+'.wiki'
		
		if os.path.exists(outfilename):
			print("duplicated file "+outfilename);
		else:
			 with open(outfilename,'w') as outf:
			 	outf.write(text)

		