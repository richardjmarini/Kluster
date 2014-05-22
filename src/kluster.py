#!/usr/bin/env python

from optparse import OptionParser, make_option
from itertools import izip
from random import choice, sample
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

      self.k= 3

   def index(self):

      super(DocumentKluster, self).index()

      self.keys= sorted(super(DocumentKluster, self).keys())
 
      self.proximity_matrix= [map(lambda r: r[0], sorted(self.find(self[document_id]), key= lambda result: result[1][0])) for document_id in self.keys]

      self.find_centers(self.keys)

   def cluster_documents(self, centroids, keys):

      clusters= {}
      for document_id in keys:

         document_index= keys.index(document_id)
         centroid_indexes= [keys.index(centroid) for centroid in centroids]

         proximities= [self.proximity_matrix[document_index][centroid_index] for centroid_index in centroid_indexes]
         nearest_centroid= centroids[proximities.index(max(proximities))]

         try:
            clusters[nearest_centroid].append(document_id)
         except KeyError:
            clusters[nearest_centroid]= [document_id]

      return clusters

   def has_converged(self, centroids, previous_centroids):

      converged= set(centroids) == set(previous_centroids)

      return converged

   def recompute_centroids(self, clusters):
 
      centroids= []
      for document_id, keys in clusters.items():

         proximities= [self.proximity_matrix[keys.index(document_id)][keys.index(key)] for key in keys]
         
         centroid= sum(proximities) / float(len(proximities))

         centroids.append(centroid)

      return centroids

   def find_centers(self, keys= None):

      if not keys:
         keys= self.keys

      centroids= sample(keys, self.k)
      previous_centroids= []

      i=0 
      while not self.has_converged(centroids, previous_centroids):

         previous_centroids= centroids
         clusters= self.cluster_documents(centroids, keys)
         
         centroids= self.recompute_centroids(clusters)
         print centroids 
 
def parse_args(argv):

   optParser= OptionParser()

   [optParser.add_option(opt) for opt in [
      make_option("-d", "--documents", default= path.join(pardir, "documents", "*.dat"), help= "documents directory")
   ]]

   optParser.set_usage("%prog --query")

   opts, args= optParser.parse_args()

   return opts

if __name__ == '__main__':

   opts= parse_args(argv)

   dk= DocumentKluster()

   i= 0
   for filename in glob(opts.documents):

      fh= open(filename, "r")
      data= decompress(b64decode(loads(fh.read()).get("payload")))
      fh.close()
      dk.add(data)

      i+= 1
      if i >= 25:
         break
   
   dk.index()
