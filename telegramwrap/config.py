from django.utils.translation import ugettext_lazy as _
from livesettings.functions import config_register
from livesettings.values import StringValue, ConfigurationGroup


SETTINGS_GROUP = ConfigurationGroup('Telegram API', _('Telegram API Settings'), ordering=0)

config_register(StringValue(
    SETTINGS_GROUP,
    'TG_API_ID',
    description=_("Telegram API ID"),
    help_text=_("api_id value retrieved from my.telegram.org"),
))

config_register(StringValue(
    SETTINGS_GROUP,
    'TG_API_HASH',
    description=_("Telegram API Hash"),
    help_text=_("api_hash value retrieved from my.telegram.org"),
))
