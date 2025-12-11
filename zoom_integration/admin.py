from django.contrib import admin
from .models import User, InstructorProfile, Enrollment, Course, Module, Lesson, ScheduledSession, ZoomMeeting, AttendanceRecord
# Register your models here.

# admin.site.register(User)
admin.site.register(InstructorProfile)
admin.site.register(Enrollment)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(ScheduledSession)
admin.site.register(ZoomMeeting)
admin.site.register(AttendanceRecord)