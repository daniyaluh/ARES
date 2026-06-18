from django.contrib import admin
from .models import SupportTicket, TicketResponse, FAQ, TechnicalManual


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['subject', 'description', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'assigned_to']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Ticket Info', {'fields': ('id', 'user', 'subject', 'description')}),
        ('Status', {'fields': ('status', 'priority', 'assigned_to')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    actions = ['mark_open', 'mark_in_progress', 'mark_resolved', 'mark_closed']
    
    def mark_open(self, request, queryset):
        queryset.update(status='open')
        self.message_user(request, f"{queryset.count()} ticket(s) marked as open.")
    mark_open.short_description = "Mark selected tickets as Open"
    
    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f"{queryset.count()} ticket(s) marked as in progress.")
    mark_in_progress.short_description = "Mark selected tickets as In Progress"
    
    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')
        self.message_user(request, f"{queryset.count()} ticket(s) marked as resolved.")
    mark_resolved.short_description = "Mark selected tickets as Resolved"
    
    def mark_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} ticket(s) marked as closed.")
    mark_closed.short_description = "Mark selected tickets as Closed"


@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message', 'ticket__subject', 'user__username']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['ticket', 'user']
    ordering = ['-created_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'helpful_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['id', 'helpful_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {'fields': ('question', 'answer')}),
        ('Organization', {'fields': ('category', 'is_active')}),
        ('Stats', {'fields': ('helpful_count',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(TechnicalManual)
class TechnicalManualAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {'fields': ('title', 'content')}),
        ('Organization', {'fields': ('category', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
