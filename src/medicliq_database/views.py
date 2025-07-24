import os
import json
from django.shortcuts import render, redirect
from .forms import PatientForm
from medicliq_database.models import Transaction
from .models import Patient, MedShelfMapper, Doctor, ScannedPrescription, Prescription, PrescriptionMedicine, StockMovement, Payment
from .utils import perform_ocr, extract_prescription_details, extract_and_save_edited_text
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
import razorpay
import tempfile
from django.utils.translation import gettext as _
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np
import re
from django.utils.translation import activate
from django.http import JsonResponse
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import qrcode  # Add this with other imports
import time 
from django.core.cache import cache
import uuid
from django.urls import reverse



#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust path if needed



#################################################################

import socket

def get_host_ip():
    try:
        # First try external connection method
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        # Fallback to local network interface scan
        hostname = socket.gethostname()
        return socket.gethostbyname_ex(hostname)[2][-1]  # Get last non-localhost IP
    
from django.core.cache import cache
import uuid

def generate_qr(request):
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        cache.set(f'session_{session_id}', {'status': 'waiting'}, timeout=300)

        # Get server IP
        server_ip = get_host_ip()
        qr_url = f"http://{server_ip}:8000/database/mobile_upload/?session={session_id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to static directory
        qr_dir = os.path.join(settings.STATICFILES_DIRS[0], 'qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, 'qr_code.png')
        img.save(qr_path)

        return render(request, "qr_display.html", {
            "qr_path": f"/static/qr_codes/qr_code.png?t={int(time.time())}",
            "session_id": session_id
        })

    except Exception as e:
        return HttpResponse(f"QR Generation Error: {str(e)}", status=500)

def check_upload(request):
    session_id = request.GET.get('session')
    if not session_id:
        return JsonResponse({"error": "Session ID missing"}, status=400)
    
    cache_key = f'session_{session_id}'
    data = cache.get(cache_key, {"status": "invalid", "processed": False})
    
    return JsonResponse({
        "status": data.get("status", "invalid"),
        "processed": data.get("processed", False),
        "timestamp": data.get("timestamp", 0)
    })

def qr_upload_page(request):
    """Mobile-friendly upload page"""
    return render(request, "mobile_upload.html")

@csrf_exempt
def handle_mobile_upload(request):
    if request.method == "POST":
        session_id = request.GET.get('session')
        if not session_id:
            return JsonResponse({"success": False, "error": "Session ID missing"}, status=400)
        
        cache_key = f'session_{session_id}'
        
        try:
            if 'prescription_image' not in request.FILES:
                return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)
            
            file = request.FILES['prescription_image']
            
            # Save file temporarily
            temp_dir = os.path.join('temp', 'mobile_uploads')
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.name)
            
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            # Process image (assuming no return value needed)
            process_image(file_path)  # Keep your existing function unchanged
            
            # Mark as successful if no exceptions
            cache.set(cache_key, {
                "status": "completed",
                "processed": True,
                "timestamp": time.time()
            }, timeout=300)
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            cache.set(cache_key, {
                "status": "error",
                "error": str(e)
            }, timeout=300)
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def upload_status(request):
    session_id = request.GET.get('session')
    data = cache.get(session_id) or {'status': 'invalid'}
    return JsonResponse(data)

#function for language setting
def set_language(request):
    if request.method == "POST":
        LANGUAGE = request.POST.get("language", "en")  # Get selected language
        activate(LANGUAGE)  # Activate language
        request.session["django_language"] = LANGUAGE  # Store in session
        return JsonResponse({"message": "Language set successfully", "lang": LANGUAGE})
    return JsonResponse({"error": "Invalid request"}, status=400)


# Function to preprocess the image
def preprocess_image(pil_image):
    pil_image = pil_image.convert('L')  # Convert to grayscale
    threshold = 160
    pil_image = pil_image.point(lambda p: p > threshold and 255)  # Binarize the image
    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(4)  # Increase contrast
    enhancer = ImageEnhance.Sharpness(pil_image)
    pil_image = enhancer.enhance(4)  # Sharpen the image
    pil_image = pil_image.filter(ImageFilter.EDGE_ENHANCE_MORE)  # Enhance edges
    pil_image = pil_image.resize((pil_image.width * 3, pil_image.height * 3), Image.Resampling.LANCZOS)  # Resize
    return np.array(pil_image)

# Function to correct common OCR mistakes
def correct_ocr_mistakes(text):
    corrections = {
        'I': '1',
        'O': '0',
        'l': '1',
        '1': 'l',
        'S': '5',  # Special fix for S -> 5 issue
    }

    def apply_contextual_correction(word):
        if re.match(r'^\d+$', word):  # Numbers only
            return word.replace('l', '1')
        elif re.match(r'^[A-Za-z0-9]+$', word):  # Alphanumeric strings
            corrected_word = ""
            for i, char in enumerate(word):
                if char == '1' and (i > 0 and word[i - 1].isdigit() or i < len(word) - 1 and word[i + 1].isdigit()):
                    corrected_word += '1'
                elif char == 'l' and (i > 0 and word[i - 1].isalpha() or i < len(word) - 1 and word[i + 1].isalpha()):
                    corrected_word += 'l'
                else:
                    corrected_word += char

                # Special correction for 'S' misread as '5'
                if char == 'S' and (i > 0 and word[i - 1].isdigit() or i < len(word) - 1 and word[i + 1].isdigit()):
                    corrected_word = corrected_word[:-1] + '5'

            return corrected_word
        return word

    corrected_words = [apply_contextual_correction(word) for word in text.split()]
    return " ".join(corrected_words)



def homepage(request):
    return render(request, 'index.html')

def p_method(request):
    return render(request,'p_method.html')

def language_selection(request):
    return render(request, 'language_selection.html')

def prescription_image(request):
    return render(request, 'prescription_image.html')

def upload_through_scanner(request):
    return render(request, 'upload_through_scanner.html')

def scanner_instructions(request):
    """Render scanner instructions page"""
    return render(request, "scanner_instructions.html")

def scanning_view(request):
    """Render actual scanner interface (existing functionality)"""
    return render(request, "upload_through_scanner.html")

def scan_image(request):
    """Handle scanner image capture and processing"""
    if request.method == "POST":
        try:
            # Generate unique filename
            filename = f"scanned_{int(time.time())}.png"
            temp_dir = os.path.join('temp', 'scans')
            os.makedirs(temp_dir, exist_ok=True)
            output_path = os.path.join(temp_dir, filename)

            # Scan command
            command = [
                "scanimage",
                "--format=png",
                "--mode", "color",
                "--resolution", "150",
                "--output-file", output_path
            ]

            # Run scanning process
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )

            if result.returncode != 0:
                raise Exception(f"Scanner error: {result.stderr.decode()}")

            # Process image through OCR pipeline
            success = process_image(output_path)
            
            return JsonResponse({
                "success": success,
                "redirect": reverse("selectmedicine")
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"Scan failed: {str(e)}"
            }, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def process_image(image_path):
    """Helper function to process an image through OCR and extract medicine details."""
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Failed to load the image.")

    # Convert image to PIL format
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Preprocess and perform OCR
    preprocessed_image = preprocess_image(pil_image)
    text = pytesseract.image_to_string(preprocessed_image)

    # Correct OCR mistakes
    corrected_text = correct_ocr_mistakes(text)

    # Save the extracted and corrected text
    extracted_info_path = os.path.join('temp', 'extracted_info.txt')
    with open(extracted_info_path, 'w') as file:
        file.write(corrected_text)

    # Extract medicine details
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    file_path = os.path.join(BASE_DIR, "temp", "extracted_info.txt")
    output_path = os.path.join(BASE_DIR, "temp", "extracted_medicine_data.json")
    
    pattern = re.compile(
        r"(?P<medicine>[A-Za-z0-9\.\-]+)\s+"
        r"(?P<dosage>\d+-\d+-\d+)\s+"
        r"(?P<duration>\d+\s?days?)\s+"
        r"(?P<measure>\d+)\s+"
        r"(?P<instruction>Before Meal|After Meal|Any Meal|With Meal)\b",
        re.IGNORECASE | re.MULTILINE
    )

    try:
        with open(file_path, 'r') as file:
            text = file.read()
        
        matches = pattern.finditer(text)
        extracted_info = []
        for match in matches:
            medicine_info = {
                "Medicine": match.group("medicine").strip(),
                "Dosage": match.group("dosage"),
                "Duration": match.group("duration"),
                "Measure": match.group("measure"),
                "Instruction": match.group("instruction")
            }
            extracted_info.append(medicine_info)
        
        result = {"Medicines": extracted_info}
        
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, indent=4)
        
        # Process to create processed_medicines.json
        input_path = os.path.join(BASE_DIR, "temp", "extracted_medicine_data.json")
        output_path = os.path.join(BASE_DIR, "temp", "processed_medicines.json")
        
        with open(input_path, "r") as infile:
            input_data = json.load(infile)

        output_data = {"Medicines": []}

        med_shelf_data = {
            med.medname.lower(): {
                "Avail_quantity": med.avail_quantity,
                "Strip_size": med.strip_size,
                "Price_per_unit": med.price_per_unit
            }
            for med in MedShelfMapper.objects.all()
        }

        for med in input_data["Medicines"]:
            med_name = med["Medicine"].lower()
            ones_count = med["Dosage"].count('1')
            duration = int(med["Duration"].split()[0])
            measure = int(med["Measure"])

            quant = ones_count * duration * measure
            medperday = quant / duration if duration > 0 else 0

            if med_name in med_shelf_data:
                available = 1 if med_shelf_data[med_name]["Avail_quantity"] > 0 else 0
                stripsize = med_shelf_data[med_name]["Strip_size"]
                ppu = med_shelf_data[med_name]["Price_per_unit"]
            else:
                available = 0
                stripsize = None
                ppu = None

            output_data["Medicines"].append({
                "Medicinename": med_name,
                "quant": quant,
                "days": duration,
                "medperday": medperday,
                "Available": available,
                "stripsize": stripsize,
                "ppu": ppu
            })

        with open(output_path, "w") as outfile:
            json.dump(output_data, outfile, indent=4)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def handle_scanner_upload(request):
    """View to handle scanner upload and process the image."""
    if request.method == 'GET':
        try:
            # Scan and save image to temp directory
            output_filename = "scanned_image.png"
            temp_dir = os.path.join('temp')
            os.makedirs(temp_dir, exist_ok=True)
            output_path = os.path.join(temp_dir, output_filename)
            
            command = [
                "scanimage",
                "--format=png",
                "--mode", "gray",
                "--resolution", "150"
            ]

            with open(output_path, "wb") as output_file:
                subprocess.run(command, stdout=output_file, check=True)

            # Process the scanned image
            success = process_image(output_path)
            if success:
                return redirect('selectmedicine')
            else:
                return HttpResponse("Error processing image", status=400)
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"Scanner error: {e}", status=500)
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
    return HttpResponse("Invalid request method", status=400)

# Django view for uploading and processing prescriptions
def upload_prescription(request):
    if request.method == 'POST' and request.FILES.get('prescription_image'):
        uploaded_image = request.FILES['prescription_image']
        
        # Save to temp directory
        temp_dir = os.path.join('temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_image.name)
        
        with open(temp_path, 'wb') as f:
            for chunk in uploaded_image.chunks():
                f.write(chunk)

        # Process the image
        success = process_image(temp_path)
        if success:
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Processing failed"}, status=400)
    return render(request, 'upload_prescription.html')

def select_medicine(request):
    BASE_DIR= os.path.abspath(os.path.join(os.path.dirname(__file__),"../"))
    json_path= os.path.join(BASE_DIR,"temp","processed_medicines.json")

    # Read the processed JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Pass all attributes from JSON
    medicines = [
        {
            "name": med["Medicinename"],
            "quantity": med["quant"],
            "days": med["days"],
            "medperday": med["medperday"],
            "available": med["Available"],
            "stripsize": med["stripsize"],
            "price": med["ppu"],  # ✅ Ensure price is passed
        }
        for med in data["Medicines"]
    ]

    return render(request, 'selectmedicine.html', {"medicines": medicines})

def cart(request):
    cart_data = request.session.get("cart", [])  # Fetch cart data from session
    total_amount = sum(item["price"] * item["quantity"] for item in cart_data)

    return render(request, "cart.html", {"cart_data": cart_data, "total_amount": total_amount})
























# Save Prescription and Medicines
def save_prescription(request):
    if request.method == 'POST':
        extracted_details = json.loads(request.POST['details'])

        # Store medicine details in the MedShelfMapper
        for med in extracted_details['medicine_details']:
            med_shelf = MedShelfMapper.objects.create(
                medname=med['Medicine Name'],
                avail_quantity=10,
                price_per_unit=100.0,
            )

        return redirect('payment_success')

    return JsonResponse({"error": "Invalid request"}, status=400)


# Register Patient
def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'register_patient.html', {'form': form})

# Login for Patients
def custom_login(request):
    return render(request, 'login.html')

# Login Patient
def login_patient(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        patient = authenticate(request, email=email, password=password)
        if patient is not None:
            login(request, patient)
            return redirect('payment')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')