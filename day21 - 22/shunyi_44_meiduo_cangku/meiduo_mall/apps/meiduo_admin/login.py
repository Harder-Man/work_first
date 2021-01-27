from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwr_encode_handler = api_settings.JWT_ENCODE_HANDLER


class AdminJSONWebTokenSerializer(JSONWebTokenSerializer):

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('user account is disabled.')
                    raise serializers.ValidationError(msg)

                # 自定义 加入用户权限限制
                if not user.is_staff:
                    msg = _('普通用户不可以')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_payload_handler(payload),
                    'user': user
                }
            else:
                msg = _('unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

from rest_framework_jwt.views import JSONWebTokenAPIView
class AdminJSONWebTokenAPIView(JSONWebTokenAPIView):

    serializer_class = AdminJSONWebTokenSerializer

admin_obtain_token = AdminJSONWebTokenAPIView.as_view()

