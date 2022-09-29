import requests
import json
import logging

import projects.covihost.covihost_csv as csvhandler

#logging.basicConfig(filename='projects/covihost/logs/zenodo.log')

def sandbox_switch(sandbox):
    if sandbox == "on":
        return "https://sandbox.zenodo.org/api/deposit/depositions"
    else:
        return "https://zenodo.org/api/deposit/depositions"


def push_data(list_of_entries, output, sandbox="off"):

    url = sandbox_switch(sandbox)
    #token = "3QbSCaJML0Ein4RgGB3ruAhu5xG7sBhi6rdK5DkmcN390HMaSeY2gckrabZJ" #marcus sandbox
    token = "1zreU7sFfMYFaA3ff4bCuMVYdAEy3GiNKw9TMHXJTciPKn4zFb6DicdOFkpG" #plazi coviho

    headers = {"Content-Type": "application/json"}

    counter = 0

    results = []

    for entry in list_of_entries:

        counter = counter + 1

        dump = {'metadata': entry}

        try:

            zenodo = requests.post(
                url,
                params = {'access_token': token},
                data = json.dumps(dump),
                headers = headers
            )

            if (zenodo.status_code >= 300):
                status = "[PUSH DATA] Entry number #{number}, DOI={doi}, couldn't be posted. Reason: {message}. Status Code: {status_code}".format(
                    number=counter,
                    doi=entry['doi'],
                    message=zenodo.json(),
                    status_code=zenodo.status_code
                )
                logging.error(status)
                print(status)
            else:
                status = "[PUSH DATA] Entry number #{number}, DOI={doi}, was succesfully pushed. Zenodo record ID: {zenodo_ID}. Status Code: {status_code}".format(
                    number=counter,
                    doi=entry['doi'],
                    zenodo_ID=zenodo.json()['id'],
                    status_code=zenodo.status_code
                )

                logging.info(status)
                print(status)

                results.append(
                    {
                        'doi': zenodo.json()['doi'],
                        'filename': '',
                        'id': zenodo.json()['id'],
                        'bucket': zenodo.json()['links']['bucket'],
                        'data': 'Pushed',
                        'PDFs': '',
                        'Status': ''
                    }
                )

        except Exception as e:

            status = "[CONNECTION] Entry number #{number}, DOI={doi}, couldn't be posted. Error: {error}.".format(
                        number=counter,
                        doi=entry['doi'],
                        error=str(e.args)
                    )

            logging.error(status)
            print(status)

    fieldnames = ['doi', 'filename', 'id', 'bucket', 'data', 'PDFs', 'Status']

    csvhandler.write_csv('projects/covihost/data/zenodo_output.csv', results, fieldnames)


def push_PDFs(list_of_deposits, output, sandbox="off"):

    url = sandbox_switch(sandbox)
    #token = "3QbSCaJML0Ein4RgGB3ruAhu5xG7sBhi6rdK5DkmcN390HMaSeY2gckrabZJ" #marcus sandbox
    token = "1zreU7sFfMYFaA3ff4bCuMVYdAEy3GiNKw9TMHXJTciPKn4zFb6DicdOFkpG" #plazi coviho

    params = {'access_token': token}

    counter = 0

    for deposit in list_of_deposits:

        counter = counter + 1

        filename = deposit["filename"]

        path = "projects/covihost/PDFs/" + filename

        try:

            with open(path, "rb") as filepath:

                zenodo = requests.put(
                    "{bucket}/{filename}".format(bucket=deposit["bucket"], filename=filename),
                    data = filepath,
                    params = params
                )

                if (zenodo.status_code >= 300):
                    status = "[ATTACH PDF] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, couldn't be attached. Reason: {message}. Status Code: {status_code}".format(
                        number=counter,
                        doi=deposit['doi'],
                        zenodo_ID=deposit['id'],
                        message=zenodo.json()['message'],
                        status_code=zenodo.status_code
                    )
                    logging.error(status)
                    print(status)
                else:

                    status = "[ATTACH PDF] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, was succesfully attached. Status Code: {status_code}".format(
                        number=counter,
                        doi=deposit['doi'],
                        zenodo_ID=deposit['id'],
                        status_code=zenodo.status_code
                    )

                    logging.info(status)
                    print(status)

                    deposit['PDFs'] = 'Ok!'

        except Exception as e:

            status = "[ATTACH PDF] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, couldn't be posted. Reason: {message}. Status Code: {status_code}. Error: {error}.".format(
                        number=counter,
                        doi=deposit['doi'],
                        zenodo_ID=deposit['id'],
                        message=zenodo.json()['message'],
                        status_code=zenodo.status_code,
                        error=str(e.args)
                    )
            logging.error(status)
            print(status)

    csvhandler.write_csv('projects/covihost/data/zenodo_output-PDFs.csv', list_of_deposits, list_of_deposits[0].keys())


def publish(list_of_deposits, output, sandbox="off"):

    url = sandbox_switch(sandbox)
    #token = "3QbSCaJML0Ein4RgGB3ruAhu5xG7sBhi6rdK5DkmcN390HMaSeY2gckrabZJ" #marcus sandbox
    token = "1zreU7sFfMYFaA3ff4bCuMVYdAEy3GiNKw9TMHXJTciPKn4zFb6DicdOFkpG" #plazi coviho

    params = {'access_token': token}

    counter = 0

    for deposit in list_of_deposits:

        counter = counter + 1

        final_url = url + "/%s/actions/publish" % deposit["id"]

        try:

            zenodo = requests.post(
                final_url,
                params = params
            )

            if (zenodo.status_code >= 300):
                        status = "[PUBLISHING] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, couldn't be published. Reason: {message}. Status Code: {status_code}".format(
                            number=counter,
                            doi=deposit['doi'],
                            zenodo_ID=deposit['id'],
                            message=zenodo.json()['message'],
                            status_code=zenodo.status_code
                        )
                        logging.error(status)
                        print(status)
            else:

                status = "[PUBLISHING] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, was succesfully published. Status Code: {status_code}".format(
                    number=counter,
                    doi=deposit['doi'],
                    zenodo_ID=deposit['id'],
                    status_code=zenodo.status_code
                )

                logging.info(status)
                print(status)

                deposit['Status'] = 'Published!'

        except Exception as e:

            status = "[PUBLISHING] Entry number #{number}, DOI={doi} and Zenodo ID={zenodo_ID}, couldn't be published. Reason: {message}. Status Code: {status_code}. Error: {error}.".format(
                        number=counter,
                        doi=deposit['doi'],
                        zenodo_ID=deposit['id'],
                        message=zenodo.json()['message'],
                        status_code=zenodo.status_code,
                        error=str(e.args)
                    )

            logging.error(status)
            print(status)

    csvhandler.write_csv('projects/covihost/data/zenodo_Published.csv', list_of_deposits, list_of_deposits[0].keys())