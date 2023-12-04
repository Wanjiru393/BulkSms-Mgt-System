from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(PasswordResetToken)
admin.site.register(Customer)
admin.site.register(SMSTemplate)
admin.site.register(SMS)


