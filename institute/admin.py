from django.contrib import admin

# Register your models here.
from institute.models import Institute, TeacherRequest, Subject, SubjectAccess

admin.site.register([Institute,
                    TeacherRequest, Subject, SubjectAccess])
