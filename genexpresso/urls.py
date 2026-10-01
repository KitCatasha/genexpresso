from django.urls import path
from . import views

app_name = 'genexpresso'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project, name='project'),
    path('new_project/', views.new_project, name='new_project'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('new_dataset/<int:project_id>/', views.new_dataset, name='new_dataset'),
    path('edit_dataset/<int:dataset_id>/', views.edit_dataset, name='edit_dataset'),
    path('delete_dataset/<int:dataset_id>/', views.delete_dataset, name='delete_dataset'),
    path('analyze_dataset/<int:dataset_id>/', views.analyze_dataset, name='analyze_dataset'),
    path('logout_page/', views.logout_page, name='logout_page'),
    path('help/', views.help_page, name='help_page'),
    path('loading_page/<int:dataset_id>/', views.loading_page, name='loading_page'),
    path('check_status/<int:dataset_id>/', views.check_status, name='check_status'),
    path('analyze_dataset_results/<int:dataset_id>/', views.analyze_dataset_results, name='analyze_dataset_results'),
    path('export_processed_data/<int:dataset_id>/', views.export_processed_data, name='export_processed_data'),
]