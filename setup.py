import io
import setuptools

VERSION = '0.2.7'

with open("README.md", "r") as fh:
    long_description = fh.read()

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    with io.open(filename, 'r') as f:
        lineiter = list(line.strip() for line in f)
    return [line for line in lineiter if line and not line.startswith("#")]

install_reqs = parse_requirements("requirements.txt")

setuptools.setup(
     name='moralstrength',
     packages=['moralstrength'],
     version=VERSION,
     #scripts=['moralstrength', 'data', 'estimators', 'lexicon_use', 'moralstrengthdict'] ,
     author="Oscar Araque, Lorenzo Gatti and Kyriaki Kalimeri",
     author_email="o.araque@upm.es",
     description="A package to predict the Moral Foundations for a tweet or text",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/oaraque/moral-foundations/",
     download_url='https://github.com/gsi-upm/gsitk/tarball/{}'.format(VERSION),
     license='LGPLv3',
     classifiers=[
     	 "Intended Audience :: Science/Research",
     	 "Natural Language :: English",
     	 "Topic :: Text Processing :: Linguistic",
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
         "Operating System :: OS Independent",
     ],
     keywords=['moral foundations', 'NLP', 'moralstrength', 'machine learning'],
	 install_requires=install_reqs,
    include_package_data=True,
 )
