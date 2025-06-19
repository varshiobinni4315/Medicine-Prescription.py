# app.py
import os
import sys
from django.conf import settings
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.db import models
from django.core.management import execute_from_command_line

BASE_DIR = os.path.dirname(__file__)
settings.configure(
    DEBUG=True,
    SECRET_KEY='devkey',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    MIDDLEWARE=['django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware'],
    INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth', 'django.contrib.sessions', 'django.contrib.admin', '__main__'],
    TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR],'APP_DIRS':True}],
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':os.path.join(BASE_DIR,'db.sqlite3')}},
)

# Models
class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    issued = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)

# Forms
class PatientForm(forms.ModelForm):
    class Meta: model = Patient; fields = '__all__'

class MedicineForm(forms.ModelForm):
    class Meta: model = Medicine; fields = '__all__'

class PrescriptionForm(forms.ModelForm):
    class Meta: model = Prescription; fields = ['patient', 'medicine', 'dosage']

# Views
def home(request):
    return render(request, 'home.html')

def add_patient(request):
    if request.method=='POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PatientForm()
    return render(request, 'form.html', {'form': form, 'title': 'New Patient'})

def add_medicine(request):
    if request.method=='POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MedicineForm()
    return render(request, 'form.html', {'form': form, 'title': 'New Medicine'})

def add_prescription(request):
    if request.method=='POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PrescriptionForm()
    return render(request, 'form.html', {'form': form, 'title': 'New Prescription'})

def list_prescriptions(request):
    pres = Prescription.objects.select_related('patient','medicine').all()
    return render(request, 'list.html', {'prescriptions': pres})

def fulfill_prescription(request, pk):
    pres = get_object_or_404(Prescription, pk=pk)
    pres.fulfilled = True
    pres.save()
    return redirect('list_prescriptions')

# URLs
urlpatterns = [
    path('', home, name='home'),
    path('patient/', add_patient, name='add_patient'),
    path('medicine/', add_medicine, name='add_medicine'),
    path('prescribe/', add_prescription, name='add_prescription'),
    path('prescriptions/', list_prescriptions, name='list_prescriptions'),
    path('fulfill/<int:pk>/', fulfill_prescription, name='fulfill'),
]

# Templates
T1 = """
<h1>E‑Prescription System</h1>
<ul>
  <li><a href="{% url 'add_patient' %}">Add Patient</a></li>
  <li><a href="{% url 'add_medicine' %}">Add Medicine</a></li>
  <li><a href="{% url 'add_prescription' %}">New Prescription</a></li>
  <li><a href="{% url 'list_prescriptions' %}">View Prescriptions</a></li>
</ul>
"""
T2 = """
<h2>{{ title }}</h2>
<form method="post">{% csrf_token %}{{ form.as_p }}<button>Submit</button></form>
<a href="{% url 'home' %}">Home</a>
"""
T3 = """
<h2>Prescriptions</h2>
<table border="1">
<tr><th>ID</th><th>Patient</th><th>Medicine</th><th>Dosage</th><th>Issued</th><th>Fulfilled</th><th>Action</th></tr>
{% for p in prescriptions %}
<tr>
<td>{{ p.id }}</td>
<td>{{ p.patient.name }}</td>
<td>{{ p.medicine.name }}</td>
<td>{{ p.dosage }}</td>
<td>{{ p.issued }}</td>
<td>{{ p.fulfilled }}</td>
<td>{% if not p.fulfilled %}<a href="{% url 'fulfill' p.id %}">Fulfill</a>{% endif %}</td>
</tr>
{% endfor %}
</table><a href="{% url 'home' %}">Home</a>
"""
open(os.path.join(BASE_DIR,'home.html'),'w').write(T1)
open(os.path.join(BASE_DIR,'form.html'),'w').write(T2)
open(os.path.join(BASE_DIR,'list.html'),'w').write(T3)

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '__main__')
    execute_from_command_line(sys.argv)

