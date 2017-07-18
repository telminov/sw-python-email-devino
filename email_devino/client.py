import base64
import requests
import os

REST_URL = 'https://integrationapi.net/email/v1'
SETTING_ADDRESS_SENDER = '/UserSettings/SenderAddresses'
BULK = '/Tasks'
TEMPLATE = '/Templates'
STATE = '/Statistics'
STATE_DETAILING = '/Statistics/Messages'
TRANSACTIONAL_EMAIL = '/Messages'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_DELETE = 'delete'
METHOD_PUT = 'put'

FORMAT = {'format': 'json'}


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

    @classmethod
    def create(cls, answer_data: dict):
        return cls(
            code=answer_data.get('Code'),
            description=answer_data.get('Description'),
            result=answer_data.get('Result'),
        )


class DevinoClient:

    def __init__(self, login: str, password: str, url: str = REST_URL):
        self.login = login
        self.password = password
        self.url = url

    def get_addresses_sender(self) -> ApiAnswer:
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header())
        return ApiAnswer.create(answer)

    def add_address_sender(self, address: str) -> ApiAnswer:
        data = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), data=data, method=METHOD_POST)
        return ApiAnswer.create(answer)

    def del_address_sender(self, address: str) -> ApiAnswer:
        request_path = os.path.join(SETTING_ADDRESS_SENDER, address)
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer)

    def get_bulk_list(self, items_range: str = '1-100') -> ApiAnswer:
        headers = self._get_auth_header()
        headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(BULK, headers)
        return ApiAnswer.create(answer)

    def get_bulk(self, id_bulk: int) -> ApiAnswer:
        request_path = os.path.join(BULK, str(id_bulk))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer)

    def add_bulk(self, data: dict) -> ApiAnswer:
        answer = self._request(BULK, self._get_auth_header(), data=data, method=METHOD_POST)
        return ApiAnswer.create(answer)

    def edit_bulk(self, id_bulk: int, data: dict) -> ApiAnswer:
        request_path = os.path.join(BULK, str(id_bulk))
        answer = self._request(request_path, self._get_auth_header(), data=data, method=METHOD_PUT)
        return ApiAnswer.create(answer)

    def edit_bulk_status(self, id_bulk: int, task_state: str) -> ApiAnswer:
        data = {
            'State': task_state,
        }
        request_path = os.path.join(BULK, str(id_bulk), 'State')
        answer = self._request(request_path, self._get_auth_header(), data=data, method=METHOD_PUT)
        return ApiAnswer.create(answer)

    def get_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer)

    def add_template(self, data: dict) -> ApiAnswer:
        answer = self._request(TEMPLATE, self._get_auth_header(), data=data, method=METHOD_POST)
        return ApiAnswer.create(answer)

    def edit_template(self, id_template: int, data: dict) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), data=data, method=METHOD_PUT)
        return ApiAnswer.create(answer)

    def del_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer)

    def get_state(self, id_bulk: int) -> ApiAnswer:
        params = {
            'TaskId': id_bulk,
        }
        answer = self._request(STATE, self._get_auth_header(), params=params)
        return ApiAnswer.create(answer)

    def get_state_detailing(self, id_bulk: int, state: str = '', items_range: str = '1-100') -> ApiAnswer:
        params = {
            'TaskId': id_bulk,
            'State': state,
        }
        headers = self._get_auth_header()
        headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(STATE_DETAILING, headers, params=params)
        return ApiAnswer.create(answer)

    def send_transactional_message(self, data: dict) -> ApiAnswer:
        answer = self._request(TRANSACTIONAL_EMAIL, self._get_auth_header(), data=data, method=METHOD_POST)
        return ApiAnswer.create(answer)

    def get_status_transactional_message(self, data: list) -> ApiAnswer:
        request_path = os.path.join(TRANSACTIONAL_EMAIL, ','.join(data))

        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer)

    def _get_auth_header(self) -> dict:
        headers = {'Authorization':
                   'Basic {}'.format(base64.b64encode('{}:{}'.format(self.login, self.password).encode()).decode())}
        return headers

    def _request(self, path, headers, params=FORMAT, data=None, method=METHOD_GET):
        params['format'] = 'json'
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
