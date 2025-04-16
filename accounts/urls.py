from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Account Creation
    #path('create/',views.CreateAccountView.as_view(), name='create_account'),
    path('dashboard/',views.personal_dashboard, name='personal_dashboard'),
    path('create/', views.create_account, name='create_account'),
    #path('accounts/', views.list_generic, name='account_list'),
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_update'),
    path('accounts/<int:pk>/delete/', views.AccountDeleteView.as_view(), name='account_delete'),

    # Residential Capture
    path('residential_dashboard/',views.residential_dashboard, name='residential_dashboard'),
    path('residential/', views.create_residential, name='create_residential'),
    path('residential_list/', views.residential_list, name='residential_list'),
    path('residential/<int:pk>/', views.residential_detail, name='residential_detail'),
    path('residential/<int:pk>/edit/', views.ResidentialUpdateView.as_view(), name='residential_update'),
    path('residential/<int:pk>/delete/', views.ResidentialDeleteView.as_view(), name='residential_delete'),
    path('residential-analytics/', views.residential_analytics, name='residential_analytics'),
    # Education Capture
    path('create_education/', views.create_education, name='create_education'),  # Replace with the correct function
    path('education_list/', views.education_list, name='education_list'),
    path('education/<int:pk>/', views.education_detail, name='education_detail'),
    path('education/<int:pk>/edit/', views.EducationUpdateView.as_view(), name='education_update'),
    path('education/<int:pk>/delete/', views.EducationDeleteView.as_view(), name='education_delete'),
    path('education/success/', views.success_view, name='education_success'),

    # Search
    path('search/', views.search_view, name='search'),
    
    # Ghana Card Entry
    path('enter-ghana-card/', views.enter_ghana_card, name='enter_ghana_card'),
    path('fetch-ghana-card/', views.fetch_ghana_card, name='fetch_ghana'),


    # Paynow
    #Apath('paynow/', views.paynow, name='paynow'),
    #path('paynow/', views.enter_ghana_card, name='paynow'),
    #path('fetch-ghana-card/', views.fetch_ghana_card, name='fetch_ghana'),
    #Apath('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    # Health Capture
    path('health/', views.create_health, name='create_health'),
    path('health_list/', views.health_list, name='health_list'),
    path('health/<int:pk>/', views.health_detail, name='health_detail'),
    path('health/<int:pk>/edit/', views.HealthUpdateView.as_view(), name='health_update'),
    path('health/<int:pk>/delete/', views.HealthDeleteView.as_view(), name='health_delete'),
    path('health/success/', views.success_view, name='health_success'),
   
    # Government Capture
    path('government/', views.create_government, name='create_government'),
    path('government_list/', views.government_list, name='government_list'),
    path('government/<int:pk>/', views.government_detail, name='government_detail'),
    path('government/<int:pk>/edit/', views.GovernmentUpdateView.as_view(), name='government_update'),
    path('government/<int:pk>/delete/', views.GovernmentDeleteView.as_view(), name='government_delete'),
    path('government/success/', views.success_view, name='government_success'),

    # Business/SME Capture
    path('sme/', views.create_sme, name='create_sme'),
    path('sme_list/', views.sme_list, name='sme_list'),
    path('sme/<int:pk>/', views.sme_detail, name='sme_detail'),
    path('sme/<int:pk>/edit/', views.SMEUpdateView.as_view(), name='sme_update'),
    path('sme/<int:pk>/delete/', views.SMEDeleteView.as_view(), name='sme_delete'),
    path('sme/success/', views.success_view, name='sme_success'),
    
    # Authentication
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    #path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Additional Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('success/', views.contact_success, name='contact_success'),  # Add this line
    path("access_denied/", views.access_denied, name="access_denied"),



]