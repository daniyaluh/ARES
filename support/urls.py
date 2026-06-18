"""
URL patterns for Support app.
Comprehensive support ticket management and resources.
"""
from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Support Tickets
    path('tickets/', views.support_ticket_list, name='support-ticket-list'),
    path('tickets/my/', views.support_ticket_my_list, name='support-ticket-my-list'),
    path('tickets/create/', views.support_ticket_create, name='support-ticket-create'),
    path('tickets/<uuid:ticket_id>/', views.support_ticket_detail, name='support-ticket-detail'),
    path('tickets/<uuid:ticket_id>/edit/', views.support_ticket_update, name='support-ticket-edit'),
    path('tickets/<uuid:ticket_id>/close/', views.support_ticket_close, name='support-ticket-close'),
    path('tickets/<uuid:ticket_id>/reopen/', views.support_ticket_reopen, name='support-ticket-reopen'),
    path('tickets/<uuid:ticket_id>/assign/', views.support_ticket_assign, name='support-ticket-assign'),
    
    # Ticket Responses
    path('tickets/<uuid:ticket_id>/responses/', views.ticket_response_list, name='ticket-response-list'),
    path('tickets/<uuid:ticket_id>/responses/create/', views.ticket_response_create, name='ticket-response-create'),
    path('responses/<uuid:response_id>/', views.ticket_response_detail, name='ticket-response-detail'),
    path('responses/<uuid:response_id>/edit/', views.ticket_response_update, name='ticket-response-edit'),
    path('responses/<uuid:response_id>/delete/', views.ticket_response_delete, name='ticket-response-delete'),
    
    # Ticket Filtering
    path('tickets/filter/', views.support_ticket_filter, name='support-ticket-filter'),
    path('tickets/by-status/<str:status>/', views.support_ticket_by_status, name='support-ticket-by-status'),
    path('tickets/by-priority/<str:priority>/', views.support_ticket_by_priority, name='support-ticket-by-priority'),
    path('tickets/search/', views.support_ticket_search, name='support-ticket-search'),
    
    # Technical Manuals
    path('manuals/', views.technical_manual_list, name='technical-manual-list'),
    path('manuals/<uuid:manual_id>/', views.technical_manual_detail, name='technical-manual-detail'),
    path('manuals/<uuid:manual_id>/download/', views.technical_manual_download, name='technical-manual-download'),
    path('manuals/create/', views.technical_manual_create, name='technical-manual-create'),
    path('manuals/<uuid:manual_id>/edit/', views.technical_manual_update, name='technical-manual-edit'),
    path('manuals/<uuid:manual_id>/delete/', views.technical_manual_delete, name='technical-manual-delete'),
    path('manuals/by-category/<uuid:category_id>/', views.technical_manual_by_category, name='technical-manual-by-category'),
    
    # FAQs
    path('faqs/', views.faq_list, name='faq-list'),
    path('faqs/<uuid:faq_id>/', views.faq_detail, name='faq-detail'),
    path('faqs/create/', views.faq_create, name='faq-create'),
    path('faqs/<uuid:faq_id>/edit/', views.faq_update, name='faq-edit'),
    path('faqs/<uuid:faq_id>/delete/', views.faq_delete, name='faq-delete'),
    path('faqs/by-category/<uuid:category_id>/', views.faq_by_category, name='faq-by-category'),
    path('faqs/search/', views.faq_search, name='faq-search'),
    path('faqs/<uuid:faq_id>/helpful/', views.faq_helpful, name='faq-helpful'),
    
    # Support Analytics (staff)
    path('analytics/', views.support_analytics, name='support-analytics'),
    path('analytics/tickets/', views.support_ticket_analytics, name='support-ticket-analytics'),
    path('analytics/response-time/', views.support_response_time_analytics, name='support-response-time-analytics'),
]









