from bottle import*
from html.parser import HTMLParser
import requests
from lxml import etree as ET
from json import *
from re import *

#=============================== Récupération du fichier ==========================================

#Pour donner la possibilité de choisir le fichier à traiter en fonction des caractéristiques du PC
choix=0
while choix ==0:
    print('choix de fichiers à traiter :')
    print('1- Parsing dblp.xml')
    print('2- Parsing dblp_2020_2021.xml')
    print('3- Parsing dblp_2017_2021.xml')
    choix= int(input('choisir un chiffre : '))
    if choix ==1 :
        filename= 'dblp.xml'
    elif choix == 2:
        filename='dblp_2020_2021.xml'
    elif choix == 3:
        filename='dblp_2017_2021.xml'
    else : choix =0
    
#Dans notre cas nous avons utilisé 'dblp_2020_2021.xml' tronqué pour faire les tests (RAM insuffisante)    
try:
    Parser = ET.XMLParser(recover=True)
    Tree = ET.parse(filename,parser=Parser)
    root = Tree.getroot()    
except:
    print('must download ' +filename+ ' on your localhost')
    

publications = ['article','inproceedings','proceedings','book','incollection','phdthesis','mastersthesis']
target_Elements = ['author','title','year','journal','booktitle']
print(f"XML File loaded and parsed, root is {root.tag}")
url_conf= 'http://portal.core.edu.au/conf-ranks/'
url_jour='http://portal.core.edu.au/jnl-ranks/'

#=============================== Les fonctions ============================================

#Fonction pour vérifier la conformité des noms introduits par l'utilisateur
def check_name(name):
    
    regular = r'(([A-Z]{1}[a-z]+) ([A-Z]{1}([.][ ][A-Z])?[a-z]+)[ ]*[0-9]*){1}'
    
    if(fullmatch(regular, name)): 
         
        result = True
 
    else:
        result = False
    return result

Error_name = 'ERROR, le nom doit commmencer par une majuscule,sans caracteres speciaux'
Error_name+= ' et doit etre au format: Nom Prenom'
Error_distance = 'ERROR, la distance n existe pas pour ces deux auteurs'
Error_Start='ERROR, count et start doivent etre des nombres, pas de lettres ni de caractères spéciaux'
        
#Fonction de controle du nombre d'éléments à afficher : 100 éléments à la fois (au maximum)
def limit(List):    
     st= False
     co= False
     result = []
     try:     
         if  request.params.get('start') is not  None :
                start = int(request.params.get('start') )
                st= True

         if request.params.get('count') is not None :
                count = int (request.params.get('count'))
                co= True
         
         if st and co :
                 result = List[start+1:start+count+1]
                
                 if start > len(List):
                     result ='Error, there is no'+ start+'th element in List'
                 elif count > 100:
                     result= 'Error, you can only display 100 elements'
                 return result
                 
         elif st:     
             result = List[start+1:start+102]          
         else:
             if len(List)>=100:
                 
                 result = List[:101]
             else :
                 result = List             
     except TypeError or ValueError:
         
         result=Error_Start
    
     return result

#Fonction qui permet de récupérer l'auteur, ses publications ou ses co-auteurs
def getInfo_by_Author(name,choix):
       
       Nombres_pub_coth = []
       Nombres_pub_coth.append(name)
       Publications=[]
       Coauthors = []
       n_pub=0
       n_cauth=0
            
       for types in publications:
               
               for pubs in root.findall(types):
                   authors=pubs.findall(target_Elements[0]) #author
                   
                   for author in authors:
                       if(author.text == name):
                           Publications.append(pubs)
        
                           n_pub+=1
                           for coauthor in authors:
                               if not( coauthor.text == name):
                                   n_cauth+=1
                                   
                                   Coauthors.append(coauthor.text)
                        
       if choix == 'author':
           Nombres_pub_coth.append(n_pub)
           Nombres_pub_coth.append(n_cauth)
           return Nombres_pub_coth
       elif choix == 'publications':
           return Publications
       elif choix =='coauthor':
           return Coauthors

#Fonction qui calcule la distance entre 2 auteurs       
def distance(name_origin,name_destination):
    d=[]
    pubs= getInfo_by_Author(name_origin, 'publications')
    
    for pub in pubs:
              
            authors=pub.findall(target_Elements[0])#author
            found = False
            for author in authors:
                if(author.text == name_origin):
                    org= authors.index(author)
                   
                    
                elif (author.text== name_destination):
                        dest=authors.index(author)
                        found = True

#ajouter cette distance à une liste des distances possibles entre 2 auteurs                        
            if found:
                d.append(abs(dest-org))     
         
    if(len(d)!=0) :                                    
        result = min(d)        
    else:
        result = Error_distance
    return result

#Fonction qui permet de retrouver un auteur en introduisant une sous séquence de son nom 
def getAuthors_by_string(searchString):
    result=[]

    for t in publications:
        for pubs in root.findall(t):
            
            authors= pubs.findall(target_Elements[0])#author
            
            for author in authors:
                
                
                if( searchString != '*'):
                    
                    if  str(author.text).find(searchString.lower() )!=-1 or str(author.text).find(searchString.upper())!=-1 or str(author.text).find(searchString)!=-1  :
                      
                        result.append((author.text))       
                else:
                    result.append(author.text)
                                
    if len(result) !=0:
        result =list(set(result))
    else:
        result ='No result'
    print(len(result))
    
    return result

#=============================== Les routes ============================================

#Question1 : prendre en entrée le nom de l'auteur et retourner ['nom_auteur', nbr_publication, nbr_coauthors]
@route('/authors/<name>')  
def authors(name):
    validation = check_name(name)         #vérification de la conformité du nom
    if(validation): 
        result=getInfo_by_Author(name,'author') 
    else:         
       result = Error_name
    return dumps(result)


#Question2 : prendre en entrée le nom de l'auteur et retourner la liste de ses publications
@route('/authors/<name>/publications',method = 'GET')   
def list_pub(name):
    validation = check_name(name)         #vérification de la conformité du nom
    if validation:
        result=[]
        result_s=[]
        s = getInfo_by_Author(name,'publications')
        if len(s)!=0:
            for pub in s :
                result_s.append(pub.find('title').text)
                result = limit(result_s)
        else:
            result =['No result'] 
    else :  
        result = Error_name

    return dumps(result)

    

#Question4 : prendre en entrée le nom d'un auteur et retourner la liste de ses co-auteurs
@route('/authors/<name>/coauthors') 
def coauthors(name):
    validation = check_name(name)       #vérification de la conformité du nom
    if validation:
        s=getInfo_by_Author(name,'coauthor')
        if len(s)!=0:
            result = limit(s)
        else:
            result =['not found']
    else:
        result = Error_name
    
    return dumps(result)

#Question5 : Prendre une sous séquence et retourner tous les auteurs dont le nom contient cette séquence
@route('/search/authors/<searchString>') 
def search(searchString):
    result = getAuthors_by_string(searchString)
     
    return dumps(result)

#Question6 : Prendre en entrée le noms de 2 auteurs et retourner la distance les séparant 
@route('/authors/<name_origin>/distance/<name_destination>')
def dist(name_origin,name_destination):
    validation = check_name(name_origin) and check_name(name_destination) #vérification de la conformité des 2 noms
    if validation:
        print(name_origin,name_destination)
        result= distance(name_origin,name_destination)
        print(result)
    else:
        result= Error_name
    return dumps(result)


#Lancement du serveur accessible : https//localhost:8085
run(host='localhost', port=8085)

