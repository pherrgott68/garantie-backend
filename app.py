from pdb import line_prefix
from tkinter.tix import Select
from wsgiref import headers
from flask import Flask, render_template, request, flash,url_for,jsonify
from flask_cors import CORS
from uuid import uuid4
import xmlrpc.client,logging
import sqlite3
import json
import pandas as pd

app=Flask(__name__)
app.secret_key="E8FDHCGP98FGQDPGF"
CORS(app)

#Connexion ODOO
url = "https://redelect-redegroup.odoo.com"
db = "redelect-redegroup-production-3942603"
username = 'philippe.herrgott@redelectric.fr'
password = "7f7b8ef9643baf48c7d7603a70d58da646ed70b2"




@app.route('/Garantie/<client_id>',methods=['POST','GET'])
def client(client_id):
    if request.method=="GET":


        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        #Chargement de tous les numéros
        serie_clients=pd.DataFrame(models.execute_kw(db, uid, password, 'stock.production.lot', 'search_read', [[]], {'fields': ['product_id', 'name','sale_order_count','sale_order_ids']}))
        condition_r = serie_clients[(serie_clients['sale_order_count'] == 1)]
        condition_r = condition_r['sale_order_ids'].str.get(0).values.tolist()
        
        #traitement des numéros de commandes
        sales_clients=pd.DataFrame(models.execute_kw(db, uid, password, 'sale.order', 'search_read', [[['id','=',condition_r]]], {'fields': ['invoice_status', 'partner_id','date_order']}))
        if client_id==str(3):
            client_id=7696


        #Traitement des numéros de séries achetés par le client
        condition_s=sales_clients[(sales_clients['partner_id'].str.get(0)==client_id)]
        condition_s = condition_s['id'].values.tolist()
        serie_clients=serie_clients[(serie_clients['sale_order_ids'].str[0].isin(condition_s))]

        #Retour
        return  serie_clients.to_json(orient = 'records')


@app.route('/login',methods=['POST'])
def login():
        #Connexion ODOO
        token = request.get_json()
        username = token['username']
        password = token['password']
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        common.version()
        uid = common.authenticate(db, username, password, {})
        if uid:
            token["token"]=str(uuid4())
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            User_c=models.execute_kw(db, uid, password, 'res.users', 'read', [uid], {'fields': ['login', 'partner_id']})
            idc=User_c[0]['partner_id'][0]
            Client_c = models.execute_kw(db,uid,password,'res.partner','read',[idc],{'fields': ['company_name','street','street2','zip','city']})
            token["Partner"]=Client_c
        else:
            token={'erreur':'erreur'}
        return json.dumps(token)
                

@app.route('/Histo/<numero_serie>',methods=['POST','GET'])
def histo(numero_serie):
    #Connexion base SQLite
    con = sqlite3.connect("garanties.db",check_same_thread=False)
    cur=con.cursor()

    result=[]
    #requete
    query="SELECT * FROM RE_HistoSeries WHERE Numero_Serie LIKE '%" + numero_serie + "%' LIMIT 50;"
    print(query)
    result = pd.read_sql(query,con)
    
    return result.to_json(orient = 'records')


#####Gestion des nomenclatures
##Nomenclatures entêtes
@app.route('/Nomenclatures/',methods=['POST','GET'])
def getNomenclatures():

    #Connexion base SQLite
    con = sqlite3.connect("garanties.db",check_same_thread=False)
    cur=con.cursor()

    query="select * from RE_Nomenclatures order by Code_Nomenclature"
    result = pd.DataFrame(pd.read_sql(query,con))
    return result.to_json(orient='records')


##Nomenclature : Get
@app.route('/Nomenclature/<Id_nomenclature>', methods=['GET'])
def getNomenclature(Id_nomenclature):
    
    #Connexion
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    #Connexion base SQLite
    con = sqlite3.connect("garanties.db",check_same_thread=False)
    cur=con.cursor()
    

    #Chargement des articles
    query= "select id,cast(id_article as integer) as id_article,Id_Nomenclature,Quantite from RE_art_Nomenclature where id_Nomenclature=" + Id_nomenclature
    Lien_ODOO = pd.DataFrame(pd.read_sql(query,con))

    M=Lien_ODOO['id_article'].to_list()

    Article_Nom_ODOO = pd.DataFrame(models.execute_kw(db, uid, password, 'product.template', 'search_read', [[['id','=',M]]], {'fields': ['default_code', 'name','list_price']}))


    ret = Lien_ODOO.merge(
        Article_Nom_ODOO,
        left_on='id_article', right_on='id'
          )

    return ret.to_json(orient='records')


##Nomenclature: Update
@app.route('/U_Nomenclature', methods=['POST','GET'])
def U_Nomenclature():
    data=request.get_json()
    #Connexion base SQLite
    con = sqlite3.connect("garanties.db",check_same_thread=False)
    cur=con.cursor()

    #requete
    if data['isNew']==True:
        query="INSERT INTO RE_Art_Nomenclature(id_nomenclature,id_article,quantite) VALUES ({0},{1},{2}) ;".format(data['id_nomenclature'],data['id_article'],data['quantite'])
    else:
        query="update RE_Art_Nomenclature set id_Article={0}, Quantite={1} where id = {2} ;".format(data['id_article'],data['quantite'],data['id'])

    result = cur.execute(query)
    con.commit()

    return result

##Nomenclature: Delete
@app.route('/D_Nomenclature', methods=['POST','GET'])
def D_Nomenclature():

    #Connexion base SQLite
    con = sqlite3.connect("garanties.db",check_same_thread=False)
    cur=con.cursor()

    data=request.get_json();
    #requete
    query="Delete from RE_Art_Nomenclature where id = {0} ;".format(data)
    print(query)
    result = cur.execute(query)
    con.commit()
    return result

#######################################

#################Articles
@app.route('/Articles/', methods=['GET'])
def getArticles():
    
    #Connexion
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    #Chargement des articles
    Articles_ODOO = pd.DataFrame(models.execute_kw(db, uid, password, 'product.template', 'search_read', [[]], {'fields': ['default_code', 'name']}))
    Articles_ODOO["value"]=Articles_ODOO["id"]  
    Articles_ODOO["label"]=Articles_ODOO["default_code"].map(str)  + " " + Articles_ODOO["name"]
    mycolumns=['value','label']

    return Articles_ODOO[mycolumns].sort_values(by=['label']).to_json(orient='records')



if __name__ == "__main__":
    app.run(debug=True)

