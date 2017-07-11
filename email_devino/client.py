import base64
import datetime
import requests
import os

REST_URL = 'https://integrationapi.net/email/v1'
SETTING_ADDRESS_SENDER = '/UserSettings/SenderAddresses'
MAILING_LIST = '/Tasks'
TEMPLATE = '/Templates'
STATE = '/Statistics'
STATE_DETAILING = '/Statistics/Messages'
TRANSACTIONAL_EMAIL = '/Messages'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_DELETE = 'delete'
METHOD_PUT = 'put'


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
        params = {
            'format': 'json',
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def add_address_sender(self, address: str) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        data = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), data=data, params=params,
                               method=METHOD_POST)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), [])

    def del_address_sender(self, address: str) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        data = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), data=data, params=params,
                               method=METHOD_DELETE)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), [])

    def get_mailing_list(self, items_range: str = None) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        headers = self._get_auth_header()
        if items_range:
            headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(MAILING_LIST, headers, params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def get_mailing(self, id_mailing: int) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        request_path = os.path.join(MAILING_LIST, str(id_mailing))
        answer = self._request(request_path, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def add_mailing(self, data: dict) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        answer = self._request(MAILING_LIST, self._get_auth_header(), data=data, params=params, method=METHOD_POST)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def edit_mailing(self, id_mailing: int, data: dict) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        request_path = os.path.join(MAILING_LIST, str(id_mailing))
        answer = self._request(request_path, self._get_auth_header(), data=data, params=params, method=METHOD_PUT)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def edit_status_mailing(self, id_mailing: int, task_state: str) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        data = {
            'State': task_state,
        }
        request_path = os.path.join(MAILING_LIST, str(id_mailing), 'State')
        answer = self._request(request_path, self._get_auth_header(), data=data, params=params, method=METHOD_PUT)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def get_template(self, id_template: id) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        request_path = os.path.join(TEMPLATE, id_template)
        answer = self._request(request_path, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def add_template(self, data: dict) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        answer = self._request(TEMPLATE, self._get_auth_header(), data=data, params=params, method=METHOD_POST)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def edit_template(self, id_template: int, data: dict) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), data=data, params=params, method=METHOD_PUT)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def del_template(self, id_template: int) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), params=params, method=METHOD_DELETE)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def get_state(self, id_mailing: int, ds: datetime.datetime, de: datetime.datetime) -> ApiAnswer:
        params = {
            'format': 'json',
            'TaskId': id_mailing,
            'StartDateTime': ds,
            'EndDateTime': de,
        }
        answer = self._request(STATE, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def get_state_detailing(self, id_mailing: int, ds: datetime.datetime, de: datetime.datetime,
                            state: str = '', items_range: str = None) -> ApiAnswer:
        params = {
            'format': 'json',
            'TaskId': id_mailing,
            'StartDateTime': ds,
            'EndDateTime': de,
            'State': state,
        }
        headers = self._get_auth_header()
        if items_range:
            headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(STATE_DETAILING, headers, params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def send_transactional_message(self, data: dict) -> ApiAnswer:
        params = {
            'format': 'json',
        }
        answer = self._request(TRANSACTIONAL_EMAIL, self._get_auth_header(), data=data, params=params,
                               method=METHOD_POST)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

    def get_status_transactional_message(self, data: list) -> ApiAnswer:
        params = {
            'format': 'json'
        }
        request_path = os.path.join(TRANSACTIONAL_EMAIL, ','.join(data))
        answer = self._request(request_path, self._get_auth_header(), params=params)
        return ApiAnswer(answer.get('Code'), answer.get('Description'), answer.get('Result'))

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
            elif method == METHOD_DELETE:
                response = requests.delete(request_url, data=data, params=params, headers=headers)
            else:
                response = requests.put(request_url, data=data, params=params, headers=headers)
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
