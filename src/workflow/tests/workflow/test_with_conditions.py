from decimal import Decimal

from django.test import TestCase

from src.workflow.tests.factories import UserFactory, AccountFactory
from src.workflow.utils.authentication import UserPINAuthenticationClass
from src.workflow.utils.workflow import Workflow


class WorkflowWithConditionsTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory(
            user_id='12345',
            pin=1234
        )
        self.account = AccountFactory(
            user=self.user,
            balance=Decimal(0)
        )

    def test_workflow_condition_equal_account_validation_status(self):
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
                            'condition': [
                                {
                                    'from_id': 'validate_account',
                                    'field_id': 'is_valid',
                                    'operator': 'eq',
                                    'value': True,
                                }
                            ],
                            'target': 'account_balance',
                        }
                    ]
                },
                {
                    'id': 'account_balance',
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

        self.assertEqual(len(workflow.logs), 2)  # validate account and get account balance

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance')
        self.assertEqual(get_balance_log['params']['user_id'], '12345')
        self.assertEqual(get_balance_log['output']['balance'], Decimal(200_000))

        self.assertEqual(workflow.initial_balance, Decimal(200_000))
        self.assertEqual(workflow.new_balance, Decimal(200_000))

    def test_workflow_condition_greater_than_balance(self):
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
                            'condition': [
                                {
                                    'from_id': 'validate_account',
                                    'field_id': 'is_valid',
                                    'operator': 'eq',
                                    'value': True,
                                }
                            ],
                            'target': 'account_balance',
                        }
                    ]
                },
                {
                    'id': 'account_balance',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                    },
                    'action': 'get_account_balance',
                    'transitions': [
                        {
                            'condition': [
                                {
                                    'from_id': 'account_balance',
                                    'field_id': 'balance',
                                    'operator': 'gt',
                                    'value': 199_999,
                                }
                            ],
                            'target': 'withdraw_150'
                        }
                    ]
                },
                {
                    'id': 'withdraw_150',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(150_000),
                        }
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

        self.assertEqual(len(workflow.logs), 3)  # validate account, get balance and withdraw

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance')
        self.assertEqual(get_balance_log['params']['user_id'], '12345')
        self.assertEqual(get_balance_log['output']['balance'], Decimal(200_000))

        withdraw_log = workflow.logs[2]
        self.assertEqual(withdraw_log['action'], 'withdraw_in_dollars')
        self.assertEqual(withdraw_log['id'], 'withdraw_150')
        self.assertEqual(withdraw_log['params']['user_id'], '12345')
        self.assertEqual(withdraw_log['params']['money'], Decimal(150_000))
        self.assertEqual(withdraw_log['output']['balance'], Decimal(50_000))

        self.assertEqual(workflow.initial_balance, Decimal(200_000))
        self.assertEqual(workflow.new_balance, Decimal(50_000))

    def test_workflow_condition_greater_than_or_equal_balance(self):
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
                            'condition': [
                                {
                                    'from_id': 'validate_account',
                                    'field_id': 'is_valid',
                                    'operator': 'eq',
                                    'value': True,
                                }
                            ],
                            'target': 'account_balance',
                        }
                    ]
                },
                {
                    'id': 'account_balance',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                    },
                    'action': 'get_account_balance',
                    'transitions': [
                        {
                            'condition': [
                                {
                                    'from_id': 'account_balance',
                                    'field_id': 'balance',
                                    'operator': 'gte',
                                    'value': Decimal(200_000),
                                }
                            ],
                            'target': 'withdraw_200'
                        }
                    ]
                },
                {
                    'id': 'withdraw_200',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(200_000),
                        }
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

        self.assertEqual(len(workflow.logs), 3)  # validate account, get balance and withdraw

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance')
        self.assertEqual(get_balance_log['params']['user_id'], '12345')
        self.assertEqual(get_balance_log['output']['balance'], Decimal(200_000))

        withdraw_log = workflow.logs[2]
        self.assertEqual(withdraw_log['action'], 'withdraw_in_dollars')
        self.assertEqual(withdraw_log['id'], 'withdraw_200')
        self.assertEqual(withdraw_log['params']['user_id'], '12345')
        self.assertEqual(withdraw_log['params']['money'], Decimal(200_000))
        self.assertEqual(withdraw_log['output']['balance'], Decimal(0))

        self.assertEqual(workflow.initial_balance, Decimal(200_000))
        self.assertEqual(workflow.new_balance, Decimal(0))

    def test_workflow_condition_lower_than_balance(self):
        self.account.balance = Decimal(40_000)
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
                            'condition': [
                                {
                                    'from_id': 'validate_account',
                                    'field_id': 'is_valid',
                                    'operator': 'eq',
                                    'value': True,
                                }
                            ],
                            'target': 'account_balance',
                        }
                    ]
                },
                {
                    'id': 'account_balance',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                    },
                    'action': 'get_account_balance',
                    'transitions': [
                        {
                            'condition': [
                                {
                                    'from_id': 'account_balance',
                                    'field_id': 'balance',
                                    'operator': 'lt',
                                    'value': Decimal(50_000),
                                }
                            ],
                            'target': 'deposit_50'
                        }
                    ]
                },
                {
                    'id': 'deposit_50',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(50_000),
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

        self.assertEqual(len(workflow.logs), 3)  # validate account, get balance and deposit

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance')
        self.assertEqual(get_balance_log['params']['user_id'], '12345')
        self.assertEqual(get_balance_log['output']['balance'], Decimal(40_000))

        deposit_log = workflow.logs[2]
        self.assertEqual(deposit_log['action'], 'deposit_money')
        self.assertEqual(deposit_log['id'], 'deposit_50')
        self.assertEqual(deposit_log['params']['user_id'], '12345')
        self.assertEqual(deposit_log['params']['money'], Decimal(50_000))
        self.assertEqual(deposit_log['output']['balance'], Decimal(90_000))

        self.assertEqual(workflow.initial_balance, Decimal(40_000))
        self.assertEqual(workflow.new_balance, Decimal(90_000))

    def test_workflow_condition_lower_than_or_equal_balance(self):
        self.account.balance = Decimal(50_000)
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
                            'condition': [
                                {
                                    'from_id': 'validate_account',
                                    'field_id': 'is_valid',
                                    'operator': 'eq',
                                    'value': True,
                                }
                            ],
                            'target': 'account_balance',
                        }
                    ]
                },
                {
                    'id': 'account_balance',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                    },
                    'action': 'get_account_balance',
                    'transitions': [
                        {
                            'condition': [
                                {
                                    'from_id': 'account_balance',
                                    'field_id': 'balance',
                                    'operator': 'lte',
                                    'value': Decimal(50_000),
                                }
                            ],
                            'target': 'deposit_50'
                        }
                    ]
                },
                {
                    'id': 'deposit_50',
                    'params': {
                        'user_id': {
                            'from_id': 'start',
                            'param_id': 'user_id',
                        },
                        'money': {
                            'from_id': None,
                            'value': Decimal(50_000),
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

        self.assertEqual(len(workflow.logs), 3)  # validate account, get balance and deposit

        validate_account_log = workflow.logs[0]
        self.assertEqual(validate_account_log['action'], 'validate_account')
        self.assertEqual(validate_account_log['id'], 'validate_account')
        self.assertEqual(validate_account_log['params']['user_id'], '12345')
        self.assertEqual(validate_account_log['params']['pin'], '****')
        self.assertTrue(validate_account_log['output']['is_valid'])

        get_balance_log = workflow.logs[1]
        self.assertEqual(get_balance_log['action'], 'get_account_balance')
        self.assertEqual(get_balance_log['id'], 'account_balance')
        self.assertEqual(get_balance_log['params']['user_id'], '12345')
        self.assertEqual(get_balance_log['output']['balance'], Decimal(50_000))

        deposit_log = workflow.logs[2]
        self.assertEqual(deposit_log['action'], 'deposit_money')
        self.assertEqual(deposit_log['id'], 'deposit_50')
        self.assertEqual(deposit_log['params']['user_id'], '12345')
        self.assertEqual(deposit_log['params']['money'], Decimal(50_000))
        self.assertEqual(deposit_log['output']['balance'], Decimal(100_000))

        self.assertEqual(workflow.initial_balance, Decimal(50_000))
        self.assertEqual(workflow.new_balance, Decimal(100_000))
