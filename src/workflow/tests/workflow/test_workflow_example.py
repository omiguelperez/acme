import json
from decimal import Decimal
from pathlib import Path

from django.test import TestCase

from src.workflow.tests.factories import UserFactory, AccountFactory
from src.workflow.utils.authentication import UserPINAuthenticationClass
from src.workflow.utils.workflow import Workflow

workflow_example_path = Path(__file__).resolve().parent.parent / 'workflow_example.json'


class WorkflowExampleTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(
            user_id='105398891',
            pin=2090
        )
        self.account = AccountFactory(
            user=self.user,
            balance=Decimal(0)
        )

    def test_process_workflow_path_1(self):
        with open(workflow_example_path) as workflow_example_file:
            self.account.balance = Decimal(150_000)
            self.account.save()

            workflow_input_data = json.loads(workflow_example_file.read())

            workflow = Workflow(
                workflow_data=workflow_input_data,
                authentication_class=UserPINAuthenticationClass,
            )
            workflow.run_trigger()

            self.assertEqual(len(workflow.logs), 4)

            validate_account_log = workflow.logs[0]
            self.assertEqual(validate_account_log['action'], 'validate_account')
            self.assertEqual(validate_account_log['id'], 'validate_account')
            self.assertEqual(validate_account_log['params']['user_id'], '105398891')
            self.assertEqual(validate_account_log['params']['pin'], '****')
            self.assertTrue(validate_account_log['output']['is_valid'])

            account_balance_log = workflow.logs[1]
            self.assertEqual(account_balance_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_log['id'], 'account_balance')
            self.assertEqual(account_balance_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_log['output']['balance'], Decimal(150_000))

            withdraw_log = workflow.logs[2]
            self.assertEqual(withdraw_log['action'], 'withdraw_in_dollars')
            self.assertEqual(withdraw_log['id'], 'withdraw_30')
            self.assertEqual(withdraw_log['params']['user_id'], '105398891')
            self.assertEqual(withdraw_log['params']['money'], 30)
            self.assertEqual(withdraw_log['output']['balance'], Decimal(149_970))

            account_balance_end_log = workflow.logs[3]
            self.assertEqual(account_balance_end_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_end_log['id'], 'account_balance_end_30')
            self.assertEqual(account_balance_end_log['params']['user_id'], '105398891')
            self.assertEqual(
                account_balance_end_log['output']['balance'],
                Decimal(149_970)
            )

            self.assertEqual(workflow.initial_balance, Decimal(150_000))
            self.assertEqual(workflow.new_balance, Decimal(149_970))

    def test_process_workflow_path_2(self):
        with open(workflow_example_path) as workflow_example_file:
            self.account.balance = Decimal(70_000)
            self.account.save()

            workflow_input_data = json.loads(workflow_example_file.read())

            workflow = Workflow(
                workflow_data=workflow_input_data,
                authentication_class=UserPINAuthenticationClass,
            )
            workflow.run_trigger()

            self.assertEqual(len(workflow.logs), 6)

            validate_account_log = workflow.logs[0]
            self.assertEqual(validate_account_log['action'], 'validate_account')
            self.assertEqual(validate_account_log['id'], 'validate_account')
            self.assertEqual(validate_account_log['params']['user_id'], '105398891')
            self.assertEqual(validate_account_log['params']['pin'], '****')
            self.assertTrue(validate_account_log['output']['is_valid'])

            account_balance_log = workflow.logs[1]
            self.assertEqual(account_balance_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_log['id'], 'account_balance')
            self.assertEqual(account_balance_log['params']['user_id'], '105398891')
            self.assertEqual(account_balance_log['output']['balance'], Decimal(70_000))

            deposit_200_log = workflow.logs[2]
            self.assertEqual(deposit_200_log['action'], 'deposit_money')
            self.assertEqual(deposit_200_log['id'], 'deposit_200')
            self.assertEqual(deposit_200_log['params']['user_id'], '105398891')
            self.assertEqual(deposit_200_log['params']['money'], Decimal(200_000))
            self.assertEqual(deposit_200_log['output']['balance'], Decimal(270_000))

            account_balance_200_log = workflow.logs[3]
            self.assertEqual(account_balance_200_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_200_log['id'], 'account_balance_200')
            self.assertEqual(account_balance_200_log['params']['user_id'], '105398891')
            self.assertEqual(
                account_balance_200_log['output']['balance'],
                Decimal(270_000)
            )

            withdraw_50_log = workflow.logs[4]
            self.assertEqual(withdraw_50_log['action'], 'withdraw_in_dollars')
            self.assertEqual(withdraw_50_log['id'], 'withdraw_50')
            self.assertEqual(withdraw_50_log['params']['user_id'], '105398891')
            self.assertEqual(withdraw_50_log['params']['money'], Decimal(50_000))
            self.assertEqual(withdraw_50_log['output']['balance'], Decimal(220_000))

            account_balance_end_log = workflow.logs[5]
            self.assertEqual(account_balance_end_log['action'], 'get_account_balance')
            self.assertEqual(account_balance_end_log['id'], 'account_balance_end_50')
            self.assertEqual(account_balance_end_log['params']['user_id'], '105398891')
            self.assertEqual(
                account_balance_end_log['output']['balance'],
                Decimal(220_000)
            )

            self.assertEqual(workflow.initial_balance, Decimal(70_000))
            self.assertEqual(workflow.new_balance, Decimal(220_000))
