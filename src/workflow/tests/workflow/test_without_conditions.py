from decimal import Decimal

from django.test import TestCase

from src.workflow.models import User
from src.workflow.tests.factories import UserFactory, AccountFactory
from src.workflow.utils.workflow import Workflow
from src.workflow.utils.authentication import UserPINAuthenticationClass
from src.workflow.utils.exceptions import (
    InsufficientBalanceException,
)


class BasicWorflowWithoutConditionsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = UserFactory(
            user_id='12345',
            pin=1234
        )
        AccountFactory(
            user=user,
            balance=Decimal(0)
        )

    def setUp(self):
        self.user = User.objects.get()
        self.account = self.user.account

    def test_basic_workflow_successful_deposit(self):
        workflow_input_data = {
            'steps': [
                {
                    'id': 'validate_account',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id'
                        },
                        'pin': {
                            'from_id': 'start',
                            'param_id': 'pin',
                        },
                    },
                    'action': 'validate_account',
                    'transitions': [
                        {
                            'target': 'deposit_200',
                            'condition': []
                        }
                    ]
                },
                {
                    'id': 'deposit_200',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(200_000),
                        },
                    },
                    'action': 'deposit_money',
                    'transitions': []
                }
            ],
            'trigger': {
                'params': {
                    'user_id': self.user.user_id,
                    'pin': self.user.pin,
                },
                'transitions': [
                    {
                        'target': 'validate_account',
                        'condition': [],
                    }
                ]
            }
        }

        workflow = Workflow(
            workflow_data=workflow_input_data,
            authentication_class=UserPINAuthenticationClass,
        )
        workflow.run_trigger()

        self.assertEqual(len(workflow.logs), 2)  # validate account and deposit

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        deposit_log = workflow.logs[1]
        self.assertEqual(deposit_log['action'], 'deposit_money')
        self.assertEqual(deposit_log['id'], 'deposit_200')
        self.assertEqual(deposit_log['params']['user_id'], '12345')
        self.assertEqual(deposit_log['params']['money'], Decimal(200_000))
        self.assertEqual(deposit_log['output']['balance'], Decimal(200_000))

        self.assertEqual(workflow.initial_balance, Decimal(0))
        self.assertEqual(workflow.new_balance, Decimal(200_000))

    def test_basic_workflow_failure_deposit_invalid_account(self):
        workflow_input_data = {
            'steps': [
                {
                    'id': 'validate_account',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id'
                        },
                        'pin': {
                            'from_id': 'start',
                            'param_id': 'pin',
                        },
                    },
                    'action': 'validate_account',
                    'transitions': []
                },
            ],
            'trigger': {
                'params': {
                    'user_id': 'invalid-user-id',
                    'pin': 0000,
                },
                'transitions': [
                    {
                        'target': 'validate_account',
                        'condition': [],
                    }
                ]
            }
        }

        workflow = Workflow(
            workflow_data=workflow_input_data,
            authentication_class=UserPINAuthenticationClass,
        )
        workflow.run_trigger()

        self.assertEqual(len(workflow.logs), 1)  # validate account

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], 'invalid-user-id')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertFalse(validate_account_log['output']['is_valid'])

        self.assertIsNone(workflow.initial_balance)
        self.assertIsNone(workflow.new_balance)

    def test_basic_workflow_successful_withdrawal(self):
        self.account.balance = Decimal(100_000)
        self.account.save()

        workflow_input_data = {
            'steps': [
                {
                    'id': 'validate_account',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id'
                        },
                        'pin': {
                            'from_id': 'start',
                            'param_id': 'pin',
                        },
                    },
                    'action': 'validate_account',
                    'transitions': [
                        {
                            'target': 'withdraw_30',
                            'condition': []
                        }
                    ]
                },
                {
                    'id': 'withdraw_30',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(30_000),
                        },
                    },
                    'action': 'withdraw_in_dollars',
                    'transitions': []
                }
            ],
            'trigger': {
                'params': {
                    'user_id': self.user.user_id,
                    'pin': self.user.pin,
                },
                'transitions': [
                    {
                        'target': 'validate_account',
                        'condition': [],
                    }
                ]
            }
        }

        workflow = Workflow(
            workflow_data=workflow_input_data,
            authentication_class=UserPINAuthenticationClass,
        )
        workflow.run_trigger()

        self.assertEqual(len(workflow.logs), 2)  # validate account and withdraw

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], self.user.user_id)
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        withdraw_log = workflow.logs[1]
        self.assertEqual(withdraw_log['action'], 'withdraw_in_dollars')
        self.assertEqual(withdraw_log['id'], 'withdraw_30')
        self.assertEqual(withdraw_log['params']['user_id'], self.user.user_id)
        self.assertEqual(withdraw_log['params']['money'], Decimal(30_000))
        self.assertEqual(withdraw_log['output']['balance'], Decimal(70_000))

        self.assertEqual(workflow.initial_balance, Decimal(100_000))
        self.assertEqual(workflow.new_balance, Decimal(70_000))

    def test_basic_workflow_failure_withdrawal_insuficient_money(self):
        workflow_input_data = {
            'steps': [
                {
                    'id': 'validate_account',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id'
                        },
                        'pin': {
                            'from_id': 'start',
                            'param_id': 'pin',
                        },
                    },
                    'action': 'validate_account',
                    'transitions': [
                        {
                            'target': 'withdraw_30',
                            'condition': []
                        }
                    ]
                },
                {
                    'id': 'withdraw_30',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(30_000),
                        },
                    },
                    'action': 'withdraw_in_dollars',
                    'transitions': []
                }
            ],
            'trigger': {
                'params': {
                    'user_id': self.user.user_id,
                    'pin': self.user.pin,
                },
                'transitions': [
                    {
                        'target': 'validate_account',
                        'condition': [],
                    }
                ]
            }
        }

        workflow = Workflow(
            workflow_data=workflow_input_data,
            authentication_class=UserPINAuthenticationClass,
        )
        self.assertRaises(InsufficientBalanceException, workflow.run_trigger)

        self.assertEqual(len(workflow.logs), 1)  # validate account

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], self.user.user_id)
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        self.assertEqual(workflow.initial_balance, Decimal(0))
        self.assertIsNone(workflow.new_balance)  # ignore applied balance modification operations

    def test_basic_workflow_get_current_balance(self):
        self.account.balance = Decimal(200_000)
        self.account.save()

        workflow_input_data = {
            'steps': [
                {
                    'id': 'validate_account',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id'
                        },
                        'pin': {
                            'from_id': 'start',
                            'param_id': 'pin',
                        },
                    },
                    'action': 'validate_account',
                    'transitions': [
                        {
                            'target': 'account_balance_end_200',
                            'condition': []
                        }
                    ]
                },
                {
                    'id': 'account_balance_end_200',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                    },
                    'action': 'get_account_balance',
                    'transitions': []
                }
            ],
            'trigger': {
                'params': {
                    'user_id': self.user.user_id,
                    'pin': self.user.pin,
                },
                'transitions': [
                    {
                        'target': 'validate_account',
                        'condition': [],
                    }
                ]
            }
        }

        workflow = Workflow(
            workflow_data=workflow_input_data,
            authentication_class=UserPINAuthenticationClass,
        )
        workflow.run_trigger()

        self.assertEqual(len(workflow.logs), 2)  # validate account and withdraw

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], self.user.user_id)
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance_end_200')
        self.assertEqual(get_balance_log['params']['user_id'], self.user.user_id)
        self.assertEqual(get_balance_log['output']['balance'], Decimal(200_000))

        self.assertEqual(workflow.initial_balance, Decimal(200_000))
        self.assertEqual(workflow.new_balance, Decimal(200_000))

