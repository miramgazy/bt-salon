from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/user_updates/(?P<user_id>\d+)/$', consumers.UserUpdateConsumer.as_asgi()),
]
