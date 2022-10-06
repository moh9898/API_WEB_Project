#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 15:39:56 2021

@author: mohamed"""

from requests import *
from json import *
import unittest

class TestAPIMethods(unittest.TestCase):
    server_ip= "127.0.0.1"
    server_port = 8085

#Vérifier que la route 1 renvoit bien Daniel Gruss avec 13 publications et 68 co-auteurs
    def test_authors(self):
        req = get(f"http://{self.server_ip}:{self.server_port}/authors/Daniel Gruss")
        result = loads(req.text)
        self.assertEqual(result[0],'Daniel Gruss')
        self.assertEqual(result[1],13)
        self.assertEqual(result[2],68)

#Vérifier que l'auteur Daniel Gruss possède 13 publications
    def test_publications(self):
        req = get(f"http://{self.server_ip}:{self.server_port}/authors/Daniel Gruss/publications")
        result= loads(req.text)
        self.assertEqual(len(result),13)

#Vérifier que l'auteur Daniel Gruss à bien 68 co-auteurs                
    def test_coauthors_by_name(self):
        r1 = get(f"http://{self.server_ip}:{self.server_port}/authors/Daniel Gruss/coauthors")
        l = loads(r1.text)
        self.assertEqual(len(l), 68)

#Vérifier que la sous séquence 'Daniel' est présente dans 2763 noms d'auteurs
    def test_search_authors(self):
        r3 = get(f"http://{self.server_ip}:{self.server_port}/search/authors/Daniel")
        l3 = loads(r3.text)
        self.assertEqual(len(l3),2763)
 
#Vérifier que 5 publications de l'auteur Wei Wei ont été affichées uniquement (à partir de la 50ème publication)       
    def test_start_count(self):
        req = get(f"http://{self.server_ip}:{self.server_port}/authors/Wei Wei/coauthors?start=50&count=5")
        result= loads(req.text)
        self.assertEqual(len(result),5)

#Vérifier que la distance minimale entre Daniel Gruss et Daniel Genkin est égale à 1            
    def test_distance(self):
        req = get(f"http://{self.server_ip}:{self.server_port}/authors/Daniel Gruss/distance/Daniel Genkin")
        result= loads(req.text)
        self.assertEqual(result,1)
                
        
if __name__ == '__main__':
    unittest.main()
    
    

