import base64
import datetime
import requests
import os

REST_URL = 'https://integrationapi.net/email/v1'
SETTING_ADDRESS_SENDER = '/UserSettings/SenderAddresses'
TASK = '/Tasks'
TEMPLATE = '/Templates'
STATE = '/Statistics'
STATE_DETAILING = '/Statistics/Messages'
TRANSACTIONAL_EMAIL = '/Messages'

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_DELETE = 'delete'
METHOD_PUT = 'put'

FORMAT = {'format': 'json'}

TYPE_TASK_NORMAL = 1
TYPE_TASK_BIRTH = 2
TYPE_TASKS = (TYPE_TASK_NORMAL, TYPE_TASK_BIRTH)

STATE_NEW = 0
STATE_CREATED = 1
STATE_STARTED = 2
STATE_STOPPED = 3
STATE_CANCELED = 4
STATE_FINISHED = 5
STATE_DELETED = 6
STATE_FAILED = 7
STATE_TASKS = (STATE_NEW, STATE_CREATED, STATE_STARTED, STATE_STOPPED, STATE_CANCELED,
               STATE_FINISHED, STATE_DELETED, STATE_FAILED)


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
    def __init__(self, code: str, description: str, result: list, request_data: dict):
        self.code = code
        self.description = description
        self.result = result
        self.request_data = request_data

    @classmethod
    def create(cls, answer_data: dict, request_data: dict = None):
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

    def get_sender_addresses(self) -> ApiAnswer:
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header())
        return ApiAnswer.create(answer)

    def add_sender_address(self, address: str) -> ApiAnswer:
        json = {
            'SenderAddress': address,
        }
        answer = self._request(SETTING_ADDRESS_SENDER, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def del_sender_address(self, address: str) -> ApiAnswer:
        request_path = os.path.join(SETTING_ADDRESS_SENDER, address)
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer, {'Address': address})

    def get_tasks(self, range_start: int = 1, range_end: int = 100) -> ApiAnswer:
        headers = self._get_auth_header()
        headers['Range'] = 'items={}-{}'.format(range_start, range_end)

        answer = self._request(TASK, headers)
        return ApiAnswer.create(answer)

    def get_task(self, id_task: int) -> ApiAnswer:
        request_path = os.path.join(TASK, str(id_task))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, {'Id': id_task})

    def add_task(self, name: str, sender_email: str, sender_name: str, subject: str, text: str,
                 type_task: int = TYPE_TASK_NORMAL, start: datetime.datetime = None,
                 end: datetime.datetime = None, user_id: str = "", contact_list: list = None,
                 template_id: str = "", duplicates: bool = None) -> ApiAnswer:
        """
        http://docs.devinotele.com/emailhttp.html#id14
        id = 1233 # example
        included = true # example
        contact_list = [(id, included), ]
        """
        assert type_task in TYPE_TASKS

        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name,
            },
            "Subject": subject,
            "Text": text,
            "Type": type_task,
            "UserCampaignId": user_id,
            "TemplateId": template_id,
            "SendDuplicates": duplicates
        }
        if contact_list:
            json["ContactGroups"] = [{"Id": id_contact, "Included": included} for id_contact, included in contact_list]
        if start:
            json['StartDateTime'] = start.strftime("%m/%d/%Y %H:%M:%S")
        if end:
            json['EndDateTime'] = end.strftime("%m/%d/%Y %H:%M:%S")
        answer = self._request(TASK, self._get_auth_header(), json=json, method=METHOD_POST)
        return ApiAnswer.create(answer, json)

    def edit_task(self, id_task: int, name: str, sender_email: str, sender_name: str, subject: str, text: str,
                  type_task: int = TYPE_TASK_NORMAL, start: datetime.datetime = None, end: datetime.datetime = None,
                  user_id: str = "", contact_list: list = None, template_id: str = "",
                  duplicates: bool = None) -> ApiAnswer:
        assert type_task in TYPE_TASKS

        json = {
            "Name": name,
            "Sender": {
                "Address": sender_email,
                "Name": sender_name,
            },
            "Subject": subject,
            "Text": text,
            "Type": type_task,
            "UserCampaignId": user_id,
            "TemplateId": template_id,
            "SendDuplicates": duplicates
        }
        if contact_list:
            json["ContactGroups"] = [{"Id": id_contact, "Included": included} for id_contact, included in contact_list]
        if start:
            json['StartDateTime'] = start.strftime("%m/%d/%Y %H:%M:%S")
        if end:
            json['EndDateTime'] = end.strftime("%m/%d/%Y %H:%M:%S")
        request_path = os.path.join(TASK, str(id_task))
        answer = self._request(request_path, self._get_auth_header(), json=json, method=METHOD_PUT)
        json['Id'] = id_task
        return ApiAnswer.create(answer, json)

    def edit_task_status(self, id_task: int, task_state: int) -> ApiAnswer:
        """
        http://docs.devinotele.com/emailhttp.html#id16
        """
        assert task_state in STATE_TASKS

        json = {
            'State': task_state,
        }
        request_path = os.path.join(TASK, str(id_task), 'State')
        answer = self._request(request_path, self._get_auth_header(), json=json, method=METHOD_PUT)
        json['Id'] = id_task
        return ApiAnswer.create(answer, json)

    def get_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, {'Id': id_template})

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
        json['Id'] = id_template
        return ApiAnswer.create(answer, json)

    def del_template(self, id_template: int) -> ApiAnswer:
        request_path = os.path.join(TEMPLATE, str(id_template))
        answer = self._request(request_path, self._get_auth_header(), method=METHOD_DELETE)
        return ApiAnswer.create(answer, {'Id': id_template})

    def get_state(self, id_task: int = None, start: datetime.date = None, end: datetime.date = None) -> ApiAnswer:
        params = {
            'Login': self.login,
        }
        if id_task:
            params['TaskId'] = id_task
        if start and end:
            params['StartDateTime'] = start.strftime('%Y-%m-%d')
            params['EndDateTime'] = end.strftime('%Y-%m-%d')
        answer = self._request(STATE, self._get_auth_header(), params=params)
        return ApiAnswer.create(answer, params)

    def get_state_detailing(self, id_task: int = None, start: datetime.date = None, end: datetime.date = None,
                            state: str = '', range_start: int = 1, range_end: int = 100) -> ApiAnswer:
        params = {
            'State': state,
            'Login': self.login
        }
        if id_task:
            params['TaskId'] = id_task
        if start and end:
            params['StartDateTime'] = start.strftime('%Y-%m-%d')
            params['EndDateTime'] = end.strftime('%Y-%m-%d')
        headers = self._get_auth_header()
        headers['Range'] = 'items={}-{}'.format(range_start, range_end)

        answer = self._request(STATE_DETAILING, headers, params=params)
        return ApiAnswer.create(answer, params)

    def send_transactional_message(self, sender_email: str, sender_name: str, recipient_email: str, recipient_name: str,
                                   subject: str, text: str, user_message_id: str = "", user_campaign_id: str = "",
                                   template_id: str = "") -> ApiAnswer:
        """
        Send single message
        """

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

    def get_status_transactional_message(self, id_messages: list) -> ApiAnswer:
        request_path = os.path.join(TRANSACTIONAL_EMAIL, ','.join(id_messages))

        answer = self._request(request_path, self._get_auth_header())
        return ApiAnswer.create(answer, {'id_{}'.format(x): id_messages[x] for x in range(len(id_messages))})

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
                description=error_description.get('Description'),
            )
            raise DevinoException(
                message='Ошибка отправки {0}-запроса'.format(method),
                http_status=response.status_code,
                error=error,
            )

        return response.json()
