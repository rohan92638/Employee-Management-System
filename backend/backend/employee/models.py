from django.db import models
from django.conf import settings
from django.utils import timezone
from PIL import Image
import os

def employee_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.first_name}_{instance.last_name}_{instance.id or 'new'}.{ext}"
    return os.path.join('employee_photos', filename)


class Employee(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null= True, blank=True)
    first_name= models.CharField(max_length= 50)
    last_name= models.CharField(max_length= 50)
    email= models.EmailField(unique= True)
    phone= models.CharField(max_length= 15, unique= True, null= True)
    
      # If you created a Department model, uncomment below and import it:
    department= models.ForeignKey('department.Department', on_delete=models.SET_NULL, null= True, blank= True)
    position= models.CharField(max_length= 100, blank= True)
    date_of_joining= models.DateField(default= timezone.now)
    salary= models.DecimalField(max_digits= 10, decimal_places=2, null= True, blank= True)
    employment_type= models.CharField(max_length= 20, choices=(
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('Internship', 'Internship'),
    ), default= 'full_time')
    profile_picture= models.ImageField(upload_to=employee_image_upload_to, null=True, blank=True)
    status= models.BooleanField(default=True) # Active or Inactive
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now= True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    # Resize image to max 512x512 to save space
    if self.profile_picture:
        try:
            img_path= self.profile_picture.path
            img= Image.open(img_path)
            max_size= (512, 512)
            img.thumbnail(max_size)
            img.save(img_path)
        except Exception:
            # if running in environment where file path not available, skip
             pass
         
class Attendance(models.Model):
    ATTENDANCE_STATUS= (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('remote', 'Remote'),
        ('half_day', 'Half Day'),
    )
    
    employee= models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date= models.DateField()
    status= models.CharField(max_length= 20, choices= ATTENDANCE_STATUS, default='present')
    time_in= models.TimeField(null= True, blank= True)
    time_out= models.TimeField(null=True, blank=True)
    notes= models.TextField(blank= True, null= True)
    
    class Meta:
        unique_together= ('employee', 'date')
        ordering= ['-date']
        
    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"
    

class LeaveRequest(models.Model):
    LEAVE_STATUS= (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    employee= models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date= models.DateField()
    end_date= models.DateField()
    reason= models.TextField()
    status= models.CharField(max_length= 20, choices= LEAVE_STATUS, default='pending')
    created_at= models.DateTimeField(auto_now_add=True)
    reviewed_by= models.ForeignKey(settings.AUTH_USER_MODEL, null=True,blank=True, on_delete=models.SET_NULL, related_name='reviewed_leaves')
    reviewed_at= models.DateTimeField(null= True, blank= True)
    
    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date} - ({self.status})"
    
    
class PerformanceRecord(models.Model):
    employee= models.ForeignKey(Employee, on_delete=models.CASCADE, related_name= 'performance_records')
    title= models.CharField(max_length= 100)
    review_date= models.DateField(default= timezone.now)
    score= models.PositiveSmallIntegerField(null= True, blank= True) # e.g. 1-10 scale
    remarks= models.TextField(blank= True, null= True)
    created_at= models.DateTimeField(auto_now_add= True)
    
    class Meta:
        ordering= ['-review_date']
        
    def __str__(self):
        return f"{self.employee} - {self.title} ({self.review_date})"