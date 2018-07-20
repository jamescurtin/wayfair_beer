import requests

class API:
    def __init__(self, base_url, header_api_key=None):
        self.base_url = base_url
        if header_api_key is not None:
            self.headers = {'x-api-key': header_api_key}
        else:
            self.headers = {}

    def get(self, endpoint, params=None):
    	url = '{}/{}'.format(self.base_url, endpoint)
    	result = requests.get(url, params=params, headers=self.headers)
    	return result.json()
