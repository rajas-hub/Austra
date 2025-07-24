from csv import reader
import os
# import easyocr
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import re

# # Initialize the EasyOCR reader
#reader = easyocr.Reader(['en'])  # Specify the language(s) you want to use

# Function to preprocess the image before OCR
def preprocess_image(pil_image):
    pil_image = pil_image.convert('L')  # Convert to grayscale
    threshold = 160
    pil_image = pil_image.point(lambda p: p > threshold and 255)  # Binarize the image
    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(4)  # Enhance contrast
    enhancer = ImageEnhance.Sharpness(pil_image)
    pil_image = enhancer.enhance(4)  # Enhance sharpness
    pil_image = pil_image.filter(ImageFilter.EDGE_ENHANCE_MORE)  # Apply edge enhancement
    pil_image = pil_image.resize((pil_image.width * 3, pil_image.height * 3), Image.Resampling.LANCZOS)  # Upscale image
    return np.array(pil_image)

# Function to perform OCR on the image
def perform_ocr(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Check if the image was loaded successfully
    if image is None:
        raise FileNotFoundError(f"Error: The image at path '{image_path}' could not be loaded. Please check the file path.")

    # Convert numpy.ndarray (OpenCV format) to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Preprocess the image before performing OCR
    preprocessed_image = preprocess_image(pil_image)

    # Perform OCR on the preprocessed image
    results = reader.readtext(preprocessed_image)

    # Save OCR results to a file
    output_txt_path = './detected_text.txt'
    with open(output_txt_path, 'w') as file:
        for (bbox, text, prob) in results:
            corrected_text = correct_ocr_mistakes(text)
            file.write(f"Detected text: '{corrected_text}' (Original: '{text}') with confidence: {prob:.2f}\n")
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, np.array(top_left) / 3))
            bottom_right = tuple(map(int, np.array(bottom_right) / 3))
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

    # Save the output image with bounding boxes
    output_image_path = './output_image.jpg'
    cv2.imwrite(output_image_path, image)
    
    print(f"Output image saved at: {output_image_path}")
    print(f"Detected text saved at: {output_txt_path}")

    return output_txt_path

# Function to correct common OCR mistakes
def correct_ocr_mistakes(text):
    corrections = {
        'I': '1',
        'O': '0',
        'l': '1',
        '1': 'l'
    }

    def apply_contextual_correction(word):
        if re.match(r'^\d+$', word):
            return word.replace('l', '1')
        elif re.match(r'^[A-Za-z0-9]+$', word):
            corrected_word = ""
            for i, char in enumerate(word):
                if char == '1' and (i > 0 and word[i-1].isdigit() or i < len(word) - 1 and word[i+1].isdigit()):
                    corrected_word += '1'
                elif char == 'l' and (i > 0 and word[i-1].isalpha() or i < len(word) - 1 and word[i+1].isalpha()):
                    corrected_word += 'l'
                else:
                    corrected_word += char
            return corrected_word
        return word

    corrected_words = [apply_contextual_correction(word) for word in text.split()]
    return " ".join(corrected_words)

# Function to extract and save the cleaned text from the detected OCR text
def extract_and_save_edited_text(input_txt_path, output_txt_path):
    with open(input_txt_path, 'r') as file:
        lines = file.readlines()

    # Extract the text between the first pair of single quotes for each line
    edited_lines = []
    for line in lines:
        match = re.search(r"'(.*?)'", line)
        if match:
            edited_lines.append(match.group(1))

    with open(output_txt_path, 'w') as output_file:
        for edited_line in edited_lines:
            output_file.write(f"{edited_line}\n")

    print(f"Edited text has been written to: {output_txt_path}")
    return output_txt_path

# Function to extract prescription details (patient name, mobile number, medicine details)
def extract_prescription_details(file_path):
    with open(file_path, 'r') as file:
        text_content = file.read()
        
    lines = text_content.splitlines()
    
    # Extracting patient name
    for i, line in enumerate(lines):
        if "Dr." in line or "Dr" in line:
            if i > 0:
                patient_name_line = lines[i-1]
                patient_name_match = re.match(r'^(.*?)\s*\(', patient_name_line)
                if patient_name_match:
                    patient_name = patient_name_match.group(1).strip()
            break

    # Extracting Mobile number
    mobile_number_match = re.search(r'(?<=Registration No:\n)\b\d{10}\b', text_content)

    mobile_number = mobile_number_match.group(0).strip() if mobile_number_match else None

    # Extracting medicine details
    medicine_details = []
    instruction_start = text_content.find("Instruction")
    notes_start = text_content.find("Notes;")
    for_aagya = text_content.find("For Aagya Clinic")
    
    upper_lim = for_aagya if notes_start == -1 else notes_start

    lines = text_content[instruction_start + 1:upper_lim].strip().splitlines()

    for i in range(0, len(lines), 5):
        if i + 4 < len(lines):
            medicine_name = lines[i+1].strip()
            duration = lines[i + 3].strip()
            measure = lines[i + 4].strip()
            medicine_details.append({
                "Medicine Name": medicine_name,
                "Duration": duration,
                "Measure": measure
            })

    # Output the results
# Open the output.txt file in write mode (creates the file if it doesn't exist)
    with open("output.txt", "w") as file:
        # Print statements will now be written to the file
        print("Patient Name:", patient_name, file=file)
        print("Mobile Number:", mobile_number, file=file)
        print("Medicine Details:", file=file)
        for detail in medicine_details:
            print(detail, file=file)


    return {
        "patient_name": patient_name,
        "mobile_number": mobile_number,
        "medicine_details": medicine_details
    }
