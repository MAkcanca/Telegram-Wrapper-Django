from rest_framework import serializers


class ReadMessageSerializer(serializers.Serializer):
    token = serializers.CharField()
    phone = serializers.CharField()


class TokenPhoneSerializer(serializers.Serializer):
    token = serializers.CharField()
    phone = serializers.CharField()

class TokenIdSerializer(serializers.Serializer):
    token = serializers.CharField()
    entity_id = serializers.CharField()


class SubmitCodeSerializer(serializers.Serializer):
    token = serializers.CharField()
    phone = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField(required=False)


class SendMessageSerializer(serializers.Serializer):
    token = serializers.CharField()
    sender = serializers.CharField()
    receiver = serializers.CharField()
    message = serializers.CharField()

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
