import lcpunit
import lcpxlsx
import os
import zenodotus
import requests
import json
import sys


# path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Neilreichia\\v11"
#path = "C:\\Users\\poa\\Documents\\programming\\lycophron\\projects\\grazia"
# path = "C:\\Users\\poa\\Desktop\\grazia"

# 2021-05-10
# path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i7"
# file = 'Notulae_odonatologicae_v9_i7.xlsx'

# path = 'C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Odonatologica\\v50\\i1-2'
# file = 'Odonatologica_v50_i1-2-edited.xlsx'

# 2021-06-21
# path = 'C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Revue_de_Paleobiologie\\v40\\i1'
# file = 'DOI_RPaleo_40_1_2021-edited.xlsx'

# # 2021-11-15
# path = 'C:\\Users\\guidoti_plazi\\Documents\\services\\doi-registration-service\\Notulae\\v9\\i8'
# file = 'Notulae_odonatologicae_v9_i8-edited.xlsx'

# import os 

# print(os.getcwd())

# 2022-02-08
path = 'C:\\Users\\guidoti_plazi\\Documents\\services\\doi-registration-service\\Revue_de_Paleobiologie\\v41\\i1'
file = 'Doi_RPaleo_41_1_2022_dois.xlsx'

# Checking and changing directory
# print(os.getcwd())
# os.chdir(path)
# print(os.getcwd())

# file = "Neilreichia_v11-edited.xlsx"
# file = "grazia-festschrift-to_Zenodo-2nd_es.xlsx"
# file = "grazia-festschrift-to_Zenodo-eddited_cc-by-Reconciled-Fixed-Combined-Authors_Fixed.xlsx"

file_path = path + "\\" + file

db = lcpxlsx.Xls(file_path)

headers = {"Content-Type": "application/json"}

#print(db.get_all_papers())

# print(db.define_action())
# zenodotus.push_data(db, sandbox="on", marcus="on")
zenodotus.push_data(db, sandbox="off", marcus="off")
#zenodotus.push_PDFs(db, sandbox="off", marcus="off")
#zenodotus.publish(db)