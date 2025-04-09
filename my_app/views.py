from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from .models import Student, Attendance
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import datetime 
from django.db.models import Count,Q
from .forms import StudentForm
from datetime import datetime as dt,timedelta
from django.utils.timezone import now
from datetime import date
from django.db import models
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request,"index.html")

def stafflogin_view(request):
    return render(request,"stafflogin.html")

@login_required(login_url='login')
def staff_page(request):
    return render(request, 'staffpage.html')

@login_required(login_url='login')
def staff_page(request):
    department = request.GET.get('department')
    year = request.GET.get('year')
    students = None

    if department and year:
        students = Student.objects.filter(department=department, year=year)

    return render(request, 'staffpage.html', {'students': students})
@login_required(login_url='login')
def mark_attendance(request):
    if request.method == "POST":
        department = request.POST.get("department")
        year = request.POST.get("year")
        absent_students_ids = request.POST.getlist("absent_students")  
        today = date.today()

        # Check if attendance has already been marked today
        existing_attendance = Attendance.objects.filter(student__department=department, student__year=year, date=today)
        if existing_attendance.exists():
            messages.error(request, "Attendance has already been marked for today.")
            return redirect("staff_page")

        # Mark selected students as absent
        for student_id in absent_students_ids:
            student = Student.objects.get(id=student_id)
            Attendance.objects.create(student=student, status="absent", date=today)

        # Mark unselected students as present
        present_students = Student.objects.filter(department=department, year=year).exclude(id__in=absent_students_ids)
        for student in present_students:
            Attendance.objects.create(student=student, status="present", date=today)

        messages.success(request, "Attendance marked successfully.")
        return redirect("staff_page")

    return redirect("staff_page")

def add_student(request):
    return render(request,"addstudent.html")

@login_required(login_url='login')
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        
        if form.is_valid():
            form.save()  # Save the new student to the database
            return redirect('add_student')  # Redirect to staff page after adding student
    
    else:
        form = StudentForm()  # Display an empty form for GET requests
    
    return render(request, 'addstudent.html', {'form': form})

@login_required(login_url='login')  # Ensures only staff can access
def remove_student(request):
    """ View to remove a student securely based on department and year """
    department = request.GET.get('department')
    year = request.GET.get('year')
    student_id = request.GET.get('student_id')

    # Fetch students based on department and year
    students = Student.objects.filter(department=department, year=year) if department and year else None

    if request.method == "GET" and student_id:
        student = get_object_or_404(Student, id=student_id)

        # Ensure the student belongs to the selected department and year
        if student.department != department or student.year != year:
            messages.error(request, "Invalid student selection!")
            return redirect("remove_student")

        # Delete student
        student.delete()
        messages.success(request, "Student removed successfully!")
        return redirect("remove_student")

    return render(request, "removestudent.html", {"students": students})
@login_required(login_url='login')
def generate_report(request):
    return render(request,"generatereport.html")


@login_required(login_url='login')
def generate_report(request):
    students = []
    student_id = request.GET.get('student_id')
    department = request.GET.get('department')
    year = request.GET.get('year')
    time_period = request.GET.get('time_period')

    if department and year:
        students = Student.objects.filter(department=department, year=year)

    attendance_data = {'present': 0, 'absent': 0}  # Default values
    attendance_trend = []  # For line chart (date-wise attendance)

    if student_id and time_period:
        try:
            student = Student.objects.get(id=student_id)
            today = timezone.now().date()

            # Determine start date based on time_period
            if time_period == "week":
                start_date = today - timedelta(days=7)
            elif time_period == "month":
                start_date = today - timedelta(days=30)
            elif time_period == "6months":
                start_date = today - timedelta(days=180)
            elif time_period == "year":
                start_date = today - timedelta(days=365)
            else:
                start_date = None

            if start_date:
                attendance_records = Attendance.objects.filter(student=student, date__range=[start_date, today])

                # Count presents and absents
                attendance_data['present'] = attendance_records.filter(status='present').count()
                attendance_data['absent'] = attendance_records.filter(status='absent').count()

                # Get date-wise attendance count
                date_counts = attendance_records.values('date').annotate(
                    present_count=Count('id', filter=models.Q(status='present')),
                    absent_count=Count('id', filter=models.Q(status='absent'))
                ).order_by('date')

                # Convert queryset to list of dictionaries
                attendance_trend = [
                    {
                        "date": record["date"].strftime("%Y-%m-%d"), 
                        "present": record["present_count"], 
                        "absent": record["absent_count"]
                    }
                    for record in date_counts
                ]

        except Student.DoesNotExist:
            pass

    return render(request, 'generatereport.html', {
        'students': students,
        'attendance_data': attendance_data,
        'attendance_trend': json.dumps(attendance_trend),  # Pass as JSON
        'student': student if 'student' in locals() else None,
        'records': attendance_records if 'attendance_records' in locals() else None,
    })

@login_required(login_url='login')
def edit_attendance(request):
    department = request.GET.get('department', '')
    year = request.GET.get('year', '')
    student_id = request.GET.get('student_id', '')
    time_period = request.GET.get('time_period', '')

    students = Student.objects.filter(department=department, year=year) if department and year else None
    attendance_records = None

    if student_id and time_period:
        student = Student.objects.get(id=student_id)
        end_date = dt.today()

        if time_period == "week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "6months":
            start_date = end_date - timedelta(days=180)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = None

        if start_date:
            attendance_records = Attendance.objects.filter(student=student, date__range=[start_date, end_date])

    return render(request, 'editstudent.html', {
        'students': students,
        'attendance_records': attendance_records,
    })

@login_required(login_url='login')
def update_attendance(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith('attendance_status_'):
                record_id = key.replace('attendance_status_', '')
                attendance_record = Attendance.objects.get(id=record_id)
                attendance_record.status = value
                
                # Get corresponding reason field
                reason_key = f"reason_{record_id}"
                reason_value = request.POST.get(reason_key, "").strip()
                attendance_record.reason = reason_value

                attendance_record.save()

        messages.success(request, "Attendance updated successfully!")
        return redirect(reverse('edit_attendance'))

    return redirect(reverse('edit_attendance'))


def studentlogin_view(request):
    return render(request, 'studentlogin.html')

@login_required(login_url='studentlogin')
def stdpage_view(request):
    return render(request, 'studentpage.html')

def stdlogin_view(request):
    if request.method=='POST':
        username =request.POST.get('username')
        password =request.POST.get('password')
        user =authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('studentpage')  # Redirect to the staff page after login
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'studentlogin.html')

def login_view(request):
    if request.method=='POST':
        username =request.POST.get('username')
        password =request.POST.get('password')
        user =authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('staff_page')  # Redirect to the staff page after login
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')
    return render(request, 'stafflogin.html')

def show_students(request):
    department = request.GET.get('department')
    year = request.GET.get('year')

    if not department or not year:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    students = Student.objects.filter(department=department, year=year)

    students_data = []
    for student in students:
        present_count = Attendance.objects.filter(student=student, status='present').count()
        absent_count = Attendance.objects.filter(student=student, status='absent').count()

        students_data.append({
            'student_id': student.id,
            'student_name': student.name,
            'present_count': present_count,
            'absent_count': absent_count,
        })

    return JsonResponse({'success': True, 'students': students_data})