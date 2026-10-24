from django.contrib import admin
from .models import Order, OrderProduct, Payment

class OrderProductInline(admin.TabularInline):
  model = OrderProduct
  extra = 0
  readonly_fields = ['user', 'payment', 'product', 'quantity', 'product_price', 'ordered']
class OrderAdmin(admin.ModelAdmin):
  list_display = [ 'order_number', 'full_name', 'email', 'phone', 'order_total', 'pin_code', 'city', 'status', 'is_ordered', 'created_at']
  list_filter = ['status', 'is_ordered']
  search_fields = ['first_name', 'last_name', 'order_number']
  list_per_page = 20
  readonly_fields = ['created_at', 'order_number', 'updated_at']
  inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
