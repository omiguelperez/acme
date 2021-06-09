from collections import OrderedDict

from src.workflow.utils.abstracts import AbstractAuthenticationClass
from src.workflow.utils.exceptions import (
    InvalidActionException,
    InsufficientBalanceException,
)


class WorkflowParamExtractorMixin:

    def extract_param_value(self, from_id, param_id):
        if from_id == 'start':
            return self.workflow_data['trigger']['params'][param_id]
        else:
            for step_data in self.workflow_data['steps']:
                if from_id == step_data['id'] and param_id in step_data['params'].keys():
                    return self.extract_param_value(
                        from_id=step_data['params'][param_id]['from_id'],
                        param_id=step_data['params'][param_id]['param_id'],
                    )
        return None

    def get_params(self, current_step):
        params = {}
        for param, source in current_step['params'].items():
            if type(source) in (dict, OrderedDict):
                if source['from_id'] is None:
                    params |= {
                        param: source['value']
                    }
                else:
                    params |= {
                        param: self.extract_param_value(
                            from_id=source['from_id'],
                            param_id=source['param_id']
                        )
                    }
            else:
                params |= {param: source}
        return params

    def hide_secret_params(self, params):
        hidden_params = ['pin']
        for param in params:
            if param in hidden_params:
                params |= {param: '****'}
        return params


class WorkflowActionsMixin:

    def validate_account(self, **params):
        user_id = params.get('user_id')
        pin = params.get('pin')
        assert user_id is not None, "'user_id' can't be null"
        assert pin is not None, "'pin' can't be null"

        auth_data = self.authentication_class.authenticate(user_id=user_id, pin=pin)
        self.initial_balance = self.new_balance = auth_data['balance']
        self.user_id = user_id
        return {
            'is_valid': auth_data['is_valid'],
            'balance': self.initial_balance,
        }

    def deposit_money(self, **params):
        self.new_balance += params['money']
        return {'balance': self.new_balance}

    def withdraw_in_dollars(self, **params):
        if params['money'] > self.new_balance:
            self.new_balance = None
            raise InsufficientBalanceException

        self.new_balance -= params['money']
        return {'balance': self.new_balance}

    def get_account_balance(self, **params):
        return {'balance': self.new_balance}


class Workflow(WorkflowParamExtractorMixin,
               WorkflowActionsMixin):

    def __init__(
            self,
            workflow_data,
            authentication_class: AbstractAuthenticationClass
    ):
        self.workflow_data = workflow_data
        self.authentication_class = authentication_class

        self.initial_balance = None
        self.new_balance = None
        self.user_id = None

        self.authentication_class = authentication_class

        self.logs: list = []

    def execute_action(self, action_name, **params):
        if action_method := getattr(self, action_name, None):
            return action_method(**params)
        raise InvalidActionException

    def process_step(self, current_step):
        if action := current_step.get('action'):
            params = self.get_params(current_step)
            output = self.execute_action(action, **params)
            self.logs.append({
                'params': self.hide_secret_params(params),
                'id': current_step['id'],
                'action': action,
                'output': output,
            })
        self.run_transitions(current_step['transitions'])

    def run_transitions(self, transitions):
        for transition in transitions:
            if self.check_conditions(transition['condition']):
                if next_step := self.get_step(transition['target']):
                    self.process_step(next_step)

    def get_step_output(self, from_id, field_id):
        for log in self.logs:
            if log['id'] == from_id:
                return log['output'][field_id]
        return None

    def check_conditions(self, conditions):
        condition_results = []
        for condition in conditions:
            step_output = self.get_step_output(
                from_id=condition['from_id'],
                field_id=condition['field_id']
            )
            operator = condition['operator']
            if operator == 'gte':
                operator = 'ge'
            if operator == 'lte':
                operator = 'le'
            condition_value = condition['value']
            is_success = getattr(step_output, f'__{operator}__')(condition_value)
            condition_results.append(is_success)
        return all(condition_results)

    def get_step(self, step_id):
        for step in self.workflow_data['steps']:
            if step['id'] == step_id:
                return step
        return None

    def run_trigger(self):
        self.process_step(self.workflow_data['trigger'])
