from wsgiref import headers
from flask import Flask, render_template, request, flash,url_for,jsonify
from flask_cors import CORS
from uuid import uuid4
import xmlrpc.client,logging
import json
import pandas as pd

app=Flask(__name__)
app.secret_key="E8FDHCGP98FGQDPGF"
CORS(app)

@app.route('/create_client',methods=['GET'])
def create_partner():
    if request.method=="GET":
        url = "https://redelect-redegroup.odoo.com"
        db = "redelect-redegroup-production-3942603"
        username = 'philippe.herrgott@redelectric.fr'
        password = "7f7b8ef9643baf48c7d7603a70d58da646ed70b2"

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        #sales_clients=pd.DataFrame(models.execute_kw(db, uid, password, 'sale.order', 'fields_get', [],{'attributes': ['required']}))

        #sales_clients=sales_clients.transpose()
        #print(sales_clients)

        #sales_clients=sales_clients[(sales_clients['required']==True)]
        
        sales_clients=pd.DataFrame(models.execute_kw(db, uid, password, 'sale.order', 'search_read', [[['id','=',690]]],{'fields': ['name','date_order','partner_id','partner_invoice_id','partner_shipping_id','pricelist_id','company_id','picking_policy','warehouse_id']}))


        id=models.execute_kw(db,uid,password,'sale.order','create',[{'name':'test','date_order':'2022-08-18','partner_id':3,'partner_invoice_id':3,'partner_shipping_id':3,'pricelist_id':2,'company_id':1,'picking_policy':'direct','warehouse_id':1}])
        print(id)

        return sales_clients.to_json(orient = 'columns')            




if __name__ == "__main__":
    app.run(debug=True)

