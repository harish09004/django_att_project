from django.contrib import admin
from .models import Student, Attendance

# Register your models here.


class StudentAdmin(admin.ModelAdmin):
    list_display= ('name', 'department', 'year')  # Columns displayed in the list view
    search_fields= ('name', 'department')  # Search by name or department
    list_filter= ('department', 'year')

admin.site.register(Student, StudentAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display= ('student', 'date', 'status')  # Columns displayed in the list view
    list_filter= ('status',) # Add filter for attendance status (Present/Absent)

# Register the customized Attendance model
admin.site.register(Attendance,AttendanceAdmin)    
