from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# ====================================================================
# I. User & Enrollment Models
# ====================================================================

class InstructorProfile(models.Model):
    """Stores instructor-specific data, including Zoom identifiers."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='instructor_profile'
    )
    bio = models.TextField(blank=True, null=True)
    
    # CRITICAL: Zoom/Meet requires a unique ID for the host
    zoom_host_id = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="The Licensed User Email/ID used for the Zoom API host.",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Instructor: {self.user.email}"
    
    class Meta:
        verbose_name_plural = "Instructor Profiles"


class Enrollment(models.Model):
    """Maps a student to a course they are enrolled in."""
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='enrollments'
    )
    course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE, 
        related_name='course_enrollments'
    )
    enrollment_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name_plural = "Enrollments"

# ====================================================================
# II. Core Content & Structure Models
# ====================================================================

class Course(models.Model):
    """The main curriculum entity."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, # Protect courses from deletion if instructor account is deleted
        related_name='taught_courses',
        # Filter for users that are instructors if you have a custom User model
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Module(models.Model):
    """Sections within a course."""
    title = models.CharField(max_length=255)
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='modules'
    )
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """The fundamental unit of content (which may be a live class)."""
    
    CONTENT_TYPES = [
        ('VIDEO', 'Video Lecture'),
        ('TEXT', 'Text/Reading Material'),
        ('LIVE', 'Live Class Session'), # This type will require a ScheduledSession
    ]
    
    title = models.CharField(max_length=255)
    module = models.ForeignKey(
        Module, 
        on_delete=models.CASCADE, 
        related_name='lessons'
    )
    content_type = models.CharField(
        max_length=10, 
        choices=CONTENT_TYPES, 
        default='TEXT'
    )
    content_url = models.URLField(max_length=2048, blank=True, null=True) # Used for stored videos/files
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        unique_together = ('module', 'order')

    def __str__(self):
        return self.title

# ====================================================================
# III. Scheduling & Live Integration Models
# ====================================================================

class ScheduledSession(models.Model):
    """
    Defines the specific time a LIVE lesson will occur. 
    This is the model that triggers the Zoom/Meet API call.
    """
    PLATFORM_CHOICES = [
        ('ZOOM', 'Zoom Meeting'),
        ('MEET', 'Google Meet'),
    ]

    lesson = models.OneToOneField(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='scheduled_session'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    platform = models.CharField(
        max_length=10, 
        choices=PLATFORM_CHOICES, 
        default='ZOOM'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Live Session for {self.lesson.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['start_time']


class ZoomMeeting(models.Model):
    """
    Stores essential data returned by the Zoom API after successful creation.
    """
    session = models.OneToOneField(
        ScheduledSession, 
        on_delete=models.CASCADE, 
        related_name='zoom_meeting',
        primary_key=True,
    )

    # Zoom API Identifiers and Links
    zoom_id = models.CharField(
        max_length=20, 
        unique=True, 
        db_index=True,
        help_text="The unique numeric ID returned by the Zoom API."
    )
    topic = models.CharField(max_length=255)
    join_url = models.URLField(max_length=2048) # Student URL
    start_url = models.URLField(max_length=2048) # Instructor Host URL
    host_id = models.CharField(max_length=100) # Copy of the host's Zoom ID/Email

    # Status tracking for recordings
    RECORDING_STATUS_CHOICES = [
        ('PENDING', 'Pending Processing'),
        ('READY', 'Ready for View'),
        ('NONE', 'No Recording Available'),
    ]
    
    recording_status = models.CharField(
        max_length=10,
        choices=RECORDING_STATUS_CHOICES,
        default='NONE',
    )
    recording_link = models.URLField(max_length=2048, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zoom: {self.topic} for Session {self.session_id}"
    
    class Meta:
        verbose_name_plural = "Zoom Meetings"


# ====================================================================
# IV. Post-Session Artifacts Models
# ====================================================================

class AttendanceRecord(models.Model):
    """Stores data pulled from Zoom Reporting API for student attendance."""
    session = models.ForeignKey(
        ScheduledSession, 
        on_delete=models.CASCADE, 
        related_name='attendance_records'
    )
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='attended_sessions'
    )
    join_time = models.DateTimeField()
    leave_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(
        help_text="Total duration student was present in minutes."
    )

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['join_time']

    def __str__(self):
        return f"{self.student.email} attended {self.session.lesson.title}"

# Note: The Recording model is merged into ZoomMeeting for simplicity in this structure.