# 💊 Auṣatra – Automatic Medicine Dispensing System

> A smart, interdisciplinary solution designed to automate the process of medicine dispensing using a secure, user-friendly system.

---

## 📦 Overview

**Auṣatra** is an automatic medicine dispensing system built using **Django**, **HTML/CSS/JS**, and integrated with **hardware automation (Arduino/Raspberry Pi)**. It ensures quick, accurate, and contactless delivery of prescribed medicines through:

- QR code–based prescription uploads
- Smart shelf mapping
- Inventory management
- Integrated payment gateway
- Real-time updates to the database

---

## 🔧 Features

- 📤 **QR-based Prescription Upload System**
  - Upload prescriptions from any mobile device by scanning a QR code

- 💡 **Automated Dispensing**
  - Uses a **spring-based 2x4 mechanical dispensing unit**
  - Controlled by Raspberry Pi or Arduino

- 💳 **Secure Online Payment**
  - Integrated with Razorpay test mode
  - Payment triggers dispensing only if medicine is in stock

- 📊 **Smart Inventory Management**
  - Admin dashboard for managing medicine stock
  - Real-time stock deduction after successful transactions

- 🔗 **WebSocket-based Communication**
  - Real-time prescription transfer between mobile device and system
  - Displays prescription PDF/image on screen after upload

- 📱 **User-Friendly Interface**
  - Developed with HTML, CSS, JS, and Django backend
  - Includes animated UI for better user engagement

---

## ⚙️ Tech Stack

| Layer        | Technology                        |
|--------------|------------------------------------|
| Frontend     | HTML, CSS, JavaScript, MP4 Animations |
| Backend      | Django (Python)                   |
| Hardware     | Arduino / Raspberry Pi            |
| Payments     | Razorpay (Test Mode)              |
| Database     | Django ORM (SQLite / PostgreSQL)  |
| Hosting      | PythonAnywhere / Local Server     |

---


---

## 🛠️ How It Works

1. **User scans QR code** on the screen
2. **Prescription is uploaded** to Google Drive and local storage
3. **Prescription is displayed** on the system screen
4. **User proceeds to payment**
5. **Payment is verified**
6. **Medicine is dispensed** automatically from mapped shelf
7. **Database is updated** with reduced stock

---

---

## 📦 Deployment

```bash
# Clone the repository
git clone https://github.com/your-username/medicliq.git
cd medicliq

# Install dependencies
pip install -r requirements.txt

# Run Django server
python manage.py runserver

🧪 Test Mode (Payment)
Razorpay test mode enabled
Mock transactions supported
Backend updates only after payment success




🙏 Acknowledgements
Django Community
Razorpay Documentation
Mechanical & IT Departments Collaboration

Made with 💡 and 💻 by Team Austra
Rajas Nandgaonkar,Utkarsh Agrawal,Kshamita Mane, Atharv Andhare  (Information Technology).
Pratham Palekar, Sahil Sondkar, Borhade Atharva, Mahesh Akim  (Mechanical) 
Guides:
Dr. Manmohan Bhoomkar & Prof.Shubhangi Deshpande 
