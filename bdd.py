import json
import csv
import sqlite3

con = sqlite3.connect("garanties.db")
cur=con.cursor()

# cur.execute("CREATE TABLE RE_Art_Nomenclature(id INTEGER NOT NULL PRIMARY KEY autoincrement,id_Nomenclature INTEGER,id_Article INTEGER,Quantite REAL)")
# cur.execute("CREATE TABLE RE_HistoSeries(id INTEGER NOT NULL PRIMARY KEY autoincrement,Modele text(50),Numero_Serie text(50),Numero_Immatriculation text(20), Date_vente date, Date_Debut_Garantie date, Duree_Garantie integer, Numero_Chassis text(50), Couleur text(20), Lien text(50))")
# cur.execute("CREATE TABLE RE_Nomenclatures(id INTEGER NOT NULL PRIMARY KEY autoincrement,Code_Nomenclature text(10),designation text(100),date_modif date, famille text(50))")


data=[("010","Révision des 1000 Km","2022-08-24","Révision"),("011","Changement d''une roue","2022-08-25","Model E"),("012","Changement du tableau de bord","2022-08-25","PRO50")]

#data=json.dumps(data)

# query="INSERT INTO [RE_Nomenclatures]([Code_Nomenclature],[designation],[date_modif],[famille]) VALUES(?,?,?,?)"

# cur.executemany(query,data)
# con.commit()

# for row in cur.execute("SELECT * FROM RE_Nomenclatures"):
#     print(row)

# with open('histo1.csv','r') as fin: # `with` statement available in 2.5+
#     # csv.DictReader uses first line in file for column headings by default
#     dr = csv.DictReader(fin) # comma is default delimiter
#     to_db = [(i['Modele'], i['Numero_Serie'],i['Numero_Immatriculation'],i['Date_vente'],i['Date_Debut_Garantie'],i['Numero_Chassis'],i['Couleur'],i['Lien']) for i in dr]

# cur.executemany("INSERT INTO RE_HistoSeries (Modele, Numero_Serie,Numero_Immatriculation,Date_vente,Date_Debut_Garantie ,Duree_Garantie,Numero_Chassis,Couleur) VALUES (?, ?,?,?,?,?,?,?);", to_db)
# con.commit()
# for row in cur.execute("SELECT * FROM RE_HistoSeries"):
#     print(row)



with open('nomen.csv','r') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['ï»¿id_Nomenclature'], i['id_Article'],i['Quantite']) for i in dr]
    print(to_db)

cur.executemany("INSERT INTO RE_Art_Nomenclature (id_Nomenclature, id_Article,Quantite) VALUES (?,?,?)", to_db)
con.commit()
for row in cur.execute("SELECT * FROM RE_Art_Nomenclature"):
    print(row)

con.close()
