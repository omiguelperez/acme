from src.workflow.utils.abstracts import AbstractAuthenticationClass


class Workflow:

    authentication_class: AbstractAuthenticationClass
    logs: list = []

    def __init__(self, workflow_data, authentication_class):
        self.workflow_data = workflow_data
        self.authentication_class = authentication_class

        self.initial_balance = None
        self.new_balance = None

    def get_params(self):
        return {}

    def execute_action(self, action_name, **params):
        pass

    def process_step(self, current_step):
        params = self.get_params()
        self.execute_action(current_step['action'], **params)
        self.run_transitions(current_step['transitions'])

    def run_transitions(self, transitions):
        for transition in transitions:
            if self.check_conditions(transition['conditions']):
                if next_step := self.get_step(transition['target']):
                    self.process_step(next_step)

    def check_conditions(self, conditions):
        pass

    def get_step(self, step_id):
        return {}

    def follow(self, current_step):
        if self.check_conditions(current_step['conditions']):
            if next_step := self.get_step(current_step['target']):
                self.process_step(next_step)

    def run_trigger(self):
        self.process_step(self.workflow_data['trigger'])
