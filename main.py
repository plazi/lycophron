import lycophron
import projects.covihost.covihost_bibtex as covihost_bibtex
import projects.covihost.covihost_csv as covihost_csv
import logging

logging.basicConfig(filename='projects/covihost/data/logs/covihost-task-20200716-odd_data.log')

#covihost_bibtex.convert_to_zenodo('projects/covihost/data/odd_data.bib', 'projects/covihost/data/converted_data.csv')

#lycophron.push_data(covihost_csv.read_csv('projects/covihost/data/converted_data.csv'), 'projects/covihost/data/zenodo_output.csv', sandbox='off')

#covihost_csv.combine_csv('projects/covihost/data/zenodo_output.csv', 'projects/covihost/data/doi-filename-no_extracted.csv')

#lycophron.push_PDFs(covihost_csv.read_csv('projects/covihost/data/combined_csvs.csv'), 'projects/covihost/data/zenodo_output-PDFs.csv', sandbox='off')

lycophron.publish(covihost_csv.read_csv('projects/covihost/data/zenodo_output-PDFs.csv'), 'projects/covihost/data/zenodo_output-PDFs-Published.csv', sandbox='off')