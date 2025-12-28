from functools import lru_cache

import requests,json

# config item e.g. PYVIN_VIN_DECODE_EXT_URL
base_url = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/' # should be const somewhere

# config item e.g. PYVIN_RESPONSE_FORMAT
base_params = {'format': 'json'}

@lru_cache(maxsize=1000)
def decode_vin_values_extended(vin:str) -> requests.Response:
    req_url = base_url + vin
    try:
        resp = requests.get(url=req_url, params=base_params)
        return resp
    except requests.RequestException as e:
        raise Exception(f"Error making request: {e}")

def print_vin_values_extended(resp: requests.Response):
    if resp.status_code != 200:
        raise Exception(f"Error decoding VIN: {resp.text}")
    for k,v in json.loads(resp.text)['Results'][0].items():
        if len(str(v)) == 0:
            continue
        print(k, ": ", v)

if __name__ == "__main__":
    vin_to_decode = "19UUA56922A021559"
    try:
        response = decode_vin_values_extended(vin_to_decode)
        print_vin_values_extended(response)
    except Exception as e:
        print(f"Error: {e}")