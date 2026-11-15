from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from .models import Category,Product,Banner,ShopSettings,Order,OrderItem,Payment,AuditLog,Favorite
admin.site.unregister(Group)
admin.site.unregister(User)
class OwnerOnlyAdmin(admin.ModelAdmin):
 def has_module_permission(self,request):return bool(request.user.is_authenticated and request.user.is_superuser)
 def has_view_permission(self,request,obj=None):return request.user.is_superuser
 def has_add_permission(self,request):return request.user.is_superuser
 def has_change_permission(self,request,obj=None):return request.user.is_superuser
 def has_delete_permission(self,request,obj=None):return request.user.is_superuser
 def save_model(self,request,obj,form,change):
  super().save_model(request,obj,form,change)
  AuditLog.objects.create(actor=request.user,action=('update' if change else 'create')+' '+obj._meta.label,details={'id':str(obj.pk)})
 def delete_model(self,request,obj):
  AuditLog.objects.create(actor=request.user,action='delete '+obj._meta.label,details={'id':str(obj.pk)})
  super().delete_model(request,obj)
@admin.register(Category)
class CategoryAdmin(OwnerOnlyAdmin):list_display=('name','slug');prepopulated_fields={'slug':('name',)}
@admin.register(Product)
class ProductAdmin(OwnerOnlyAdmin):list_display=('name','price','sale_price','stock','active');list_filter=('active','category');search_fields=('name',);prepopulated_fields={'slug':('name',)}
@admin.register(Banner)
class BannerAdmin(OwnerOnlyAdmin):list_display=('title','active')
@admin.register(ShopSettings)
class ShopSettingsAdmin(OwnerOnlyAdmin):
 def has_add_permission(self,request):return request.user.is_superuser and not ShopSettings.objects.exists()
class ItemInline(admin.TabularInline):model=OrderItem;extra=0;readonly_fields=('product','name','unit_price','quantity');can_delete=False
@admin.register(Order)
class OrderAdmin(OwnerOnlyAdmin):
 list_display=('id','user','status','total','created_at');list_filter=('status',);inlines=[ItemInline];readonly_fields=('user','status','total','created_at','updated_at','expires_at')
 def has_add_permission(self,request):return False
 def has_delete_permission(self,request,obj=None):return False
@admin.register(Payment)
class PaymentAdmin(OwnerOnlyAdmin):
 list_display=('provider_id','order','status','amount','updated_at');readonly_fields=('order','provider_id','status','qr_code','qr_base64','amount','updated_at')
 def has_add_permission(self,request):return False
 def has_delete_permission(self,request,obj=None):return False
@admin.register(AuditLog)
class AuditAdmin(OwnerOnlyAdmin):
 list_display=('actor','action','created_at');readonly_fields=('actor','action','details','created_at')
 def has_add_permission(self,request):return False
 def has_delete_permission(self,request,obj=None):return False
class RestrictedUserAdmin(UserAdmin):
 def has_module_permission(self,request):return request.user.is_superuser
 def has_view_permission(self,request,obj=None):return request.user.is_superuser
 def has_add_permission(self,request):return False
 def has_change_permission(self,request,obj=None):return request.user.is_superuser
 def has_delete_permission(self,request,obj=None):return False
 def get_readonly_fields(self,request,obj=None):
  return ('is_staff','is_superuser','groups','user_permissions')
admin.site.register(User,RestrictedUserAdmin)
from . import admin_dashboard

@admin.register(Favorite)
class FavoriteAdmin(OwnerOnlyAdmin):
 list_display=('user','product','created_at')
 list_select_related=('user','product')
 readonly_fields=('user','product','created_at')
 def has_add_permission(self,request):return False
 def has_change_permission(self,request,obj=None):return False
 def has_delete_permission(self,request,obj=None):return False
