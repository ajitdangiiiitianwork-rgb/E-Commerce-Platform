from django.contrib import admin
from .models import Account


class AccountAdmin(admin.ModelAdmin):
  list_display = ('email', 'first_name', 'last_name', 'last_login', 'created_at', 'is_active')
  list_display_links = ('email', 'first_name')
  readonly_fields =  ('created_at', 'last_login', 'password')
  ordering = ['-created_at']

  filter_horizontal = ()
  list_filter = ()
  fieldsets = ()

admin.site.register(Account, AccountAdmin)
