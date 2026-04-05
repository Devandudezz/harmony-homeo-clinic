from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.dateformat import DateFormat
from .models import Patient

# Frontend page
def frontend(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('backend'))
    return render(request, "frontend.html")

# Backend dashboard with search + pagination
@cache_control(no_cache=True, must_validate=True, no_store=True)
@login_required(login_url='login')
def backend(request):
    if 'q' in request.GET:
        q = request.GET['q']
        all_patient_list = Patient.objects.filter(
            Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q) |
            Q(age__icontains=q) | Q(gender__icontains=q) | Q(note__icontains=q)
        ).order_by('-created_at')
    else:
        all_patient_list = Patient.objects.all().order_by('-created_at')

    paginator = Paginator(all_patient_list, 10)
    page = request.GET.get('page')
    all_patient = paginator.get_page(page)

    return render(request, 'backend.html', {"patients": all_patient})

# Add patient
import datetime
from django.utils.dateparse import parse_datetime

from django.utils.dateparse import parse_datetime
from .models import Patient
from django.utils import timezone

@cache_control(no_cache=True, must_validate=True, no_store=True)
@login_required(login_url='login')
def add_patient(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        created_at = request.POST.get('created_at') or timezone.now()
        note = request.POST.get('note')

        Patient.objects.create(
            name=name,
            phone=phone,
            email=email,
            age=age,
            gender=gender,
            created_at=created_at,
            note=note
        )
        messages.success(request, "✅ Patient added successfully.")
        return redirect('backend')

    return render(request, 'add.html')
   # return render(request, 'add.html', {'now': timezone.now()})

# View patient (redirects to edit page)
@cache_control(no_cache=True, must_validate=True, no_store=True)
@login_required(login_url='login')
def patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'edit.html', {'patient': patient})

# Edit patient
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from .models import Patient

from django.utils.timezone import now
from django.utils.dateparse import parse_datetime

@cache_control(no_cache=True, must_validate=True, no_store=True)
@login_required(login_url='login')
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.email = request.POST.get('email')
        patient.age = request.POST.get('age')
        patient.gender = request.POST.get('gender')
        patient.note = request.POST.get('note')

        created_at_str = request.POST.get('created_at')
        if created_at_str:
            from datetime import datetime
            try:
                patient.created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                patient.created_at = timezone.now()

        patient.save()
        messages.success(request, "✏️ Patient edited successfully.")
        return redirect('backend') 
     # or wherever you want to go after editing
    return render(request, 'edit.html', {
        'patient': patient,'now': now(), })


@cache_control(no_cache=True, must_validate=True, no_store=True)
@login_required(login_url='login')
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    patient.delete()
    messages.success(request, 'Patient removed successfully')
    return HttpResponseRedirect(reverse('backend'))

# Get patient details for modal view (AJAX)
@login_required(login_url='login')
@login_required(login_url='login')
def get_patient_details(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    data = {
        "name": patient.name,
        "phone": patient.phone,
        "email": patient.email,
        "age": patient.age,
        "gender": patient.gender,
        "note": patient.note,
        "created_at": DateFormat(patient.created_at).format('d-m-Y H:i')
    }
    return JsonResponse(data)


# Download all patients as PDF (formatted & modern)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from .models import Patient
@login_required(login_url='login')
def download_all_patients_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_patients.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph("All Registered Patients", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [['Name', 'Phone', 'Email', 'Age', 'Gender', 'Registered At']]
    patients = Patient.objects.all().order_by('-created_at')

    for p in patients:
        data.append([
            p.name, p.phone, p.email, p.age, p.gender,
            p.created_at.strftime("%d-%m-%Y %H:%M")
        ])

    table = Table(data, colWidths=[80, 80, 100, 40, 50, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f0f8ff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightcyan])
    ]))
    elements.append(table)
    doc.build(elements)
    return response

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import Frame, Image
from django.utils.dateformat import DateFormat
from reportlab.lib.styles import ParagraphStyle

@login_required(login_url='login')
def download_single_patient_pdf(request, patient_id):
    from django.shortcuts import get_object_or_404

    patient = get_object_or_404(Patient, pk=patient_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{patient.name}_details.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Heading', fontSize=14, leading=20, spaceAfter=10, fontName='Helvetica-Bold'))

    title = Paragraph(f"Patient Details: {patient.name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # Patient information in two-column layout
    patient_data = [
        ["Name:", patient.name],
        ["Phone:", patient.phone],
        ["Email:", patient.email],
        ["Age:", patient.age],
        ["Gender:", patient.gender],
        ["Registered At:", DateFormat(patient.created_at).format('d-m-Y H:i')],
    ]

    table = Table(patient_data, colWidths=[120, 360])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#d9e1f2")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.1, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Notes Section - Highlighted Box
    note_title = Paragraph("Notes", styles['Heading'])
    note_content = Paragraph(patient.note.replace('\n', '<br/>'), styles['Normal'])

    note_box = Table([[note_content]], colWidths=[480])
    note_box.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#003366")),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eef3f7")),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    elements.append(note_title)
    elements.append(Spacer(1, 6))
    elements.append(note_box)

    doc.build(elements)
    return response
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.dateparse import parse_date
import datetime

@login_required(login_url='login')
def download_patients_by_date(request):
    selected_date = request.GET.get('date')
    if not selected_date:
        return HttpResponse("Date is required", status=400)

    try:
        date_obj = parse_date(selected_date)
        start = datetime.datetime.combine(date_obj, datetime.time.min)
        end = datetime.datetime.combine(date_obj, datetime.time.max)
        patients = Patient.objects.filter(created_at__range=(start, end))
    except Exception as e:
        return HttpResponse(f"Invalid date: {str(e)}", status=400)

    # PDF setup
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="patients_{selected_date}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Patients Registered on {selected_date}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [['Name', 'Phone', 'Email', 'Age', 'Gender', 'Registered At']]
    for p in patients:
        data.append([
            p.name,
            p.phone,
            p.email,
            str(p.age),
            p.gender,
            p.created_at.strftime("%d-%m-%Y %H:%M")
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    doc.build(elements)

    return response

