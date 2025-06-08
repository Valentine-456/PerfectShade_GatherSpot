from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, Interest, Review, OrganizationProxy, IndividualUserProxy
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
import csv
from io import TextIOWrapper
from django.utils.html import format_html
from django.urls import reverse

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'user_type', 'is_email_verified','is_org_verified', 'is_staff')
    list_filter = ('user_type', 'is_email_verified', 'is_org_verified')
    search_fields = ('username', 'email', 'organization_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Verification Info', {'fields': ('user_type', 'is_email_verified', 'is_org_verified')}),
        ('Organization Info', {'fields': ('organization_name', 'verification_document')}),
        ('Connections', {'fields': ('friends','interests')}),
        ('Event Attendance', {'fields': ('attending_events_display',)}),
    )
    filter_horizontal = ('friends', 'interests')  # Makes interests (and friends) multi-select UI nicer
    readonly_fields = ('attending_events_display',)

    def attending_events_display(self, obj):
        events = obj.attending_events.all()
        if not events:
            return "No events"

        links = []
        for event in events:
            url = reverse('admin:PerfectSpot_event_change', args=[event.id])  
            links.append(f'<a href="{url}">{event.title}</a>')

        return format_html('<br>'.join(links))  
    attending_events_display.short_description = "Attending Events"

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date', 'location', 'is_promoted')
    list_filter = ('is_promoted', 'date')
    search_fields = ('title', 'location', 'creator__username')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='event_import_csv'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.DictReader(csv_file)

                expected_columns = ['title', 'description', 'location', 'date', 'creator', 'is_promoted']
                missing_columns = [col for col in expected_columns if col not in reader.fieldnames]

                if missing_columns:
                    messages.error(request, f"Missing columns: {', '.join(missing_columns)}")
                    return redirect("..")
                
                success_count = 0
                
                for row in reader:
                    try:
                        creator = CustomUser.objects.get(username=row['creator'])
                    except CustomUser.DoesNotExist:
                        messages.error(request, f"Error on row {reader.line_num}: User '{row['creator']}' does not exist.")
                        continue
                        
                    try:
                        from datetime import datetime
                        parsed_date = datetime.strptime(row['date'], "%Y-%m-%d %H:%M")

                        is_promoted = row.get('is_promoted', '').strip().lower() in ['true', '1']
                        
                        Event.objects.create(
                            title=row['title'],
                            description=row['description'],
                            location=row['location'],
                            date=parsed_date,  # YYYY-MM-DD HH:MM
                            creator=creator,  # Must be an existing user
                            is_promoted=is_promoted
                        )
                        success_count += 1

                    except ValueError as ve:
                        messages.error(request, f"Row {reader.line_num}: Date or value error – {ve}")
                        continue
                    except KeyError as ke:
                        messages.error(request, f"Row {reader.line_num}: Missing required field – {ke}")
                        continue
                    except Exception as e:
                        messages.error(request, f"Row {reader.line_num}: Unexpected error – {e}")
                        continue
                    
                self.message_user(request, f"Successfully imported {success_count} events.")
                return redirect("..")
        else:
            form = CsvImportForm()

        context = {
            "form": form,
            "opts": self.model._meta,
            "title": "Import Events from CSV"
        }
        return render(request, "admin/csv_form.html", context)

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['upload_link'] = reverse('admin:event_import_csv')
        return super().changelist_view(request, extra_context=extra_context)

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
        return False  

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name']
# csv import class
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()