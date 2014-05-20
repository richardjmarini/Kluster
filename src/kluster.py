#!/usr/bin/env python

from itertools import izip
from random import choice, sample
from glob import glob 
from json import loads, dumps
from zlib import compress, decompress
from base64 import b64encode, b64decode
from os import path
from cPickle import dumps as serialize
from operator import itemgetter
 
from vespse import Document, TermDocumentMatrix, Vector

docdir= "../documents"

class DocumentKluster(TermDocumentMatrix):


   def __init__(self, docdir, k= 3):

      super(DocumentKluster, self).__init__()

      self.k= 3

   def index(self):

      super(DocumentKluster, self).index()

      keys= sorted(super(DocumentKluster, self).keys())
 
      self.proximity_matrix= izip(keys, [sorted(self.find(self[document_id]), key= lambda result: result[1][0]) for document_id in keys])
      print list(self.proximity_matrix)
            

if __name__ == '__main__':

   dk= DocumentKluster(docdir= docdir)

   i= 0
   for filename in glob(path.join(docdir, "*.dat")):

      fh= open(filename, "r")
      data= decompress(b64decode(loads(fh.read()).get("payload")))
      fh.close()
      dk.add(data)

      i+= 1
      if i >= 25:
         break
   
   dk.index()
