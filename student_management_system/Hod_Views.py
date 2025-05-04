from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from app.models import Course, Session_Year, CustomUser, Student, Staff, Subject, Staff_Notification, Staff_leave, Staff_Feedback, Student_Notification, Student_Feedback, Student_leave, Attendance, Attendance_Report, Parent
from django.contrib import messages
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='/')
def HOME(request):
    student_count = Student.objects.all().count()
    staff_count = Staff.objects.all().count()
    course_count = Course.objects.all().count()
    subject_count = Subject.objects.all().count()
    parent_count = Parent.objects.all().count()
    student_gender_male = Student.objects.filter(gender='Male').count()
    student_gender_female = Student.objects.filter(gender='Female').count()
    pending_staff_leaves = Staff_leave.objects.filter(status=0).count()
    pending_student_leaves = Student_leave.objects.filter(status=0).count()
    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'course_count': course_count,
        'subject_count': subject_count,
        'parent_count': parent_count,
        'student_gender_male': student_gender_male,
        'student_gender_female': student_gender_female,
        'pending_staff_leaves': pending_staff_leaves,
        'pending_student_leaves': pending_student_leaves,
    }
    return render(request, 'Hod/home.html', context)

@login_required(login_url='/')
def ADD_STUDENT(request):
    course = Course.objects.all()
    session_year = Session_Year.objects.all()
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        full_name = request.POST.get('full_name')
        enrollment_no = request.POST.get('enrollment_no')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course_id')
        session_year_id = request.POST.get('session_year_id')
        semester = request.POST.get('semester')

        # Validate uniqueness
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken')
            return redirect('add_student')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken')
            return redirect('add_student')
        if Student.objects.filter(enrollment_no=enrollment_no).exists():
            messages.warning(request, 'Enrollment Number Is Already Taken')
            return redirect('add_student')

        try:
            # Create CustomUser
            user = CustomUser(
                first_name=full_name,
                last_name='',
                username=username,
                email=email,
                user_type=3
            )
            if profile_pic:
                logger.info(f"Processing profile_pic upload for user: {username}")
                user.profile_pic = profile_pic  # Cloudinary storage handles this
            user.set_password(password)
            user.save()
            logger.info(f"CustomUser {username} saved successfully")

            # Create Student
            course = Course.objects.get(id=course_id)
            session_year = Session_Year.objects.get(id=session_year_id)
            student = Student(
                admin=user,
                address=address,
                session_year_id=session_year,
                course_id=course,
                gender=gender,
                enrollment_no=enrollment_no,
                semester=semester if semester else None
            )
            student.save()
            logger.info(f"Student {enrollment_no} saved successfully")

            messages.success(request, f"{user.first_name} Successfully Added!")
            return redirect('add_student')
        except Exception as e:
            logger.error(f"Error adding student: {str(e)}")
            messages.error(request, f"Error adding student: {str(e)}")
            return redirect('add_student')

    context = {
        'course': course,
        'session_year': session_year,
    }
    return render(request, 'Hod/add_student.html', context)

@login_required(login_url='/')
def VIEW_STUDENT(request):
    student = Student.objects.all()
    context = {
        'student': student,
    }
    return render(request, 'Hod/view_student.html', context)

@login_required(login_url='/')
def EDIT_STUDENT(request, id):
    student = Student.objects.get(id=id)
    course = Course.objects.all()
    session_year = Session_Year.objects.all()
    context = {
        'student': student,
        'course': course,
        'session_year': session_year,
    }
    return render(request, 'Hod/edit_student.html', context)

@login_required(login_url='/')
def UPDATE_STUDENT(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        profile_pic = request.FILES.get('profile_pic')
        full_name = request.POST.get('full_name')
        enrollment_no = request.POST.get('enrollment_no')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course_id')
        session_year_id = request.POST.get('session_year_id')
        semester = request.POST.get('semester')
        
        try:
            user = CustomUser.objects.get(id=student_id)
            user.first_name = full_name
            user.last_name = ''
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                logger.info(f"Updating profile_pic for user: {username}")
                user.profile_pic = profile_pic
            user.save()
            logger.info(f"CustomUser {username} updated successfully")
            
            student = Student.objects.get(admin=student_id)
            if enrollment_no != student.enrollment_no and Student.objects.filter(enrollment_no=enrollment_no).exists():
                messages.warning(request, 'Enrollment Number Is Already Taken')
                return redirect('edit_student', id=student.id)
            
            student.address = address
            student.gender = gender
            student.enrollment_no = enrollment_no
            course = Course.objects.get(id=course_id)
            student.course_id = course
            session_year = Session_Year.objects.get(id=session_year_id)
            student.session_year_id = session_year
            student.semester = int(semester) if semester else None
            student.save()
            logger.info(f"Student {enrollment_no} updated successfully")
            
            messages.success(request, 'Record Successfully Updated!')
            return redirect('view_student')
        except Exception as e:
            logger.error(f"Error updating student: {str(e)}")
            messages.error(request, f"Error updating student: {str(e)}")
            return redirect('view_student')
    return render(request, 'Hod/edit_student.html')

@login_required(login_url='/')
def DELETE_STUDENT(request, admin):
    try:
        student = CustomUser.objects.get(id=admin)
        student.delete()
        messages.success(request, 'Record Successfully Deleted!')
    except Exception as e:
        logger.error(f"Error deleting student: {str(e)}")
        messages.error(request, f"Error deleting student: {str(e)}")
    return redirect('view_student')

@login_required(login_url='/')
def ADD_COURSE(request):
    if request.method == "POST":
        course_name = request.POST.get('course_name')
        try:
            course = Course(name=course_name)
            course.save()
            messages.success(request, 'Course Successfully Created')
            return redirect('view_course')
        except Exception as e:
            logger.error(f"Error adding course: {str(e)}")
            messages.error(request, f"Error adding course: {str(e)}")
    return render(request, 'Hod/add_course.html')

@login_required(login_url='/')
def VIEW_COURSE(request):
    course = Course.objects.all()
    context = {
        'course': course,
    }
    return render(request, 'Hod/view_course.html', context)

@login_required(login_url='/')
def EDIT_COURSE(request, id):
    course = Course.objects.get(id=id)
    context = {
        'course': course,
    }
    return render(request, 'Hod/edit_course.html', context)

@login_required(login_url='/')
def UPDATE_COURSE(request):
    if request.method == "POST":
        name = request.POST.get('name')
        course_id = request.POST.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
            course.name = name
            course.save()
            messages.success(request, 'Course Successfully Updated')
            return redirect('view_course')
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            messages.error(request, f"Error updating course: {str(e)}")
    return render(request, 'Hod/edit_course.html')

@login_required(login_url='/')
def DELETE_COURSE(request, id):
    try:
        course = Course.objects.get(id=id)
        course.delete()
        messages.success(request, 'Course Successfully Deleted')
    except Exception as e:
        logger.error(f"Error deleting course: {str(e)}")
        messages.error(request, f"Error deleting course: {str(e)}")
    return redirect('view_course')

@login_required(login_url='/')
def ADD_STAFF(request):
    subjects = Subject.objects.all()
    courses = Course.objects.all()
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        course_id = request.POST.get('course_id')
        subject_id = request.POST.get('subject_id')
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken!')
            return redirect('add_staff')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken!')
            return redirect('add_staff')
        if subject_id and Staff.objects.filter(subjects__id=subject_id).exists():
            messages.error(request, 'This subject is already assigned to another staff member.')
            return redirect('add_staff')
        try:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                user_type=2
            )
            if profile_pic:
                logger.info(f"Processing profile_pic upload for user: {username}")
                user.profile_pic = profile_pic
            user.set_password(password)
            user.save()
            staff = Staff(
                admin=user,
                address=address,
                gender=gender
            )
            staff.save()
            if subject_id:
                subject = Subject.objects.get(id=subject_id)
                staff.subjects.add(subject)
            messages.success(request, 'Staff Successfully Added!')
            return redirect('add_staff')
        except Exception as e:
            logger.error(f"Error adding staff: {str(e)}")
            messages.error(request, f"Error adding staff: {str(e)}")
    context = {
        'subjects': subjects,
        'courses': courses,
    }
    return render(request, 'Hod/add_staff.html', context)

@login_required(login_url='/')
def VIEW_STAFF(request):
    staff = Staff.objects.all()
    context = {
        'staff': staff,
    }
    return render(request, 'Hod/view_staff.html', context)

@login_required(login_url='/')
def EDIT_STAFF(request, id):
    staff = Staff.objects.get(id=id)
    subjects = Subject.objects.all()
    courses = Course.objects.all()
    context = {
        'staff': staff,
        'subjects': subjects,
        'courses': courses,
    }
    return render(request, 'Hod/edit_staff.html', context)

@login_required(login_url='/')
def UPDATE_STAFF(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        subject_id = request.POST.get('subject_id')
        try:
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                logger.info(f"Updating profile_pic for user: {username}")
                user.profile_pic = profile_pic
            user.save()
            staff = Staff.objects.get(admin=staff_id)
            staff.address = address
            staff.gender = gender
            staff.save()
            if subject_id:
                existing_subjects = staff.subjects.all()
                new_subject = Subject.objects.get(id=subject_id)
                if new_subject not in existing_subjects and Staff.objects.filter(subjects__id=subject_id).exclude(id=staff.id).exists():
                    messages.error(request, 'This subject is already assigned to another staff member.')
                    return redirect('edit_staff', id=staff.id)
                staff.subjects.clear()
                staff.subjects.add(new_subject)
            else:
                staff.subjects.clear()
            messages.success(request, 'Staff Successfully Updated!')
            return redirect('view_staff')
        except Exception as e:
            logger.error(f"Error updating staff: {str(e)}")
            messages.error(request, f"Error updating staff: {str(e)}")
            return redirect('view_staff')
    return render(request, 'Hod/edit_staff.html')

@login_required(login_url='/')
def DELETE_STAFF(request, admin):
    try:
        staff = CustomUser.objects.get(id=admin)
        staff.delete()
        messages.success(request, 'Staff Successfully Deleted!')
    except Exception as e:
        logger.error(f"Error deleting staff: {str(e)}")
        messages.error(request, f"Error deleting staff: {str(e)}")
    return redirect('view_staff')

@login_required(login_url='/')
def ADD_SUBJECT(request):
    course = Course.objects.all()
    staff = Staff.objects.all()
    if request.method == "POST":
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course_id')
        credit = request.POST.get('credit')
        try:
            course = Course.objects.get(id=course_id)
            subject = Subject(
                name=subject_name,
                subject_code=subject_code,
                course=course,
                credit=credit if credit else None
            )
            subject.save()
            messages.success(request, 'Subject Successfully Added!')
            return redirect('view_subject')
        except Exception as e:
            logger.error(f"Error adding subject: {str(e)}")
            messages.error(request, f"Error adding subject: {str(e)}")
    context = {
        'course': course,
        'staff': staff,
    }
    return render(request, 'Hod/add_subject.html', context)

@login_required(login_url='/')
def VIEW_SUBJECT(request):
    subject = Subject.objects.all()
    context = {
        'subject': subject,
    }
    return render(request, 'Hod/view_subject.html', context)

@login_required(login_url='/')
def EDIT_SUBJECT(request, id):
    subject = Subject.objects.get(id=id)
    course = Course.objects.all()
    staff = Staff.objects.all()
    context = {
        'subject': subject,
        'course': course,
        'staff': staff,
    }
    return render(request, 'Hod/edit_subject.html', context)

@login_required(login_url='/')
def UPDATE_SUBJECT(request):
    if request.method == "POST":
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        course_id = request.POST.get('course_id')
        credit = request.POST.get('credit')
        try:
            subject = Subject.objects.get(id=subject_id)
            subject.name = subject_name
            subject.subject_code = subject_code
            course = Course.objects.get(id=course_id)
            subject.course = course
            subject.credit = credit if credit else None
            subject.save()
            messages.success(request, 'Subject Successfully Updated!')
            return redirect('view_subject')
        except Exception as e:
            logger.error(f"Error updating subject: {str(e)}")
            messages.error(request, f"Error updating subject: {str(e)}")
    return redirect('view_subject')

@login_required(login_url='/')
def DELETE_SUBJECT(request, id):
    try:
        subject = Subject.objects.get(id=id)
        subject.delete()
        messages.success(request, 'Subject Successfully Deleted!')
    except Exception as e:
        logger.error(f"Error deleting subject: {str(e)}")
        messages.error(request, f"Error deleting subject: {str(e)}")
    return redirect('view_subject')

@login_required(login_url='/')
def ADD_SESSION(request):
    if request.method == "POST":
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        try:
            session = Session_Year(
                session_start=session_year_start,
                session_end=session_year_end
            )
            session.save()
            messages.success(request, 'Session Successfully Created!')
            return redirect('view_session')
        except Exception as e:
            logger.error(f"Error adding session: {str(e)}")
            messages.error(request, f"Error adding session: {str(e)}")
    return render(request, 'Hod/add_session.html')

@login_required(login_url='/')
def VIEW_SESSION(request):
    session = Session_Year.objects.all()
    context = {
        'session': session,
    }
    return render(request, 'Hod/view_session.html', context)

@login_required(login_url='/')
def EDIT_SESSION(request, id):
    session = Session_Year.objects.get(id=id)
    context = {
        'session': session,
    }
    return render(request, 'Hod/edit_session.html', context)

@login_required(login_url='/')
def UPDATE_SESSION(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        try:
            session = Session_Year.objects.get(id=session_id)
            session.session_start = session_year_start
            session.session_end = session_year_end
            session.save()
            messages.success(request, 'Session Successfully Updated!')
            return redirect('view_session')
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            messages.error(request, f"Error updating session: {str(e)}")
    return redirect('view_session')

@login_required(login_url='/')
def DELETE_SESSION(request, id):
    try:
        session = Session_Year.objects.get(id=id)
        session.delete()
        messages.success(request, 'Session Successfully Deleted!')
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        messages.error(request, f"Error deleting session: {str(e)}")
    return redirect('view_session')

@login_required(login_url='/')
def ADD_PARENT(request):
    students = Student.objects.all()
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        relationship = request.POST.get('relationship')
        student_id = request.POST.get('student_id')
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken!')
            return redirect('add_parent')
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken!')
            return redirect('add_parent')
        try:
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                user_type=4
            )
            if profile_pic:
                logger.info(f"Processing profile_pic upload for user: {username}")
                user.profile_pic = profile_pic
            user.set_password(password)
            user.save()
            student = Student.objects.get(id=student_id)
            parent = Parent(
                admin=user,
                student=student,
                relationship=relationship,
                phone_number=phone_number,
                address=address
            )
            parent.save()
            messages.success(request, 'Parent Successfully Added!')
            return redirect('add_parent')
        except Exception as e:
            logger.error(f"Error adding parent: {str(e)}")
            messages.error(request, f"Error adding parent: {str(e)}")
    context = {
        'students': students,
    }
    return render(request, 'Hod/add_parent.html', context)

@login_required(login_url='/')
def VIEW_PARENT(request):
    parents = Parent.objects.all()
    context = {
        'parents': parents,
    }
    return render(request, 'Hod/view_parent.html', context)

@login_required(login_url='/')
def EDIT_PARENT(request, id):
    parent = Parent.objects.get(id=id)
    students = Student.objects.all()
    context = {
        'parent': parent,
        'students': students,
    }
    return render(request, 'Hod/edit_parent.html', context)

@login_required(login_url='/')
def UPDATE_PARENT(request):
    if request.method == "POST":
        parent_id = request.POST.get('parent_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        relationship = request.POST.get('relationship')
        student_id = request.POST.get('student_id')
        try:
            user = CustomUser.objects.get(id=parent_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if password and password.strip():
                user.set_password(password)
            if profile_pic:
                logger.info(f"Updating profile_pic for user: {username}")
                user.profile_pic = profile_pic
            user.save()
            parent = Parent.objects.get(admin=parent_id)
            parent.phone_number = phone_number
            parent.address = address
            parent.relationship = relationship
            student = Student.objects.get(id=student_id)
            parent.student = student
            parent.save()
            messages.success(request, 'Parent Successfully Updated!')
            return redirect('view_parent')
        except Exception as e:
            logger.error(f"Error updating parent: {str(e)}")
            messages.error(request, f"Error updating parent: {str(e)}")
            return redirect('view_parent')
    return render(request, 'Hod/edit_parent.html')

@login_required(login_url='/')
def DELETE_PARENT(request, admin):
    try:
        parent = CustomUser.objects.get(id=admin)
        parent.delete()
        messages.success(request, 'Parent Successfully Deleted!')
    except Exception as e:
        logger.error(f"Error deleting parent: {str(e)}")
        messages.error(request, f"Error deleting parent: {str(e)}")
    return redirect('view_parent')

@login_required(login_url='/')
def STAFF_SEND_NOTIFICATION(request):
    staff = Staff.objects.all()
    context = {
        'staff': staff,
    }
    return render(request, 'Hod/staff_notification.html', context)

@login_required(login_url='/')
def SAVE_STAFF_NOTIFICATION(request):
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        message = request.POST.get('message')
        try:
            staff = Staff.objects.get(id=staff_id)
            notification = Staff_Notification(
                staff_id=staff,
                message=message
            )
            notification.save()
            messages.success(request, 'Notification Successfully Sent!')
        except Exception as e:
            logger.error(f"Error sending staff notification: {str(e)}")
            messages.error(request, f"Error sending notification: {str(e)}")
    return redirect('staff_send_notification')

@login_required(login_url='/')
def STUDENT_SEND_NOTIFICATION(request):
    student = Student.objects.all()
    context = {
        'student': student,
    }
    return render(request, 'Hod/student_notification.html', context)

@login_required(login_url='/')
def SAVE_STUDENT_NOTIFICATION(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        message = request.POST.get('message')
        try:
            student = Student.objects.get(id=student_id)
            notification = Student_Notification(
                student_id=student,
                message=message
            )
            notification.save()
            messages.success(request, 'Notification Successfully Sent!')
        except Exception as e:
            logger.error(f"Error sending student notification: {str(e)}")
            messages.error(request, f"Error sending notification: {str(e)}")
    return redirect('student_send_notification')

@login_required(login_url='/')
def STAFF_LEAVE_VIEW(request):
    staff_leave = Staff_leave.objects.all()
    context = {
        'staff_leave': staff_leave,
    }
    return render(request, 'Hod/staff_leave.html', context)

@login_required(login_url='/')
def STAFF_APPROVE_LEAVE(request, id):
    try:
        leave = Staff_leave.objects.get(id=id)
        leave.status = 1
        leave.save()
        messages.success(request, 'Leave Approved!')
    except Exception as e:
        logger.error(f"Error approving staff leave: {str(e)}")
        messages.error(request, f"Error approving leave: {str(e)}")
    return redirect('staff_leave_view')

@login_required(login_url='/')
def STAFF_DISAPPROVE_LEAVE(request, id):
    try:
        leave = Staff_leave.objects.get(id=id)
        leave.status = 2
        leave.save()
        messages.success(request, 'Leave Disapproved!')
    except Exception as e:
        logger.error(f"Error disapproving staff leave: {str(e)}")
        messages.error(request, f"Error disapproving leave: {str(e)}")
    return redirect('staff_leave_view')

@login_required(login_url='/')
def STUDENT_LEAVE_VIEW(request):
    student_leave = Student_leave.objects.all()
    context = {
        'student_leave': student_leave,
    }
    return render(request, 'Hod/student_leave.html', context)

@login_required(login_url='/')
def STUDENT_APPROVE_LEAVE(request, id):
    try:
        leave = Student_leave.objects.get(id=id)
        leave.status = 1
        leave.save()
        messages.success(request, 'Leave Approved!')
    except Exception as e:
        logger.error(f"Error approving student leave: {str(e)}")
        messages.error(request, f"Error approving leave: {str(e)}")
    return redirect('student_leave_view')

@login_required(login_url='/')
def STUDENT_DISAPPROVE_LEAVE(request, id):
    try:
        leave = Student_leave.objects.get(id=id)
        leave.status = 2
        leave.save()
        messages.success(request, 'Leave Disapproved!')
    except Exception as e:
        logger.error(f"Error disapproving student leave: {str(e)}")
        messages.error(request, f"Error disapproving leave: {str(e)}")
    return redirect('student_leave_view')

@login_required(login_url='/')
def STAFF_FEEDBACK(request):
    feedback = Staff_Feedback.objects.all()
    context = {
        'feedback': feedback,
    }
    return render(request, 'Hod/staff_feedback.html', context)

@login_required(login_url='/')
def STAFF_FEEDBACK_SAVE(request):
    if request.method == "POST":
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')
        try:
            feedback = Staff_Feedback.objects.get(id=feedback_id)
            feedback.feedback_reply = feedback_reply
            feedback.status = 1
            feedback.save()
            messages.success(request, 'Feedback Reply Successfully Sent!')
        except Exception as e:
            logger.error(f"Error saving staff feedback reply: {str(e)}")
            messages.error(request, f"Error saving feedback reply: {str(e)}")
    return redirect('staff_feedback_reply')

@login_required(login_url='/')
def STUDENT_FEEDBACK(request):
    feedback = Student_Feedback.objects.all()
    context = {
        'feedback': feedback,
    }
    return render(request, 'Hod/student_feedback.html', context)

@login_required(login_url='/')
def REPLY_STUDENT_FEEDBACK(request):
    if request.method == "POST":
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')
        try:
            feedback = Student_Feedback.objects.get(id=feedback_id)
            feedback.feedback_reply = feedback_reply
            feedback.status = 1
            feedback.save()
            messages.success(request, 'Feedback Reply Successfully Sent!')
        except Exception as e:
            logger.error(f"Error saving student feedback reply: {str(e)}")
            messages.error(request, f"Error saving feedback reply: {str(e)}")
    return redirect('get_student_feedback')

@login_required(login_url='/')
def VIEW_ATTENDANCE(request):
    subject = Subject.objects.all()
    session_year = Session_Year.objects.all()
    context = {
        'subject': subject,
        'session_year': session_year,
    }
    return render(request, 'Hod/view_attendance.html', context)

@login_required(login_url='/')
def get_subjects_by_course(request):
    course_id = request.GET.get('course_id')
    subjects = Subject.objects.filter(course_id=course_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)