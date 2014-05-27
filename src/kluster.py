#!/usr/bin/env python

from optparse import OptionParser, make_option
from itertools import izip, repeat
from random import choice, sample, random
from glob import glob 
from json import loads, dumps
from zlib import compress, decompress
from base64 import b64encode, b64decode
from os import path, pardir, curdir
from cPickle import dumps as serialize
from operator import itemgetter
from sys import argv, exit
from pprint import pprint
from math import sqrt
 
from vespse import Document, TermDocumentMatrix, Vector

class DocumentKluster(TermDocumentMatrix):


   def __init__(self, k= 3):

      super(DocumentKluster, self).__init__(idf_enabled= False)

      self.k= k

   def index(self):

      super(DocumentKluster, self).index()

      self.keys= sorted(super(DocumentKluster, self).keys())
 
      self.proximity_matrix= [map(lambda r: r[0], sorted(self.find(self[document_id]), key= lambda result: result[1][0])) for document_id in self.keys]

      self.find_centers(self.keys)

   def cluster_documents(self, centroids, keys):

      clusters= dict([(centroid, []) for centroid in centroids])
      
      for document_id in keys:

         document_index= keys.index(document_id)

         proximities= [min(self.proximity_matrix[document_index], key= lambda p: abs(p - centroid)) for centroid in centroids]
         nearest_centroid= centroids[proximities.index(max(proximities))]

         clusters[nearest_centroid].append(document_id)

      return clusters

   def has_converged(self, centroids, previous_centroids):

      converged= set(centroids) == set(previous_centroids)

      return converged

   def recompute_centroids(self, clusters):
 
      centroids= []
      for centroid, keys in clusters.items():
         proximities= [min(self.proximity_matrix[keys.index(key)], key= lambda p: abs(p - centroid)) for key in keys]

         # NOT SURE ABOUT THIS!!!!
         if proximities:
            centroid= sum(proximities) / float(len(proximities))

         centroids.append(centroid)
      
      return centroids

   def find_centers(self, keys= None):

      if not keys:
         keys= self.keys

      #centroids= [1.0 / ((i * len(keys)) / self.k) for i in range(1, self.k)]  
      centroids= [random() for i in range(self.k)]

      print centroids
      previous_centroids= []
      
      i=0 
      while not self.has_converged(centroids, previous_centroids):

         previous_centroids= centroids
         
         clusters= self.cluster_documents(centroids, keys)
         centroids= self.recompute_centroids(clusters)
         
      pprint(clusters)
        
 
def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-d", "--documents", default= path.join(pardir, "documents", "*.dat"), help= "documents directory"),
      make_option("-k", "--k", default= 3, type= int, help= "number of k clustering points")
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()

   return opts

if __name__ == '__main__':

   opts= parse_args(argv)

   dk= DocumentKluster(opts.k)

   i= 0
   for filename in glob(opts.documents):

      fh= open(filename, "r")
      data= fh.read()
      #data= decompress(b64decode(loads(fh.read()).get("payload")))
      fh.close()
      dk.add(data, id= filename)
      i+= 1
      if i >= 10:
         break
   
   dk.index()
