import base64
import datetime
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
    def __init__(self, code: str, description: str, result: list, request_data):
        self.code = code
        self.description = description
        self.result = result
        self.request_data = request_data

    @classmethod
    def create(cls, answer_data: dict, request_data=None):
        return cls(
            code=answer_data.get('Code'),
            description=answer_data.get('Description'),
            result=answer_data.get('Result'),
            request_data=request_data,
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
        json = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def del_address_sender(self, address: str) -> ApiAnswer:
        request_path = os.path.join(SETTING_ADDRESS_SENDER, address)
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer, address)

    def get_bulk_list(self, items_range: str = '1-100') -> ApiAnswer:
        headers = self._get_auth_header()
        headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(BULK, headers)
        return ApiAnswer.create(answer)

    def get_bulk(self, id_bulk: int) -> ApiAnswer:
        request_path = os.path.join(BULK, str(id_bulk))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, id_bulk)

    def add_bulk(self, name: str, sender_email: str, sender_name: str, subject: str, text: str, type_bulk: int,
                 start_datetime: datetime.datetime = None, end_datetime: datetime.datetime = None, user_id: str = "",
                 contact_list: list = None, template_id: str = "",  duplicates: bool = None) -> ApiAnswer:
        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name,
            },
            "Subject": subject,
            "Text": text,
            "Type": type_bulk,
            "UserCampaignId": user_id,
            "TemplateId": template_id,
            "SendDuplicates": duplicates
        }
        if contact_list:
            json["ContactGroups"] = [{"Id": id_contact, "Included": included} for id_contact, included in contact_list]
        if start_datetime:
            json['StartDateTime'] = start_datetime.strftime("%m/%d/%Y %h:%m:%s")
        if end_datetime:
            json['EndDateTime'] = end_datetime.strftime("%m/%d/%Y %h:%m:%s")
        answer = self._request(BULK, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def edit_bulk(self, id_bulk: int, name: str, sender_email: str, sender_name: str, subject: str, text: str,
                  type_bulk: int, start_datetime: datetime.datetime = None, end_datetime: datetime.datetime = None,
                  user_id: str = "", contact_list: list = None, template_id: str = "",
                  duplicates: bool = None) -> ApiAnswer:
        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name,
            },
            "Subject": subject,
            "Text": text,
            "Type": type_bulk,
            "UserCampaignId": user_id,
            "TemplateId": template_id,
            "SendDuplicates": duplicates
        }
        if contact_list:
            json["ContactGroups"] = [{"Id": id_contact, "Included": included} for id_contact, included in contact_list]
        if start_datetime:
            json['StartDateTime'] = start_datetime.strftime("%m/%d/%Y %h:%m:%s")
        if end_datetime:
            json['EndDateTime'] = end_datetime.strftime("%m/%d/%Y %h:%m:%s")
        request_path = os.path.join(BULK, str(id_bulk))
        answer = self._request(request_path, self._get_auth_header(), json=json, method=METHOD_PUT)
        json['id'] = id_bulk
        return ApiAnswer.create(answer, json)

    def edit_bulk_status(self, id_bulk: int, task_state: str) -> ApiAnswer:
        json = {
            'State': task_state,
        }
        request_path = os.path.join(BULK, str(id_bulk), 'State')
        answer = self._request(request_path, self._get_auth_header(), json=json, method=METHOD_PUT)
        json['id'] = id_bulk
        return ApiAnswer.create(answer, json)

    def get_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, id_template)

    def add_template(self, name: str, text: str, sender_email: str = "", sender_name: str = "",
                     subject: str = "", user_template_id: str = "") -> ApiAnswer:
        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name
            },
            "Subject": subject,
            "Text": text,
            "UserTemplateId": user_template_id,
        }
        answer = self._request(TEMPLATE, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def edit_template(self, id_template: int, name: str, text: str, sender_email: str = "", sender_name: str = "",
                      subject: str = "", user_template_id: str = "") -> ApiAnswer:
        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name
            },
            "Subject": subject,
            "Text": text,
            "UserTemplateId": user_template_id,
        }
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), json=json, method=METHOD_PUT)
        json['id'] = id_template
        return ApiAnswer.create(answer, json)

    def del_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer, id_template)

    def get_state(self, id_bulk: int = None, start_date: datetime.date = None,
                  end_date: datetime.date = None) -> ApiAnswer:
        params = {
            'Login': self.login,
        }
        if id_bulk:
            params['TaskId'] = id_bulk
        if start_date and end_date:
            params['StartDateTime'] = start_date.strftime('%Y-%m-%d')
            params['EndDateTime'] = end_date.strftime('%Y-%m-%d')
        answer = self._request(STATE, self._get_auth_header(), params=params)
        return ApiAnswer.create(answer, params)

    def get_state_detailing(self, id_bulk: int = None, start_date: datetime.date = None, end_date: datetime.date = None,
                            state: str = '', items_range: str = '1-100') -> ApiAnswer:
        params = {
            'State': state,
            'Login': self.login
        }
        if id_bulk:
            params['TaskId'] = id_bulk
        if start_date and end_date:
            params['StartDateTime'] = start_date.strftime('%Y-%m-%d')
            params['EndDateTime'] = end_date.strftime('%Y-%m-%d')
        headers = self._get_auth_header()
        headers['Range'] = 'items={}'.format(items_range)

        answer = self._request(STATE_DETAILING, headers, params=params)
        return ApiAnswer.create(answer, params)

    def send_transactional_message(self, sender_email: str, sender_name: str, recipient_email: str, recipient_name: str,
                                   subject: str, text: str, user_message_id: str = "", user_campaign_id: str = "",
                                   template_id: str = "") -> ApiAnswer:
        json = {
            "Sender": {
                "Address": sender_email,
                "Name": sender_name
            },
            "Recipient": {
                "Address": recipient_email,
                "Name": recipient_name
            },
            "Subject": subject,
            "Text": text,
            "UserMessageId": user_message_id,
            "UserCampaignId": user_campaign_id,
            "TemplateId": template_id,
        }
        answer = self._request(TRANSACTIONAL_EMAIL, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def get_status_transactional_message(self, data: list) -> ApiAnswer:
        request_path = os.path.join(TRANSACTIONAL_EMAIL, ','.join(data))

        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, data)

    def _get_auth_header(self) -> dict:
        headers = {'Authorization':
                   'Basic {}'.format(base64.b64encode('{}:{}'.format(self.login, self.password).encode()).decode())}
        return headers

    def _request(self, path, headers, params=FORMAT, json=None, method=METHOD_GET):
        params['format'] = 'json'
        request_url = self.url + path

        try:
            if method == METHOD_GET:
                response = requests.get(request_url, params=params, headers=headers)
            elif method == METHOD_POST:
                response = requests.post(request_url, json=json, params=params, headers=headers)
            elif method == METHOD_DELETE:
                response = requests.delete(request_url, json=json, params=params, headers=headers)
            else:
                response = requests.put(request_url, json=json, params=params, headers=headers)
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
