from distutils.core import setup

from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'graphoW',        
  packages = ['graphoW'],  
  version = '0.4',     
  license='apache-2.0',      
  description = 'graphoW is a Python package for the creation of a Graph-of-Words (GoW) representation of texts.',  
  author = 'Antonela Tommasel',                  
  author_email = 'antonela.tommasel@isistan.unicen.edu.ar',     
  url = 'https://github.com/tommantonela/graphoW',   
  download_url = 'https://github.com/tommantonela/graphoW/archive/v_04.tar.gz',  
  keywords = ['graph-of-words', 'text analysis', 'natural language processing'],   
  install_requires=[  
            'matplotlib',
            'networkx',
            'karateclub',
            'sklearn',
            'spacy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: Linguistic',
    'License :: OSI Approved :: Apache Software License',   
    'Natural Language :: English',
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.7',
  ],
  long_description=long_description,
  long_description_content_type='text/markdown'
)