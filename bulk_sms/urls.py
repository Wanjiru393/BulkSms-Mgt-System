from django.urls import path
from .views import *
from bulk_sms import views

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='register'),
    path('login/', UserLogin.as_view(), name='login'),
    path('password-reset/', PasswordReset.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),

    path('manage-user-roles/<int:user_id>/', manage_user_roles, name='manage_user_roles'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('sms-templates/', SMSTemplateListView.as_view(), name='sms_templates_list'),
    path('sms-templates/create/', SMSTemplateCreateView.as_view(), name='sms_templates_create'),
    path('sms-templates/update/<int:pk>/', SMSTemplateUpdateView.as_view(), name='sms_templates_update'),
    path('template/delete/<int:pk>/', SMSTemplateDeleteView.as_view(), name='delete_template'),

    path('sms/create/', SMSCreateView.as_view(), name='sms_create'),
    path('sms/list/', SMSListView.as_view(), name='sms_list'),
    path('sms/edit/<int:pk>/', SMSEditView.as_view(), name='sms_edit'),
    path('sms/delete/<int:pk>/', SMSDeleteView.as_view(), name='sms_delete'),
    path('sms/deleted/', SMSDeletedListView.as_view(), name='sms_deleted_list'),
    path('sms/restore/<int:pk>/', SMSRestoreView.as_view(), name='sms_restore'),

    path('sms/approve/<int:pk>/', SMSApprovalView.as_view(), name='sms-approve'),
    path('sms/approved/', ApprovedSMSView.as_view(), name='sms-approved'),
    path('sms/rejected/', RejectedSMSView.as_view(), name='sms-rejected'),
]