import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='MoralStrength',  
     version='1.0.0',
     scripts=['moralstrength', 'data', 'estimators', 'lexicon_use', 'moralstrengthdict'] ,
     author="Oscar Araque, Lorenzo Gatti and Kyriaki Kalimeri",
     author_email="o.araque@upm.es",
     description="A package to predict the Moral Foundations for a tweet or text",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/oaraque/moral-foundations/",
     packages=setuptools.find_packages(),
     license='LGPLv3',
     classifiers=[
     	 "Intended Audience :: Science/Research",
     	 "Natural Language :: English",
     	 "Topic :: Text Processing :: Linguistic",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
         "Operating System :: OS Independent",
     ],
     keywords='moral foundations NLP moralstrength',
	 project_urls={

	 },
	 install_requires=[
   		'gsitk',
		'nltk',
		'numpy',
		'pandas',
		'scikit-learn>=0.20.0,<0.21.0',
	],
	package_data={
	    'moralstrength': ['export'],
	},
     
 )