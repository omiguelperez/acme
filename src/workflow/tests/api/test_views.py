import json
from decimal import Decimal
from pathlib import Path

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from src.workflow.models import Upload
from src.workflow.tests.factories import UserFactory, AccountFactory

workflow_example_path = Path(__file__).resolve().parent.parent / 'workflow_example.json'


class WorkflowAPITestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory(
            user_id='105398891',
            pin=2090
        )
        self.account = AccountFactory(
            user=self.user,
            balance=Decimal(0)
        )

        self.url = reverse('api:workflow:upload')

    def test_process_workflow_path_1(self):
        with open(workflow_example_path) as workflow_example_file:
            self.account.balance = Decimal(150_000)
            self.account.save()

            payload = {
                'file': workflow_example_file,
            }
            res = self.client.post(self.url, data=payload, format='multipart')

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

            res_data = res.json()
            upload_id = res_data['id']

            upload = Upload.objects.get(pk=upload_id)

            self.assertEqual(len(upload.logs), 4)

            validate_account_log = upload.logs[0]
            self.assertEqual(validate_account_log['action'], 'validate_account')
            self.assertEqual(validate_account_log['id'], 'validate_account')
            self.assertEqual(validate_account_log['params']['user_id'], '105398891')
            self.assertEqual(validate_account_log['params']['pin'], '****')
            self.assertTrue(validate_account_log['output']['is_valid'])

            account_balance_log = upload.logs[1]
            self.assertEqual(account_balance_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_log['id'], 'account_balance')
            self.assertEqual(account_balance_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_log['output']['balance'], '150000.00')

            withdraw_log = upload.logs[2]
            self.assertEqual(withdraw_log['action'], 'withdraw_in_dollars')
            self.assertEqual(withdraw_log['id'], 'withdraw_30')
            self.assertEqual(withdraw_log['params']['user_id'], '105398891')
            self.assertEqual(withdraw_log['params']['money'], 30)
            self.assertEqual(withdraw_log['output']['balance'], '149970.00')

            account_balance_end_log = upload.logs[3]
            self.assertEqual(account_balance_end_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_end_log['id'], 'account_balance_end_30')
            self.assertEqual(account_balance_end_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_end_log['output']['balance'], '149970.00')

            self.account.refresh_from_db()
            self.assertEqual(self.account.balance.to_decimal(), Decimal(149_970))

    def test_process_workflow_path_2(self):
        with open(workflow_example_path) as workflow_example_file:
            self.account.balance = Decimal(70_000)
            self.account.save()

            payload = {
                'file': workflow_example_file,
            }
            res = self.client.post(self.url, data=payload, format='multipart')

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

            res_data = res.json()
            upload_id = res_data['id']

            upload = Upload.objects.get(pk=upload_id)

            self.assertEqual(len(upload.logs), 6)

            validate_account_log = upload.logs[0]
            self.assertEqual(validate_account_log['action'], 'validate_account')
            self.assertEqual(validate_account_log['id'], 'validate_account')
            self.assertEqual(validate_account_log['params']['user_id'], '105398891')
            self.assertEqual(validate_account_log['params']['pin'], '****')
            self.assertTrue(validate_account_log['output']['is_valid'])

            account_balance_log = upload.logs[1]
            self.assertEqual(account_balance_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_log['id'], 'account_balance')
            self.assertEqual(account_balance_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_log['output']['balance'], '70000.00')

            deposit_200_log = upload.logs[2]
            self.assertEqual(deposit_200_log['action'], 'deposit_money')
            self.assertEqual(deposit_200_log['id'], 'deposit_200')
            self.assertEqual(deposit_200_log['params']['user_id'], '105398891')
            self.assertEqual(deposit_200_log['params']['money'], 200_000)
            self.assertEqual(deposit_200_log['output']['balance'], '270000.00')

            account_balance_200_log = upload.logs[3]
            self.assertEqual(account_balance_200_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_200_log['id'], 'account_balance_200')
            self.assertEqual(account_balance_200_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_200_log['output']['balance'], '270000.00')

            withdraw_50_log = upload.logs[4]
            self.assertEqual(withdraw_50_log['action'], 'withdraw_in_dollars')
            self.assertEqual(withdraw_50_log['id'], 'withdraw_50')
            self.assertEqual(withdraw_50_log['params']['user_id'], '105398891')
            self.assertEqual(withdraw_50_log['params']['money'], 50_000)
            self.assertEqual(withdraw_50_log['output']['balance'], '220000.00')

            account_balance_end_log = upload.logs[5]
            self.assertEqual(account_balance_end_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_end_log['id'], 'account_balance_end_50')
            self.assertEqual(account_balance_end_log['params']['user_id'], '105398891')
            self.assertEqual(
                account_balance_end_log['output']['balance'],
                '220000.00'
            )

            self.account.refresh_from_db()
            self.assertEqual(self.account.balance.to_decimal(), Decimal(220_000))

