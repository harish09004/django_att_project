from django.db import models

class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('cs', 'Computer Science'),
        ('it', 'Information Technology'),
        ('bca', 'Bachelor of Computer Applications'),
    ]

    YEAR_CHOICES = [
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
    ]

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=3, choices=DEPARTMENT_CHOICES)
    year = models.CharField(max_length=3, choices=YEAR_CHOICES)
    roll_number = models.CharField(max_length=15, unique=True, null=True)

    def __str__(self):
        return f"{self.roll_number} - {self.name}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateField()
    reason = models.TextField(blank=True, null=True)  # New Field
    remarks = models.TextField(blank=True, null=True)  # New Field

    def __str__(self):
        return f"{self.student.name} - {self.status} on {self.date}"
