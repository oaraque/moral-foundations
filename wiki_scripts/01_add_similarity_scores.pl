from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import glob
import pdb
import os.path
import spacy

nlp = spacy.load("en_core_web_trf", exclude=["ner", "parser"])




#iterator to avoid reading everything in memory
class readAlignedDocs():
	def __iter__(self):
		filenames = glob.glob('aligned/exact/*.wiki')
		filenames.extend(glob.glob('aligned/exact/*.conserva'))
		filenames.extend(glob.glob('aligned/redirects/*.wiki'))
		filenames.extend(glob.glob('aligned/redirects/*.conserva'))
	
		for i, filename in enumerate(filenames):
			filename_nopath = os.path.basename(filename)
			with open(filename) as f:
				content = f.read()
				toks = nlp(content)
				tokens = [tok.lemma_ for tok in toks]
				yield(TaggedDocument(tokens, [filename_nopath]))


trainingcorpus = readAlignedDocs()
print("Starting doc2vec training...")
model = Doc2Vec(trainingcorpus, vector_size = 300, workers = 4)
model.save('doc2vec_trained.model')