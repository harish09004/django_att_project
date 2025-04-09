from django.urls import path,include
from .import views 
from django.contrib.auth import views as auth_views 
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('/') 

urlpatterns= [
    path('stafflogin/', views.stafflogin_view, name='stafflogin'),
    path('login/', views.login_view, name='login'),
    #path('get_students/<str:department>/<str:year>/', views.get_students, name='get_students'),
    #path('update_attendance/', views.update_attendance, name='update_attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('show_students/', views.show_students, name='show_students'),
    path('studentlogin/', views.studentlogin_view, name='studentlogin'),
    path('std_login/',views.stdlogin_view,name='std_login'),
    path('studentpage/',views.stdpage_view,name='studentpage'),
    path('remove_student/', views.remove_student, name='remove_student'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('staff_page/', views.staff_page, name='staff_page'),
    path('add_student/', views.add_student, name='add_student'),
    path('logout/', custom_logout, name='logout'),
    path('edit_attendance/', views.edit_attendance, name='edit_attendance'),
    path('update_attendance/', views.update_attendance, name='update_attendance'),
]

