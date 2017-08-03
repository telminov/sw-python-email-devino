import datetime
from unittest import TestCase
from unittest.mock import patch

from .. import client


class ApiAnswer(TestCase):
    def test_create(self):
        answer_data = {
            'Code': 'ok',
            'Description': 'ok',
            'Result': []
        }
        api_answer = client.ApiAnswer.create(answer_data)

        self.assertEqual(api_answer.code, answer_data['Code'])
        self.assertEqual(api_answer.description, answer_data['Description'])
        self.assertEqual(api_answer.result, answer_data['Result'])
        self.assertEqual(api_answer.request_data, None)


@patch.object(client, 'requests')
class DevinoClient(TestCase):
    def setUp(self):
        self.client = client.DevinoClient('test_login', 'test_passw')

    def test_request_get(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.get.called)

        response = self.client._request('/some_url/', {'test': 123})

        self.assertTrue(requests_mock.get.called)
        self.assertEqual(response, requests_mock.get.return_value.json.return_value)

    def test_request_post(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.post.called)

        response = self.client._request('/some_url/', {'test': 123}, method=client.METHOD_POST)

        self.assertTrue(requests_mock.post.called)
        self.assertEqual(response, requests_mock.post.return_value.json.return_value)

    def test_request_put(self, requests_mock):
        requests_mock.put.return_value.status_code = 200
        requests_mock.put.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.put.called)

        response = self.client._request('/some_url/', {'test': 123}, method=client.METHOD_PUT)

        self.assertTrue(requests_mock.put.called)
        self.assertEqual(response, requests_mock.put.return_value.json.return_value)

    def test_request_delete(self, requests_mock):
        requests_mock.delete.return_value.status_code = 200
        requests_mock.delete.return_value.json.return_value = 'ok'
        self.assertFalse(requests_mock.delete.called)

        response = self.client._request('/some_url/', {'test': 123}, method=client.METHOD_DELETE)

        self.assertTrue(requests_mock.delete.called)
        self.assertEqual(response, requests_mock.delete.return_value.json.return_value)

    def test_request_error(self, requests_mock):
        error_data = {'Code': 'internal_error', 'Description': 'test error'}
        requests_mock.get.return_value.status_code = 500
        requests_mock.get.return_value.json.return_value = error_data
        self.assertFalse(requests_mock.get.called)

        exception = None
        try:
            self.client._request('/some_url/', {'test': 123})
        except client.DevinoException as ex:
            exception = ex

        self.assertTrue(requests_mock.get.called)
        self.assertIsNotNone(exception)
        self.assertEqual(exception.http_status, requests_mock.get.return_value.status_code)
        self.assertEqual(exception.error.code, error_data['Code'])
        self.assertEqual(exception.error.description, error_data['Description'])

    def test_auth_header(self, requests_mock):
        response = self.client._get_auth_header()

        self.assertEqual(response['Authorization'], 'Basic dGVzdF9sb2dpbjp0ZXN0X3Bhc3N3')

    def test_get_sender_addresses(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Code': 'ok', 'Description': 'ok',
                                                            'Result': {'Address': 'test@test.test', 'Confirmed': True}}

        response = self.client.get_sender_addresses()
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.SETTING_ADDRESS_SENDER, call_args[0])

    def test_add_sender_address(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = {'Code': 'ok', 'Description': 'ok'}

        address = 'testtest@test.test'
        self.client.add_sender_address(address)

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.SETTING_ADDRESS_SENDER, call_args[0])
        self.assertEqual(address, call_kwargs['json']['SenderAddress'])

    def test_del_sender_address(self, requests_mock):
        requests_mock.delete.return_value.status_code = 200
        requests_mock.delete.return_value.json.return_value = {'Code': 'ok', 'Description': 'ok'}

        address = 'testtest@test.test'
        self.client.del_sender_address(address)

        call_args, call_kwargs = requests_mock.delete.call_args
        self.assertEqual(self.client.url + client.SETTING_ADDRESS_SENDER + '/' + address, call_args[0])

    def test_get_tasks(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': 1}

        response = self.client.get_tasks()
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.TASK, call_args[0])
        self.assertEqual('items=1-100', call_kwargs['headers']['Range'])

    def test_get_task(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': 1}

        id_task = 0
        response = self.client.get_task(id_task)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.TASK + '/' + str(id_task), call_args[0])

    def test_add_task(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = {'Result': 1}

        data = {
            'name': 'test name',
            'sender_email': 'test email',
            'sender_name': 'test sender name',
            'subject': 'test subj',
            'text': 'test text',
            'contact_list': [(0, True), (1, False)],
            'start': datetime.datetime(year=2017, month=8, day=1),
            'end': datetime.datetime(year=2017, month=9, day=1)

        }
        response = self.client.add_task(**data)
        self.assertEqual(response.result, requests_mock.post.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.TASK, call_args[0])
        self.assertEqual(data['name'], call_kwargs['json']['Name'])
        self.assertEqual(data['sender_email'], call_kwargs['json']['Sender']['Address'])
        self.assertEqual(data['sender_name'], call_kwargs['json']['Sender']['Name'])
        self.assertEqual(data['subject'], call_kwargs['json']['Subject'])
        self.assertEqual(data['text'], call_kwargs['json']['Text'])
        self.assertEqual(client.TYPE_TASK_NORMAL, call_kwargs['json']['Type'])
        self.assertEqual([{'Id': 0, 'Included': True}, {'Id': 1, 'Included': False}],
                         call_kwargs['json']['ContactGroups'])
        self.assertEqual(data['start'].strftime("%m/%d/%Y %H:%M:%S"), call_kwargs['json']['StartDateTime'])
        self.assertEqual(data['end'].strftime("%m/%d/%Y %H:%M:%S"), call_kwargs['json']['EndDateTime'])

    def test_edit_task(self, requests_mock):
        requests_mock.put.return_value.status_code = 200
        requests_mock.put.return_value.json.return_value = {'Result': 1}

        data = {
            'id_task': 1,
            'name': 'test name',
            'sender_email': 'test email',
            'sender_name': 'test sender name',
            'subject': 'test subj',
            'text': 'test text',
            'contact_list': [(0, True), (1, False)],
            'start': datetime.datetime(year=2017, month=8, day=1),
            'end': datetime.datetime(year=2017, month=9, day=1)

        }
        response = self.client.edit_task(**data)
        self.assertEqual(response.result, requests_mock.put.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.put.call_args
        self.assertEqual(self.client.url + client.TASK + '/' + str(data['id_task']), call_args[0])
        self.assertEqual(data['name'], call_kwargs['json']['Name'])
        self.assertEqual(data['sender_email'], call_kwargs['json']['Sender']['Address'])
        self.assertEqual(data['sender_name'], call_kwargs['json']['Sender']['Name'])
        self.assertEqual(data['subject'], call_kwargs['json']['Subject'])
        self.assertEqual(data['text'], call_kwargs['json']['Text'])
        self.assertEqual(client.TYPE_TASK_NORMAL, call_kwargs['json']['Type'])
        self.assertEqual([{'Id': 0, 'Included': True}, {'Id': 1, 'Included': False}],
                         call_kwargs['json']['ContactGroups'])
        self.assertEqual(data['start'].strftime("%m/%d/%Y %H:%M:%S"), call_kwargs['json']['StartDateTime'])
        self.assertEqual(data['end'].strftime("%m/%d/%Y %H:%M:%S"), call_kwargs['json']['EndDateTime'])

    def test_edit_task_status(self, requests_mock):
        requests_mock.put.return_value.status_code = 200
        requests_mock.put.return_value.json.return_value = {'Code': 'ok', 'Description': 'ok'}

        data = {
            'id_task': 1,
            'task_state': 1
        }
        self.client.edit_task_status(**data)

        call_args, call_kwargs = requests_mock.put.call_args
        self.assertEqual(self.client.url + client.TASK + '/' + str(data['id_task']) + '/State', call_args[0])
        self.assertEqual(data['task_state'], call_kwargs['json']['State'])

    def test_get_template(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': 1}

        id_template = 0
        response = self.client.get_template(id_template)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.TEMPLATE + '/' + str(id_template), call_args[0])

    def test_add_template(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = {'Result': 1, 'Code': 'ok', 'Description': 'ok'}

        data = {
            'name': 'test name',
            'text': 'test_text',
            'sender_email': 'test sender email',
            'sender_name': 'test sender name',
            'subject': 'test subject',
        }
        response = self.client.add_template(**data)
        self.assertEqual(response.result, requests_mock.post.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.TEMPLATE, call_args[0])
        self.assertEqual(data['name'], call_kwargs['json']['Name'])
        self.assertEqual(data['text'], call_kwargs['json']['Text'])
        self.assertEqual(data['sender_email'], call_kwargs['json']['Sender']['Address'])
        self.assertEqual(data['sender_name'], call_kwargs['json']['Sender']['Name'])
        self.assertEqual(data['subject'], call_kwargs['json']['Subject'])
        self.assertEqual('', call_kwargs['json']['UserTemplateId'])

    def test_edit_template(self, requests_mock):
        requests_mock.put.return_value.status_code = 200
        requests_mock.put.return_value.json.return_value = {'Result': 1, 'Code': 'ok', 'Description': 'ok'}

        data = {
            'id_template': 1,
            'name': 'test name',
            'text': 'test_text',
            'sender_email': 'test sender email',
            'sender_name': 'test sender name',
            'subject': 'test subject',
        }
        response = self.client.edit_template(**data)
        self.assertEqual(response.result, requests_mock.put.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.put.call_args
        self.assertEqual(self.client.url + client.TEMPLATE + '/' + str(data['id_template']), call_args[0])
        self.assertEqual(data['name'], call_kwargs['json']['Name'])
        self.assertEqual(data['text'], call_kwargs['json']['Text'])
        self.assertEqual(data['sender_email'], call_kwargs['json']['Sender']['Address'])
        self.assertEqual(data['sender_name'], call_kwargs['json']['Sender']['Name'])
        self.assertEqual(data['subject'], call_kwargs['json']['Subject'])
        self.assertEqual('', call_kwargs['json']['UserTemplateId'])

    def test_del_template(self, requests_mock):
        requests_mock.delete.return_value.status_code = 200
        requests_mock.delete.return_value.json.return_value = {'Code': 'ok', 'Description': 'ok'}

        id_template = 1
        self.client.del_template(id_template)

        call_args, call_kwargs = requests_mock.delete.call_args
        self.assertEqual(self.client.url + client.TEMPLATE + '/' + str(id_template), call_args[0])

    def test_get_state_with_id(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': {'NotSent': 0, 'Sent': 0, 'Delivered': 0,
                                                                       'Read': 0, 'Clicked': 0, 'Bounced': 0,
                                                                       'Rejected': 0, 'Total': 0}}
        id_task = 1
        response = self.client.get_state(id_task)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.STATE, call_args[0])
        self.assertEqual(id_task, call_kwargs['params']['TaskId'])

    def test_get_state_with_date(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': {'NotSent': 0, 'Sent': 0, 'Delivered': 0,
                                                                       'Read': 0, 'Clicked': 0, 'Bounced': 0,
                                                                       'Rejected': 0, 'Total': 0}}
        start = datetime.date(year=2017, month=8, day=1)
        end = datetime.date(year=2017, month=8, day=1)
        response = self.client.get_state(start=start, end=end)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.STATE, call_args[0])
        self.assertEqual(start.strftime('%Y-%m-%d'), call_kwargs['params']['StartDateTime'])
        self.assertEqual(end.strftime('%Y-%m-%d'), call_kwargs['params']['EndDateTime'])

    def test_get_state_detailing_with_id(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': {'State': '', 'Price': 0, 'Id': 0,
                                                                       'DestinationEmail': 'test@test.test',
                                                                       'LastUpdateUtc': '', 'CreatedDateUtc': ''}}
        id_task = 1
        response = self.client.get_state_detailing(id_task)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.STATE_DETAILING, call_args[0])
        self.assertEqual(id_task, call_kwargs['params']['TaskId'])

    def test_get_state_detailing_with_date(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': {'State': '', 'Price': 0, 'Id': 0,
                                                                       'DestinationEmail': 'test@test.test',
                                                                       'LastUpdateUtc': '', 'CreatedDateUtc': ''}}
        start = datetime.date(year=2017, month=8, day=1)
        end = datetime.date(year=2017, month=8, day=1)
        response = self.client.get_state_detailing(start=start, end=end)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.STATE_DETAILING, call_args[0])
        self.assertEqual(start.strftime('%Y-%m-%d'), call_kwargs['params']['StartDateTime'])
        self.assertEqual(end.strftime('%Y-%m-%d'), call_kwargs['params']['EndDateTime'])

    def test_send_message(self, requests_mock):
        requests_mock.post.return_value.status_code = 200
        requests_mock.post.return_value.json.return_value = {'Result': "test id"}

        data = {
            'sender_email': 'test sender email',
            'sender_name': 'test sender name',
            'recipient_email': 'test recipient email',
            'recipient_name': 'rest recipient name',
            'subject': 'test subject text',
            'text': 'test subject text',
        }
        response = self.client.send_transactional_message(**data)
        self.assertEqual(response.result, requests_mock.post.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.post.call_args
        self.assertEqual(self.client.url + client.TRANSACTIONAL_EMAIL, call_args[0])
        self.assertEqual(data['sender_email'], call_kwargs['json']['Sender']['Address'])
        self.assertEqual(data['sender_name'], call_kwargs['json']['Sender']['Name'])
        self.assertEqual(data['recipient_email'], call_kwargs['json']['Recipient']['Address'])
        self.assertEqual(data['recipient_name'], call_kwargs['json']['Recipient']['Name'])
        self.assertEqual(data['subject'], call_kwargs['json']['Subject'])
        self.assertEqual(data['text'], call_kwargs['json']['Text'])

    def test_status_messages(self, requests_mock):
        requests_mock.get.return_value.status_code = 200
        requests_mock.get.return_value.json.return_value = {'Result': {'MessageId': 'test id', 'Email': 'test email',
                                                                       'State': 'test sent'}}
        id_messages = ['test id', ]
        response = self.client.get_status_transactional_message(id_messages)
        self.assertEqual(response.result, requests_mock.get.return_value.json.return_value['Result'])

        call_args, call_kwargs = requests_mock.get.call_args
        self.assertEqual(self.client.url + client.TRANSACTIONAL_EMAIL + '/' + id_messages[0], call_args[0])
