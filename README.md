# Lycophron

> Tool to batch upload papers (or any other file type) to Zenodo, writing information back to the original databases (i.e., pre-reserved DOIs), to Plazi use as service for clients and perhaps one day be implemented as a webservice in [Plazi's website](http://plazi.org).



## Content

[Disclaimer](#Disclaimer)  
[How to Run Lycophron](#How-to-Run-Lycophron)  
[Further Documentation](#Further-Documentation)  
[Known Bugs](#Known-Bugs)  
[How to Contribute](#How-to-Contribute)  
[License](#License)  



## Disclaimer

Currently, Lycophron only reads data from *.xlsx and *.xls. As this was designed from the scratch as a modular software, in the future, if needed, new modules to read different databases can be easily included.  

I'll include a **link here** or somewhere else (blog post, I don't know) the initial designs, UML schemes, changes along the way, in the future (not anytime soon though!).



## How to Run Lycophron

***Lycophron*** is currently in **alpha** version and it's run only by command line, calling lcpxlsx.py and zenodotus.py functions directly. 



A text-based interface is planned for **v1.0**, and a GUI for v2.0. The design of the GUI will be openly discussed here when the time comes.



## Further Documentation

I wrote this [data dictionary](https://docs.google.com/spreadsheets/d/1tx3EEw3AxDwQu9gFKETk6HdimS-uBcl6pHZmZG75rmM/edit?usp=sharing) based on [Zenodo API's documentation](http://developers.zenodo.org). In this file, you can see what is currently implemented on ***Lycophron***, how it's implemented, how to access different data in Python and on Zenodo's response *jsons*, what is not and the reason why, and so on. 



## Known Bugs

***Lycophron*** has some bugs that need to be fixed:

*  It doesn't function properly when the original database (in this current version, *.xlsx or *.xls only) is open (issue # )

* When writing the Zenodo Resource Fields as new columns, when needed, some blank ones are being added unintentionally (issue # );
* It crashes when trying to read non-Unicode character (issue # )



## How to Contribute

> *It depends on the License, and, on Plazi's plans for Lycophron. But if a open source project, I'll write a proper CONTRIBUTE.md.*



## License

> *That's not to me to decide! It belongs to Plazi, but, on which license?*
