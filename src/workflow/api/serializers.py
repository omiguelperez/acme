import json

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers

from src.workflow.models import Upload, Account
from src.workflow.utils.authentication import UserPINAuthenticationClass
from src.workflow.utils.exceptions import WorkflowException
from src.workflow.utils.workflow import Workflow


class CustomConditionValueField(serializers.Field):
    def to_internal_value(self, data):
        return data


class ConditionSerializer(serializers.Serializer):
    from_id = serializers.CharField()
    field_id = serializers.CharField()
    operator = serializers.CharField()
    value = CustomConditionValueField()


class TransitionSerializer(serializers.Serializer):
    target = serializers.CharField()
    condition = ConditionSerializer(many=True)


class TriggerParamsSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    pin = serializers.IntegerField()


class TriggerSerializer(serializers.Serializer):
    params = TriggerParamsSerializer()
    transitions = TransitionSerializer(many=True)


class ParamSerializer(serializers.Serializer):
    from_id = serializers.CharField(allow_null=True)
    param_id = serializers.CharField(required=False)
    value = serializers.IntegerField(required=False)


class StepParamsSerializer(serializers.Serializer):
    user_id = ParamSerializer()
    pin = ParamSerializer(required=False)
    money = ParamSerializer(required=False)


class StepSerializer(serializers.Serializer):
    id = serializers.CharField()
    params = StepParamsSerializer()
    action = serializers.CharField()
    transitions = TransitionSerializer(many=True)


class WorkflowDataSerializer(serializers.Serializer):
    steps = StepSerializer(many=True)
    trigger = TriggerSerializer()


class WorkflowFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload
        fields = ('id', 'file', 'logs',)
        read_only_fields = ('id', 'logs',)
        extra_kwargs = {
            'file': {'write_only': True},
        }

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        json_data = json.loads(validated_data['file'].read())
        workflow_serializer = WorkflowDataSerializer(data=json_data)
        workflow_serializer.is_valid(raise_exception=True)
        self.context['workflow_data'] = workflow_serializer.validated_data

        return validated_data

    def save(self, **kwargs):
        upload = super().save(**kwargs)
        workflow = Workflow(
            workflow_data=self.context['workflow_data'],
            authentication_class=UserPINAuthenticationClass
        )
        try:
            workflow.run_trigger()
            if workflow.new_balance:
                account = Account.objects.get(user__user_id=workflow.user_id)
                account.balance = workflow.new_balance
                account.save()
                upload.success = True
        except WorkflowException:
            # handle exception, maybe send to sentry
            pass
        upload.logs = json.loads(
            json.dumps(
                workflow.logs,
                cls=DjangoJSONEncoder
            )
        )
        upload.save()
