#E O MODULO ZENODOTUS (por enquanto, uma funcao, mandar dados, e escrever as infos resultantes mas sem publicar.)
import os
import requests
import json
import openpyxl as opxl
import random
import lcpxlsx
import lcpunit


def sandbox_switch(sandbox="off"):

    if sandbox == "on":
        return "https://sandbox.zenodo.org/api/deposit/depositions"

    else:
        return "https://zenodo.org/api/deposit/depositions"


def token_switch(sandbox="off", marcus="off"):

    if "sandbox" in sandbox_switch(sandbox):

        if marcus == "off":

            #Access token name = sandbox_doi_service_plazi
            return "6R6LCyqt7qSskQZMmN9RtnOd7KR59IH977deYBfbzJjOaXnN4cFktWHCmwfn"

        else:
            #Access token Name = mguidoti_sandbox
            print("marcus mode")
            return "3QbSCaJML0Ein4RgGB3ruAhu5xG7sBhi6rdK5DkmcN390HMaSeY2gckrabZJ"


    else:

        if marcus == "off":

            #Access token name = doi_service_plazi
            return "5izwuFcjcN9Vk7En8JNeP6PqVe2oM1KIRxVEfvCGoJ4rW6cYyck5LBIWmB1v"

        else:
            #Access token Name = mguidoti
            print("marcus mode")
            return "yoCuTRygTHb0YSQ3UQY45Rj9JfcJhWhVXXvV3ZTRAQbTuiZY7KHD2fWg8S1j"


def push_data(database, sandbox="off", marcus="off"):

    url = sandbox_switch(sandbox)
    key = token_switch(sandbox, marcus)

    papers = database.get_all_papers()

    if database.define_action() == 0:

        zenodo_resource_data = {
            "zenodo_created": "created",
            #"zenodo_doi": "doi",
            #"zenodo_doi_url": "doi_url",
            "zenodo_id": "id",
            "zenodo_modified": "modified",
            "zenodo_owner": "owner",
            "zenodo_record_id": "record_id",
            "zenodo_status": "state",
            "zenodo_published": "submitted",
            "zenodo_prereserve_doi": "prereserve_doi"
        }

        for each in papers:

            headers = {"Content-Type": "application/json"}

            data = each.zenodo_metadata()

            zen = requests.post(url, params={'access_token': key}, data=json.dumps(data), headers=headers)

            print(zen.status_code)
            print(zen.json())

            internal_id = each.internal_id

            for each in zenodo_resource_data:
                if each == "zenodo_prereserve_doi":

                    update = zen.json()["metadata"]["prereserve_doi"]["doi"]

                    database.write_checking_internal_id(internal_id, each, update)

                else:

                    update = zen.json()[zenodo_resource_data[each]]

                    database.write_checking_internal_id(internal_id, each, update)


def update_resource_info(database, paper, url, key):
    """
    Retrieves the updated information from the Zenodo deposit of a specific paper and checks with the information on the database for that specific paper. Then, updates the dabatase if needed.

    Parameters
    ----------
    database : obj
        An object with the database loaded and its respective methods available.

    paper : obj
        A paper object with all of its attributes.

    url : str
        The base url (with or without 'sandbox') to be used while retrieving the updated metadata information of a given Zenodo deposit.

    key : str
        The API key to be used while retrieving the updated metadata information of a given Zenodo deposit.

    Returns
    -------
    bool
        Returns True if any information for that given paper was updated in the database, and False if no information was updated in the database.

    Example
    -------
    update_resource_info(db, each_from_a_for_loop, zen).

    """

    #Creates the dictionary with the terms for both paper object atributes, which is the same names for columns in the database, and the zenodo field so both can be retrieved and compared and the information written in the database if needed.
    zenodo_resource_data = {
        "zenodo_doi": "doi",
        "zenodo_doi_url": "doi_url",
        "zenodo_modified": "modified",
        "zenodo_status": "state",
        "zenodo_published": "submitted"
    }

    #Sets the URL to retrieve the updated Zenodo deposit metadata.
    retrieve_info_url = url + "/" + paper.zenodo_id + "?access_token=" + key

    #Gets the updated metadata for a given Zenodo deposit.
    zen = requests.get(retrieve_info_url)

    #Creates the variable that will be used to return the boolean value at the end.
    overwritten_checker = False

    #Creates a loop checker for all fields in the dictionary.
    for each in zenodo_resource_data:

        #Compares if the paper data is the same as the zenodo data for each field in the dictionary, and, if the dictionary key doesn't exist, continues the loop without breaking the program.
        try:
            if str(zen.json()[zenodo_resource_data[each]]) != str(paper.__getattribute__(each)):

                #Writes the new information, if they are different, into the database.
                database.write_checking_internal_id(paper.internal_id, each, zenodo_info)

                #Need to write the 'sent' status on the pdf_status field here.

                #Change the state of the variable that will define what this function will return.
                overwritten_checker = True

        except:
            #Continues the loop in case of one of the dictionary keys  doesn't exist.
            continue


    #Returns the checking variable. If after all fields were checked for the provided paper, returns the default value, False.
    return overwritten_checker


def push_PDFs(database, sandbox="off", marcus="off"):
    """
    Uploads the PDF files listed in the database to the respective Zenodo deposit using the Zenodo ID in that given row (for that given paper) of the database.

    It returns False if any of the PDFs was considered to be a duplicate with the files already existing for that specific Zenodo deposit and couldn't be uploaded to Zenodo.

    Parameters
    ----------
    database : obj
        An object with the database loaded and its respective methods available.

    sandbox : str
        Optional parameter to turn on the sandbox option, in order to test the data before trying to upload to the real Zenodo server. Default value = off.

    marcus : str
        Optional parameter to turn on my API keys instead of Terry's, also, intended to testing. Default value = off.

    Returns
    -------
    bool
        Returns True if all PDFs in the database was succesfully pushed to their respective Zenodo depositions, and False, if at least one of them couldn't be uploaded for some reason. The error message is added to the <error_message> dictionary of the database object.

    Example
    -------
    push_PDFs(database, sandbox="off", marcus="off").

    """
    #Sets the two variables that will be used to send the files and to retrieved the json() from Zenodo with the updated resoruce information to be updated in the database.
    url = sandbox_switch(sandbox)
    key = token_switch(sandbox, marcus)

    #Removes the key "Filename already exists. for internal IDs:" in the <error_messages> dictionary of the database object, to make sure I won't run into problems when defining the returning boolean at the end of this function.
    database.error_messages.pop("Filename already exists. for internal IDs:", None)

    #Gets the list of Paper() objects from the database.
    papers = database.get_all_papers()

    #Iteracts with the list, going through all papers.
    for each in papers:

        #This avoids OS problems with the slash used in the file paths.
        if each.path_to_pdf.__contains__("\\"):
            separator = "\\"
        elif each.path_to_pdf.__contains__("/"):
            separator = "/"

        #Sets the URL to 'create' a PDF for a given depoistion.
        send_pdf_url = url + "/" + each.zenodo_id + "/files?access_token=" + key

        #Sets the two metadata required for creating a new file within a Zenodo deposition: file name and file path.
        data = {"filename": each.path_to_pdf[each.path_to_pdf.find(separator)+1:]}
        files = {"file": open(each.path_to_pdf, "rb")}

        #Creates a new file within a Zenodo deposition.
        zen = requests.post(send_pdf_url, data=data, files=files)

        #Tests the response. If succesfull (== 201)... if not (== 400)... These HTTP error codes were defined by Zenodo API.
        if zen.status_code == 201:

            #Call the function that will cross-check each of the zenodo resource fields for updated information, overwritting this field for that respective paper if a new value is observed.
            update_resource_info(database, each, url, key)


        #Better to update this when I write the function status_code(), and use the if strategy adopted in the function 'publish', which is, if NOT the good code, then do this.. else, do the good code routine (update database with the new metadata).
        elif zen.status_code == 400:

            #Adds to the error_message dictionary of the database object the papers <internal_ID>'s that presented an error when trying to upload the file indicated in the database.
            database.append_to_error_dict((str(zen.json()["message"]) + " for internal IDs:"), each.internal_id)

            #Makes sure the program will continue for the next Paper() object in the list of papers if the current one encountered an error when trying to upload the PDF to its respective Zenodo deposit.
            continue

    #Print the specific key in the <error_message> dictionary of the database object if this one exists, returning False; returns True if the key doesn't exist.
    try:
        print("Filename already exists. for internal IDs: " + database.error_messages["Filename already exists. for internal IDs:"])
        return False
    except KeyError:
        return True


def publish(database, sandbox="off", marcus="off"):

    #Sets the two variables that will be used to send the files and to retrieved the json() from Zenodo with the updated resoruce information to be updated in the database.
    url = sandbox_switch(sandbox)
    key = token_switch(sandbox, marcus)

    #Gets the list of Paper() objects from the database.
    papers = database.get_all_papers()

    error_checker = False

    for each in papers:

        publishing_url = url + "/" + each.zenodo_id + "/actions/publish"

        zen = requests.post(publishing_url, params={'access_token': key})

        if zen.status_code != 202:
            error_checker = True

        else:
            update_resource_info(database, each, url, key)

    if error_checker == False:
        return True

    else:
        return False
