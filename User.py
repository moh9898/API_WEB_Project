#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 22:52:44 2021

@author: mohamed
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 15:02:12 2021

@author: mohamed
"""
from bottle import route, request, run
from json import *
from requests import get
server_ip = "127.0.0.1"
server_port = 8085

def disp_List(resultat):
    resultat = resultat.strip('[')
    resultat = resultat.strip(']')
    resultat= resultat.replace('"','')
    result = resultat.split(",")
    if result != ['']:
        result = sorted(result)
        Titre = ""
        Tabp='<table border="1" cellpadding="10" cellspacing="1" width="100%">'
        for j in result:
                Titre+='<tr><td>'
                Titre+=str(j)
                Titre+='</tr></td>'
        Tabp+=Titre+'</table>'
        
        return Tabp
    else:
        print(result)
        result ='No result'
        return result



def check_error(resultat):
    if(resultat.find('ERROR')!= -1):
        resultat = loads(resultat)
    
        Tab='<table border="1" cellpadding="10" cellspacing="1" width="100%"><tr><th>Solution</th>' 
        Tab+=f'<tr><td>{resultat}</td></tr>'         
        Tab+= '<html><body>'+'<BODY BGCOLOR="#FF0000">'+Tab+'</body></html>' 
        return [Tab,'']
    else:
        return resultat
    



@route("/home", method=['GET','POST'])
def home():
	return '''
	<form action="/input" method="post">
		<h4> Rechercher un auteur par chaine de caractères: </h4>
		<a href="/input_car"><input type="button" value="rechercher" /></a>
		<h4> Affichage des publications et de coauteurs d'un auteur: </h4>
		<a href="/input_auteur"><input type="button" value="Publications et coauteurs" /></a>
		<h4> Afficher la distance entre deux auteurs </h4>
		<a href="/input_auth_d"><input type="button" value="Distance" /></a>
		</form>
		'''

@route("/input_car")
def input_car():
	return '''
		<form action="/input_car" method="post">
		<h4> Donner une chaine de caracteres </h4>
		recherche: <input name="char" type="text" />
		<input value="Search" type="submit" />
		</form>
		'''

@route("/input_car", method='POST')

def on_input_car():
    recherche = request.forms.getunicode('char')
    req = get(f"http://{server_ip}:{server_port}/search/authors/{recherche}")
    result= disp_List(req.text)
    return f"<h2> Auteurs contenant '{recherche}' : {result} </h2> "
    
    

@route("/input_auteur")

def input_auteur():
	return '''
		<form action="/input_auteur" method="post">
		<h4> Donner le nom d'un auteur </h4>
		Auteur : <input name="name" type="text" />
		<input value="Search" type="submit" />
		</form>
		'''
        
@route("/input_auteur", method='POST')
def on_intput_auteur():
    
    name= request.forms.getunicode('name')
    req=get(f"http://{server_ip}:{server_port}/authors/{name}/publications")
    req1=get(f"http://{server_ip}:{server_port}/authors/{name}/coauthors")
    ce=check_error(req.text)
    ce1=check_error(req1.text)
    if len(ce)==2 and len(ce1)==2:
        return ce[0]+ce1[0]
    else: 
        tri=disp_List(req.text)
        tri2=disp_List(req1.text)
        return f"<h2>Publications de <<{name}>> triés : {tri} </h2> <h2> les co-auteurs de ><{name}>> triés: {tri2} </h2>"


	
@route("/input_auth_d")
def input_auth_d():
	return '''
		<form action="/input_auth_d" method="post">
		<h4> Donner deux noms d'auteurs  </h4>
		Origin name: <input name="auteur1" type="text" />
		Destination name: <input name="auteur2" type="text" />
		<input value="Distance" type="submit" />
		</form>
		'''

@route("/input_auth_d", method='POST')
def on_input_aut_d():
    auteur_1= request.forms.getunicode('auteur1')
    auteur_2= request.forms.getunicode('auteur2')
    req=get(f"http://{server_ip}:{server_port}/authors/{auteur_1}/distance/{auteur_2}")
    ce=check_error(req.text)
    if len(ce)==2:
        return ce[0]
    else:
        result= loads(req.text)
        return f"<h3> La distance entre <<{auteur_1}>> et <<{auteur_2}>> est : {result} </h3> "

	
	
run(host='localhost', port=8099)

