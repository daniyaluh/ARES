"""
URL patterns for Verification app.
Expanded to include comprehensive verification management.
"""
from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    # Robot/Product Views with Verification Checks
    path('robots/', views.RobotListView.as_view(), name='robot-list'),
    path('robots/<uuid:robot_id>/', views.RobotDetailView.as_view(), name='robot-detail'),
    path('military-robots/', views.MilitaryRobotsListView.as_view(), name='military-robots-list'),
    path('military-robots/<uuid:robot_id>/', views.RobotDetailView.as_view(), name='military-robot-detail'),
    
    # Verification Requests
    path('request/', views.verification_request_create, name='request'),
    path('request/<uuid:request_id>/', views.verification_request_detail, name='request-detail'),
    path('request/<uuid:request_id>/edit/', views.verification_request_update, name='request-edit'),
    path('request/<uuid:request_id>/cancel/', views.verification_request_cancel, name='request-cancel'),
    path('request/<uuid:request_id>/withdraw/', views.verification_request_withdraw, name='request-withdraw'),
    path('requests/', views.verification_request_list, name='request-list'),
    path('requests/my/', views.verification_request_my_list, name='request-my-list'),
    
    # Identity Documents
    path('request/<uuid:request_id>/documents/', views.identity_document_list, name='identity-document-list'),
    path('request/<uuid:request_id>/documents/add/', views.identity_document_create, name='identity-document-create'),
    path('documents/<uuid:document_id>/', views.identity_document_detail, name='identity-document-detail'),
    path('documents/<uuid:document_id>/edit/', views.identity_document_update, name='identity-document-edit'),
    path('documents/<uuid:document_id>/delete/', views.identity_document_delete, name='identity-document-delete'),
    
    # Certifications
    path('request/<uuid:request_id>/certifications/', views.certification_list, name='certification-list'),
    path('request/<uuid:request_id>/certifications/add/', views.certification_create, name='certification-create'),
    path('certifications/<uuid:cert_id>/', views.certification_detail, name='certification-detail'),
    path('certifications/<uuid:cert_id>/edit/', views.certification_update, name='certification-edit'),
    path('certifications/<uuid:cert_id>/delete/', views.certification_delete, name='certification-delete'),
    
    # Military Affiliation
    path('request/<uuid:request_id>/military/', views.military_affiliation_detail, name='military-affiliation-detail'),
    path('request/<uuid:request_id>/military/edit/', views.military_affiliation_update, name='military-affiliation-edit'),
    
    # Clearance Levels
    path('clearance-levels/', views.clearance_level_list, name='clearance-level-list'),
    path('clearance-levels/<uuid:level_id>/', views.clearance_level_detail, name='clearance-level-detail'),
    
    # My Clearance Status
    path('my-clearance/', views.my_clearance_status, name='my-clearance'),
    path('my-clearance/renew/', views.clearance_renew, name='clearance-renew'),
    
    # Admin/Review Views (staff only)
    path('review/', views.verification_review_list, name='review-list'),
    path('review/<uuid:request_id>/', views.verification_review_detail, name='review-detail'),
    path('review/<uuid:request_id>/approve/', views.verification_review_approve, name='review-approve'),
    path('review/<uuid:request_id>/reject/', views.verification_review_reject, name='review-reject'),
    path('review/<uuid:request_id>/assign-clearance/', views.verification_review_assign_clearance, name='review-assign-clearance'),
    
    # Verification Logs
    path('logs/', views.verification_log_list, name='verification-log-list'),
    path('logs/<uuid:log_id>/', views.verification_log_detail, name='verification-log-detail'),
    path('request/<uuid:request_id>/logs/', views.verification_request_logs, name='verification-request-logs'),
    
    # Export Licenses
    path('licenses/', views.export_license_list, name='license-list'),
    path('licenses/apply/', views.export_license_apply, name='license-apply'),
    path('licenses/<uuid:license_id>/', views.export_license_detail, name='license-detail'),
    path('licenses/<uuid:license_id>/edit/', views.export_license_update, name='license-edit'),
    path('licenses/<uuid:license_id>/submit/', views.export_license_submit, name='license-submit'),
    path('licenses/<uuid:license_id>/withdraw/', views.export_license_withdraw, name='license-withdraw'),
    
    # Staff License Management
    path('staff/pending-licenses/', views.staff_pending_licenses, name='staff-pending-licenses'),
    path('staff/review-license/<uuid:license_id>/', views.staff_review_license, name='staff-review-license'),
]
