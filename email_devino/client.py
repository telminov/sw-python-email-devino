import base64
import requests

REST_URL = 'https://integrationapi.net/email/v1'
SETTING_ADDRESS_SENDER = '/UserSettings/SenderAddresses'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_DELETE = 'delete'


class DevinoError:
    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description


class DevinoException(Exception):
    def __init__(self, message: str, http_status: int = None, error: DevinoError = None,
                 base_exception: Exception = None):
        self.message = message
        self.http_status = http_status
        self.error = error
        self.base_exception = base_exception


class ApiAnswer:
    def __init__(self, code: str, description: str, result: list):
        self.code = code
        self.description = description
        self.result = result


class DevinoClient:

    def __init__(self, login: str, password: str, url: str = REST_URL):
        self.login = login
        self.password = password
        self.url = url

    def get_addresses_sender(self) -> ApiAnswer:
        params = {'format': 'json'}
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def add_address_sender(self, address) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        data = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), data=data, params=params,
                               method=METHOD_POST)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), [])

    def del_address_sender(self, address) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        data = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), data=data, params=params,
                               method=METHOD_DELETE)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), [])

    def _get_auth_header(self) -> dict:
        headers = {'Authorization':
                   'Basic {}'.format(base64.b64encode('{}:{}'.format(self.login, self.password).encode()).decode())}
        return headers

    def _request(self, path, headers, params=None, data=None, method=METHOD_GET):
        request_url = self.url + path

        try:
            if method == METHOD_GET:
                response = requests.get(request_url, params=params, headers=headers)
            elif method == METHOD_POST:
                response = requests.post(request_url, data=data, params=params, headers=headers)
            else:
                response = requests.delete(request_url, data=data, params=params, headers=headers)
        except requests.ConnectionError as ex:
            raise DevinoException(
                message='Ошибка соединения',
                base_exception=ex,
            )

        if 400 <= response.status_code <= 500:
            error_description = response.json()
            error = DevinoError(
                code=error_description.get('Code'),
                description=error_description.get('Desc'),
            )
            raise DevinoException(
                message='Ошибка отправки {0}-запроса'.format(method),
                http_status=response.status_code,
                error=error,
            )

        return response.json()
