from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
        # Application Details
    path('app/<int:app_id>/', views.app_details, name='app_details'),

    # Add Review for a specific app
    path('app/<int:app_id>/review/', views.add_review, name='add_review'),
        path('feedback/', views.add_feedback, name='add_feedback'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
