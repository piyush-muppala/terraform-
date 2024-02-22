from sys import displayhook
import requests
import pandas as pd
import numpy as np
import xmltodict

endpoint = "http://wits.worldbank.org/API/V1/SDMX/V21/rest"


def getCodelist(codelist):
    codelist_meta = {
        'id': codelist['@id'],
        'agencyID': codelist['@agencyID'],
        'version': codelist['@version'],
        'isFinal': codelist['@isFinal'],
        'name': codelist['Name']['#text']
    }
    codelist_codes = codelist['Code']

    if type(codelist_codes) == list:
        codelist_code = [{'id': code['@id'],
                          'name': code['Name']['#text'],
                          'language': code['Name']['@xml:lang']} for code in codelist_codes]
    else:
        codelist_code = [{'id': codelist_codes['@id'],
                          'name': codelist_codes['Name']['#text'],
                          'language': codelist_codes['Name']['@xml:lang']}]

    return {
        'header': pd.DataFrame([codelist_meta]),
        'codes': pd.DataFrame(codelist_code)
    }


def get_user_input():
    dataset_id = input("Enter dataset ID: ")
    datastructure_id = input("Enter datastructure ID: ")
    start_period = input("Enter start period (e.g., 2010): ")
    end_period = input("Enter end period (e.g., 2015): ")

    query_params = {
        'FREQ': input("Enter frequency: "),
        'REPORTER': input("Enter reporter code: "),
        'PARTNER': input("Enter partner code: "),
        'PRODUCTCODE': input("Enter product code: "),
        'INDICATOR': input("Enter indicator code: "),
    }

    return dataset_id, datastructure_id, start_period, end_period, query_params


def make_api_call(endpoint, dataset_id, query_params, period_parameter):
    query_string = '.'.join([value for value in query_params.values()])
    path = f'{endpoint}/data/{dataset_id}/{query_string}/{period_parameter}'

    response = requests.get(path)

    if response.status_code == 200:
        response_dict = xmltodict.parse(response.text)
        response_series = response_dict['message:GenericData']['message:DataSet']['generic:Series']
        series_list = [response_series] if type(response_series) == dict else response_series

        series_observations = []
        for i, series in enumerate(series_list):
            series_key = series['generic:SeriesKey']
            series_key_values_raw = [series_key['generic:Value']] if type(series_key['generic:Value']) == dict else \
                series_key['generic:Value']
            series_key_values = {value['@id']: value['@value'] for value in series_key_values_raw}

            series_obs_raw = series['generic:Obs']
            series_obs = [series_obs_raw] if type(series_obs_raw) == dict else series_obs_raw

            observations = []
            for j, obs in enumerate(series_obs):
                obs_dimensions_raw = [obs['generic:ObsDimension']] if type(
                    obs['generic:ObsDimension']) == dict else obs['generic:ObsDimension']
                obs_dimensions = {value['@id']: value['@value'] for value in obs_dimensions_raw}

                obs_attributes = obs['generic:Attributes']['generic:Value']
                obs_attributes = [obs_attributes] if type(obs_attributes) == dict else obs_attributes
                obs_attributes = {value['@id']: value['@value'] for value in obs_attributes}

                obs_value = obs['generic:ObsValue']
                obs_value = {'OBS_VALUE': float(obs_value['@value'])}

                observation = [{**series_key_values, **obs_dimensions, **obs_attributes, **obs_value}]
                observations.extend(observation)

            series_observations.extend(observations)

        data = pd.DataFrame(series_observations)
        return data  
    else:
        print(f"Error: Received status code {response.status_code}")
        print("Response Content:", response.text)
        return None


def get_codelist(endpoint, agency_id, codelist_id):
    path = f'{endpoint}/codelist/{agency_id}/{codelist_id}'
    response = requests.get(path)

    if response.status_code == 200:
        response_dict = xmltodict.parse(response.text)['Structure']
        codelists = response_dict['Structures']['Codelists']['Codelist']
        return getCodelist(codelists)['codes']
    else:
        print(f"Error: Received status code {response.status_code}")
        return None


def main():
    dataset_id, datastructure_id, start_period, end_period, query_params = get_user_input()
    period_parameter = f'?startperiod={start_period}&endperiod={end_period}'

    codelist_id = 'CL_TS_COUNTRY_WITS' 
    codelist = get_codelist(endpoint, 'WBG_WITS', codelist_id)
    displayhook(codelist.head())


    data = make_api_call(endpoint, dataset_id, query_params, period_parameter)

    if data is not None:
        csv_filename = f'{dataset_id}_{datastructure_id}_data.csv'
        data.to_csv(csv_filename, index=False)
        print(f'Data saved to {csv_filename}')
    else:
        print('Error: Unable to retrieve data.')


if __name__ == "__main__":
    main()
