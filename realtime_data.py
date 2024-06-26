import requests
from datetime import datetime
import logging

AUTH_URL = 'https://lb.solinteg-cloud.com/openapi/v2/loginv2/auth'
AUTH_ACCOUNT = 'shailendra.nair@atriapower.com'
AUTH_PASSWORD = 'SolarEnergy'
BASE_DATA_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDeviceRealtimeData'
DAY_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryDayAggregateValues'
MONTH_AGGREGATE_URL = 'https://lb.solinteg-cloud.com/openapi/v2/device/queryMonthAggregateValues'
DEVICE_SN = 'A102300100402049'

logging.basicConfig(level=logging.INFO)

def get_auth_token():
    payload = {
        'authAccount': AUTH_ACCOUNT,
        'authPassword': AUTH_PASSWORD
    }
    try:
        response = requests.post(AUTH_URL, json=payload)
        logging.info(f'Auth response: {response.status_code} {response.text}')
        response.raise_for_status()
        auth_data = response.json()
        return auth_data['body']
    except requests.exceptions.RequestException as e:
        logging.error(f'Error getting auth token: {str(e)}')
        raise

def get_data(url, token, params):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'token': token
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        logging.info(f'Data response from {url}: {response.status_code} {response.text}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error getting data from {url}: {str(e)}')
        raise

def get_current_month_dates():
    now = datetime.now()
    start_date = now.strftime('%Y%m01')
    end_date = now.strftime('%Y%m%d')
    return start_date, end_date

def fetch_data(token):
    start_date, end_date = get_current_month_dates()

    urls_and_params = [
        (BASE_DATA_URL, {'deviceSn': DEVICE_SN}),
        (DAY_AGGREGATE_URL, {'deviceSn': DEVICE_SN, 'date': end_date}),
        (MONTH_AGGREGATE_URL, {'deviceSn': DEVICE_SN, 'startDate': start_date, 'endDate': end_date})
    ]

    data_results = []
	@@ -63,24 +50,31 @@ def fetch_data(token):
        data_results.append(data)
    return data_results

def main():
    try:
        token = get_auth_token()
        realtime_data, day_aggregate_data, month_aggregate_data = fetch_data(token)

        combined_data = {}
        combined_data.update(realtime_data.get('body', {}))
        combined_data.update(day_aggregate_data.get('body', {}))
        combined_data['productionThisMonth'] = month_aggregate_data.get('body', {}).get('pvGeneration', 'N/A')

        if not combined_data:
            return {'error': 'Failed to decode data.'}

        return combined_data
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        logging.error(f'Error fetching data: {str(e)}')
        return {'error': str(e)}

if __name__ == '__main__':
    result = main()
    print(result)
