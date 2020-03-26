from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from telethon.errors import RPCError, SessionPasswordNeededError

from telegramwrap.exceptions import TelegramAuthorizationException
from telegramwrap.models import TelegramAuthorization
from telegramwrap.serializers import TokenPhoneSerializer, SubmitCodeSerializer, SendMessageSerializer, \
    TokenIdSerializer, RegisterSerializer
from telegramwrap.tasks import attach_messagehook
from telegramwrap.utils import Telegram


class AttachWebhookView(GenericAPIView):
    serializer_class = TokenPhoneSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = TokenPhoneSerializer(data=request.data)
            if serializer.is_valid():
                attach_messagehook.delay(request.data.get("phone"))
                return Response({"success": True})


class GetEntityView(GenericAPIView):
    serializer_class = TokenIdSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = TokenIdSerializer(data=request.data)
            if serializer.is_valid():
                attach_messagehook.delay(request.data.get("phone"))
                return Response({"success": True})


class SubmitCodeView(GenericAPIView):
    serializer_class = SubmitCodeSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = SubmitCodeSerializer(data=request.data)
            if serializer.is_valid():
                phone, code, password = request.data.get("phone"), request.data.get("code"), request.data.get("password")
                user = Token.objects.get(key=request.data['token']).user
                auth = TelegramAuthorization.objects.get(user=user, phone=phone)
                client = Telegram.get_client(phone)
                try:
                    client.sign_in(auth.phone, code, phone_code_hash=auth.phone_code_hash)
                except SessionPasswordNeededError:
                    if password:
                        client.sign_in(password=password)
                    else:
                        return Response({
                            "success": False,
                            "message": "Two Factor Authorization enabled. Please provide both code and password"
                        })

                except RPCError as e:
                    return Response(
                        {"success": False,
                         "message": "Telegram exception occurred. %s. %s. %s" % (e.code, e.message, str(e))})

                except Exception as e:
                    return Response(
                        {"success": False, "message": "'Error occurred during telegram sign-in\n%s'" % e})

                client.disconnect()

                # do not store hash after successful login
                auth.phone_code_hash = None
                auth.save()

                return Response({"success": True})


class LogoutView(GenericAPIView):
    serializer_class = TokenPhoneSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = TokenPhoneSerializer(data=request.data)
            if serializer.is_valid():
                phone = request.data.get("phone")
                user = Token.objects.get(key=request.data['token']).user
                try:
                    telegram_authorization = TelegramAuthorization.objects.get(user=user, phone=phone)
                except TelegramAuthorization.DoesNotExist:
                    return Response({"success": False, "message": "Phone '%s' is invalid'" % phone})

                client = Telegram.get_client(telegram_authorization.phone)

                if client.log_out():
                    # delete auth record
                    telegram_authorization.delete()
                    return Response({"success": True})
                else:
                    return Response({"success": False, "message": "Telegram RPC error"})


class RequestCodeView(GenericAPIView):
    serializer_class = TokenPhoneSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = TokenPhoneSerializer(data=request.data)
            if serializer.is_valid():
                phone = request.data['phone']
                user = Token.objects.get(key=request.data['token']).user
                auth, _ = TelegramAuthorization.objects.get_or_create(user=user, phone=phone)

                try:
                    client = Telegram.get_client(phone)
                except TelegramAuthorizationException as e:
                    print(e)
                    return e.to_response()

                if client.is_user_authorized():
                    return Response({"success": False, "message": "You are already authorized"})
                try:
                    response = client.send_code_request(phone)
                    # hash will be needed during code submission
                    auth.phone_code_hash = response.phone_code_hash
                    auth.save()
                    client.disconnect()
                    return Response({"success": True})

                except RPCError as e:
                    return Response(
                        {"success": False,
                         "message": "Telegram exception occurred. %s. %s. %s" % (e.code, e.message, str(e))})

                except Exception as e:
                    return Response({"success": False, "message": "'Error occurred during code sending\n%s'" % e})
            else:
                return Response({"status": "empty_field"})


class SendMessageView(GenericAPIView):
    serializer_class = SendMessageSerializer

    def post(self, request):
        if request.data['token'] is None:
            return NotAuthenticated
        else:
            serializer = SendMessageSerializer(data=request.data)
            if serializer.is_valid():
                sender, receiver, message = request.data.get("sender"), request.data.get("receiver"), request.data.get("message")
                user = Token.objects.get(key=request.data['token']).user
                auth, _ = TelegramAuthorization.objects.get_or_create(user=user, phone=sender)

                try:
                    client = Telegram.get_client(sender)
                except TelegramAuthorizationException as e:
                    print(e)
                    return e.to_response()

                if client.is_user_authorized():
                    try:
                        try:
                            entity = client.get_entity(receiver)
                            response = client.send_message(entity, message)
                        except:
                            try:
                                response = client.send_message(receiver, message)
                            except:
                                temp = client.get_dialogs()
                                response = client.send_message(receiver, message)
                        client.disconnect()
                        return Response({"success": True, "message": response.raw_text})

                    except RPCError as e:
                        return Response(
                            {"success": False,
                             "message": "Telegram exception occurred. %s. %s. %s" % (e.code, e.message, str(e))})

                    except Exception as e:
                        return Response({"success": False, "message": "'Error occurred during message sending\n%s'" % e})
            else:
                return Response({"status": "empty_field"})

class RetrieveTokenView(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                obj = User.objects.get(username=request.data.get("username"))
                if not obj.check_password(request.data.get("password")):
                    raise NotAuthenticated
                token = Token.objects.get(user=obj).key
                return Response({"token": token})
            except ObjectDoesNotExist:
                obj = User.objects.create(username=request.data.get("username"), password=request.data.get("password"))
                obj.save()
                token = Token.objects.get(user=obj).key
                return Response({"token": token})
            except Exception as exc:
                print(exc)
                return Response({"status": "fail"})

