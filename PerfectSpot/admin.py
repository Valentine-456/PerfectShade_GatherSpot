from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, Review, OrganizationProxy, IndividualUserProxy

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_email_verified','is_org_verified', 'is_staff')
    list_filter = ('user_type', 'is_email_verified', 'is_org_verified')
    search_fields = ('username', 'email', 'organization_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Verification Info', {'fields': ('user_type', 'is_email_verified', 'is_org_verified')}),
        ('Organization Info', {'fields': ('organization_name', 'verification_document')}),
        ('Connections', {'fields': ('friends',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date', 'location', 'is_promoted')
    list_filter = ('is_promoted', 'date')
    search_fields = ('title', 'location', 'creator__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'event__title')

class OrganizationAdmin(UserAdmin):
    model = OrganizationProxy
    list_display = ('username', 'email', 'organization_name', 'is_email_verified', 'is_org_verified', 'is_active', 'is_staff')
    list_filter = ('is_org_verified', 'is_email_verified')
    search_fields = ('username', 'email', 'organization_name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user_type='organization')

    def has_add_permission(self, request):
        return False  

admin.site.register(OrganizationProxy, OrganizationAdmin)

@admin.register(IndividualUserProxy)
class IndividualUserAdmin(UserAdmin):
    model = IndividualUserProxy
    list_display = ('username', 'email', 'is_email_verified', 'is_active', 'is_staff')
    list_filter = ('is_email_verified',)
    search_fields = ('username', 'email')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(user_type='individual')

    def has_add_permission(self, request):
        return False  # Signup happens via frontend only
