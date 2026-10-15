from django.contrib import admin
from .models import Product, Variation

class ProductAdmin(admin.ModelAdmin):
  list_display = ('product_name', 'slug', 'price', 'stock', 'is_available', 'category' ,'created_date', 'modified_date')
  list_display_links = ('product_name', 'slug')
  readonly_fields = ('created_date', 'modified_date')
  prepopulated_fields = {'slug' : ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
  list_display = ('product', 'variation_category', 'variation_values', 'is_active', 'created_date')
  readonly_fields = ('created_date',)
  list_editable = ('is_active',)
  list_filter = ('product', 'variation_category', 'variation_values', 'is_active', 'created_date')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)