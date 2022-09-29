import lcpunit
import lcpxlsx
import os
import zenodotus
import requests
import json
import sys

#sys.stdout.reconfigure(encoding='utf-8')

#path = "C:\\Users\\Marcus\\projects\\work\\plazi\\doi-registration-service\\Revue_Suisse_de_Zoologie\\v126\\i2"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Odonatologica\\v48\\i3-4\\"

#path = "C:\\Users\\poa\\Documents\\Fabricius"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Odonatologica\\v48\\i3-4"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i4"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Revue_de_Paleobiologie\\v38\\i2"

#path = "C:\\Users\\Marcus\\projects\\work\\plazi\\doi-registration-service\\Conferences\\International_Symposium_of_Neuropterology\\XIII"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i5"
#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Odonatologica\\v49\\i1-2"
# path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Revue_de_Paleobiologie\\v39\\i2"
path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i7"

#path = "C:\\Users\\Marcus\\projects\\work\\plazi\\doi-registration-service\\Odonatologica\\v48\\i3-4"

#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i6"
#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Odonatologica\\v49\\i1-2"
#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Neilreichia\\v11"
#path = "C:\\Users\\poa\\Documents\\programming\\doi-registration-service\\Notulae\\v9\\i5"

#os.chdir("D:\\Plazi\\services\\DOI\\Revue_de_Paleobiologie")
#os.chdir("D:\\Plazi\\services\\DOI\\Notulae")
#os.chdir("D:\\Plazi\\services\\DOI\\Odonatologica")
os.chdir(path)
#os.chdir("D:\\Plazi\\services\\DOI\\RSZ\\126_1")

#file = "DOI_RPALEO_38_1_edit_prereserved_dois.xlsx"
#file = "DOI_RPALEO_38_1_edit.xlsx"
#file = "Notulae_odonatologicae_DOI_2019_June_prereserved_doi_pdfs.xlsx"
#file = "Odonatologica_June_2019_RSZ_122_2_prereserved_doi_pdfs.xlsx"
#file = "RSZ_126_1_prereserve_doi_pdfs_included.xlsx"
#file = "Odonatologica_v48_i3-4-edited-prereserved_dois.xlsx"
#file = "Notulae_Odonatologicae_v9_i5-edited.xlsx"
#file = "Odonatologica_v49_i1-2-edited-prereserved_dois.xlsx"
#file = "Revue_Suisse_Zoologie_v126_i1.xlsx"
#file = "Revue_Suisse_Zoologie_v126_i2-edited-predefined_dois-updated-pushed_pdfs-TESTING.xlsx"
#file = "XIII_Int_Symp_Neuropterology_Dec2019_edited_prereserved_dois.xlsx"
#file = "Revue_de_Paléobiologie_v38_i2_edited_prereserved_dois.xlsx"
#file = "Odonatologica_v48_i3-4.xlsx"
#file = "Odonatologica_v48_i3-4-edited-prereserved_dois.xlsx"
#file = "Notulae_Odonatologicae_v9_i4-edited-prereserved_dois-pdfs_pushed.xlsx"
#file = "Revue_de_Paleobiologie\\v39\\i1\\Revue_de_Paléobiologie_v39_i1-edited-prereserved_dois-pushed_pdfs.xlsx"
#file = "DOI_39_1_RPaleo-edited.xlsx"

#file = "Odonatologica_v49_i1-2-edited-prereserved_dois-pdfs_pushed.xlsx"
#file = "DOI_39_1_RPaleo-edited-prereserved_dois-pushed_pdfs.xlsx"
#file = "Notulae_odonatologicae_v9_i5-edited-prereserved_dois-pushed_pdfs.xlsx"

# file = "Doi_RPaleo_39_2_2020_extra.xlsx"
file = 'Notulae_odonatologicae_v9_i7'

#file_path = "D:\\Plazi\\services\\DOI\\Revue_de_Paleobiologie\\" + file
#file_path = "D:\Plazi\services\DOI" + r"\N" + "eilreichia\\" + file
#file_path = "D:\\Plazi\\services\\DOI\\Notulae\\" + file
#file_path = "D:\\Plazi\\services\\DOI\\Odonatologica\\" + file
#file_path = "D:\\Plazi\\services\\DOI\\RSZ\\126_1\\" + file
file_path = path + "\\" + file


db = lcpxlsx.Xls(file_path)

headers = {"Content-Type": "application/json"}

#string = str(self.working_sheet.cell(1, 52).value) + "\n" + str(self.working_sheet.cell(2, 52).value) + "\n" + str(self.working_sheet.cell(1, 53).value) + "\n" + str(self.working_sheet.cell(2, 53).value)
"""
data = {
    "metadata": {
        "doi": "10.5555/Zookeys",
        "title": "My first upload",
        "upload_type": "publication",
        "publication_type": "article",
        "description": "This is my first upload",
        "notes": "blabla",
        "communities": [{"identifier": "biosyslit"}],
        "keywords": ["a","b","c","d","e"],
        "creators": [
            {"name": "Guidoti, John", "affiliation": "Zenodo"}
            ],
        "contributors": [
            {"type": "ContactPerson", "name": "Guidoti, Marcus"},
            {"type": "DataCollector", "name": "Guidoti, Marcus"},
            {"type": "DataCurator", "name": "Guidoti, Marcus"},
            {"type": "DataManager", "name": "Guidoti, Marcus"},
            {"type": "Editor", "name": "Guidoti, Marcus"},
            {"type": "Researcher", "name": "Guidoti, Marcus"},
            {"type": "RightsHolder", "name": "Guidoti, Marcus"},
            {"type": "Sponsor", "name": "Guidoti, Marcus"},
            {"type": "Other", "name": "Guidoti, Marcus"}
        ]
    }
}
"""
#obj = lcp_data.Paper(paper_info)

#a = vars(obj)

#for at in a:
#    print(at + ": " + a[at])

#print(obj.get_upload_type())
#print(obj.get_publication_type())

#print(obj.__getattribute__("upload_type"))

#obj.__setattr__("upload_type", "hahaha")

#print(obj.upload_type)


#print(lcpxlsx.Xls.__init__.__doc__)

#x = self.working_sheet.max_row

#print(db.get_column_index("TItle"))
#print(self.check_data("upload_type"))
#print(self.check_PDFs_validity())
#print(self.error_messages)
#db.write_ID(2, "88888")
#print(self.check_PDFs_validity())
#print(self.error_messages)


#self.check_internal_fields()

#self.check_resource_fields()

#print(self.get_data("communities", 2))

#self.check_metadata_fields()
#print(self.error_messages)
#print(self.get_data("creators", 2))
#print(self.get_data("keywords", 2))
#print(self.get_data("title", 2))

#print(self.check_PDFs_validity())
#self.define_action()

#print(self.check_metadata_fields())

#print(self.initial_check())

#print(db.define_action())

#self.get_all_papers()

#print(self.check_all_fields())
#print(self.error_messages)

#print(self.check_data_content("zenodo_status", "done"))
#print(self.error_messages)

#print(self.check_data_content("zenodo_status", "unsubmitted"))
#print(self.error_messages)

#print(self.check_metadata_fields())
#print(self.error_messages)

#print(self.get_data("creators", 12))
#print(self.working_sheet.cell(5, 4).value)

#for each in self.get_all_papers():
#    print(each["metadata"]["title"])
#    print(each["metadata"]["creators"])

# Access token Name = mguidoti_sandbox
#ACCESS_TOKEN = "3QbSCaJML0Ein4RgGB3ruAhu5xG7sBhi6rdK5DkmcN390HMaSeY2gckrabZJ"

#url = "https://sandbox.zenodo.org/api/deposit/depositions"

#r = requests.post(url, params={'access_token': ACCESS_TOKEN}, data=json.dumps(data), headers=headers)

#print(r.status_code)

#print(r.json()["metadata"]["notes"])

#zenodotus.push(self, sandbox="off", marcus="on")


#zenodotus.push(self, sandbox="on", marcus="on")


#print(db.check_PDFs_validity())
#print(db.define_action())

#zenodotus.define_parameters(sandbox="on", marcus="on")
#zenodotus.push_data(db, sandbox="on", marcus="on")
#print(zenodotus.token_switch(sandbox="on", marcus="on"))

#print(self.get_data("creator_5_name",4))
#print(self.get_data("creator_2_affiliation",4))
#print(self.get_data("creator_3_affiliation",4))
#print(self.get_data("creator_4_affiliation",4))
#print(self.get_data("title",4))
#print(self.get_data("description",4))



#zenodotus.push_data(db, sandbox="on", marcus="on")

"""
if db.define_action() == 5:

    print(zenodotus.push_PDFs(db, sandbox="off", marcus="off"))

else:
    print("no")
"""

#print(db.define_action())
"""
print(zenodotus.publish(db))
"""
"""
if "2019-04-30T14:26:39.921621+00:00" != "2019-03-31T17:35:52.391577+00:00":
    print("hey")
else:
    print("Nope")
"""

"""
papers_all = db.get_all_papers()

for each in papers_all:
    print(each)
    print(each.internal_id)
"""

#print(db.get_all_papers())
#print(db.define_action())
#zenodotus.push_data(db, sandbox="on", marcus="on")
zenodotus.push_data(db, sandbox="off", marcus="off")
#zenodotus.push_PDFs(db, sandbox="off", marcus="off")
#zenodotus.publish(db)

#r = requests.post('https://zenodo.org/api/deposit/depositions/2619518/actions/publish', params={'access_token': "5izwuFcjcN9Vk7En8JNeP6PqVe2oM1KIRxVEfvCGoJ4rW6cYyck5LBIWmB1v"})

#print(r.json())

#print(db.define_action())



#papers = self.get_all_papers()

#print(papers[1].title)
#papers[1].title = "voila"

#print(papers[1].title)

#self.check_resource_fields()

#for each in dict_temp:
#    if each == "metadata":
#        for metadata in dict_temp[each]:
#            dict_temp[each][metadata] = self.get_data(metadata, 2)
#    elif self.get_data(each, 2) == None:
#        dict_temp[each] = ""
#    else:
#        dict_temp[each] = self.get_data(each, 2)

#print(dict_temp)


#print(self.get_column_index("internal_id"))

#print(self.working_sheet.max_column)
#print(self.working_sheet.cell(1,((self.working_sheet.max_column)+1)).value)
#print(self.working_sheet.cell(1,((self.working_sheet.max_column))).value)
#print(self.working_sheet.cell(1,((self.working_sheet.max_column)-1)).value)

#TESTING GETTING KEYWORDS OF ONE PAPER
#print(self.get_data("keywords", 2))
#print(self.get_data("keywords", 2)[2])

#TESTING GETTING COMMUNITIES OF ONE PAPER
#print(self.get_data("communities", 2))
#print(self.get_data("communities", 2)[1]["identifier"])

#TESTING GETTING ANY OTHER FIELD OF ONE PAPER
#print(self.get_data("journal_title", 3))

#TESTING GETTING A NON-EXISTING FIELD OF ONE PAPER
#print(self.get_data("titl", 3))

#TESTING ITERACTION WITH AUTHORS OF ONE PAPER
#creators_of_paper = self.get_data("creators", 11)

#print(creators_of_paper)
#print(creators_of_paper[1]["affiliation"])
#print(creators_of_paper[2]["name"])
#print(creators_of_paper[0]["affiliation"])
#print(creators_of_paper[0]["orcid"])

#TESTING ITERACTION WITH CONTRIBUTORS OF ONE PAPER
#contributors_of_paper = self.get_data("contributors", 2)

#print(contributors_of_paper)
#print(contributors_of_paper[0]["name"])
#print(contributors_of_paper[1]["affiliation"])
#print(contributors_of_paper[2]["name"])
#print(contributors_of_paper[0]["affiliation"])
#print(contributors_of_paper[0]["type"])


#field_name = "creators"
#col = "creator_7_name"
#num = col[(col.find("_")+1):][:col[(col.find("_")+1):].find("_")]

#print(num)

#str = (field_name[:(len(field_name)-1)] + "_" + num + "_name")

#print(self.get_column_index("pau"))

#str = "creator_1_affiliation"

#print(str[(str.find("_")+1):].find("_"))
#print(str[(str.find("_")+1):])
#print(str[(str.find("_")+1):][((str[(str.find("_")+1):].find("_"))+1):])

#print(str[(str.find("_")+1):][:str[(str.find("_")+1):].find("_")])

#if "creator" in str:
#    print("yes")
#else:
#    print("no")
#print(self.get_data("title",3))

#print(os.path.isfile((str(self.dir) + "\\" + str(self.working_sheet.cell(2, self.get_column_index("filename")).value))))

#list = [7, 8, "", ""]

#dict = {
#    "name": 7,
#    "affiliation": 8,
#    "orcid": None,
#    "gnd": None
#}

#dict = {}

#if dict != {}:
#    print(dict)

#else:
#    print("ups")

#dict.update({"type": "uhul"})

#print(dict)
