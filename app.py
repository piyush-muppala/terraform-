from sys import displayhook
from tkinter.tix import DisplayStyle
import requests
import pandas as pd
import numpy as np
import xmltodict

from app1 import getCodelist

endpoint = "http://wits.worldbank.org/API/V1/SDMX/V21/rest"


path = '/'.join([endpoint, 'dataflow'])
response = requests.get(path)
if response.status_code == 200:

   # Convert XML Response to Dictionary Object
   response_dict = xmltodict.parse(response.text)['Structure']

   # Drill through specific keys to get the list of dataflows in the dictionary and then normalize it to pandas dataframe.
   dataflows = pd.json_normalize(response_dict['Structures']['Dataflows']['Dataflow'])

   # Only get English version of dataflows' name and description
   dataflows = dataflows[(dataflows['Name.@xml:lang'] == 'en') &
                           (dataflows['Description.@xml:lang'] == 'en')
                       ]
   dataflows = dataflows[['@id', '@agencyID', '@version', '@isFinal', 'Description.#text', 'Structure.Ref.@id']]

   # Rename the dataflow column
   dataflows = dataflows.rename(columns={
       '@id': 'id',
       '@agencyID': 'agencyID',
       '@version': 'version',
       '@isFinal':'isFinal',
       'Description.#text': 'description',
       'Structure.Ref.@id': 'datastructure'
   })

displayhook(dataflows[['id', 'datastructure', 'description']])

codelist = 'CL_TS_COUNTRY_WITS'
path = '/'.join([endpoint, 'codelist/WBG_WITS', codelist])

response = requests.get(path)
if response.status_code == 200:
   response_dict = xmltodict.parse(response.text)['Structure']
   codelists = response_dict['Structures']['Codelists']['Codelist']
   codelist = getCodelist(codelists)['codes']

filtered_codes = codelist[codelist['name'].isin(['Singapore', 'Malaysia', 'Indonesia'])]
displayhook(filtered_codes)