from django.shortcuts import render
from django.http import JsonResponse
import razorpay
from medicliq_database.models import Payment
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

import json
from django.shortcuts import render
import os
from medicliq_database.models import MedShelfMapper

import serial
import time
import threading
from threading import Thread
from django.urls import reverse



# Function to run a motor for the given count of times
def run_motor(arduino, motor, count):
    for i in range(count):
        if motor in ['1', '2', '3', '4', '5', '6', '7']:
            arduino.write(motor.encode())  # Send the motor command to Arduino
            print(f"Motor {motor} running {i+1} time on {arduino.portstr}...")
            time.sleep(1)  # Run the motor for 1 second (or desired time)
            arduino.write(b'R')  # Stop the motor after each run
            print(f"Motor {motor} stopped after {i+1} run.")
            time.sleep(0.5)  # Pause between runs
        else:
            print(f"Invalid motor number: {motor}. Please use '1', '2', '3', '4', '5', '6', or '7'.")

# Function to run motors for the specified counts
def run_motors_with_counts(arduino1, arduino2, motor_counts):
    # Initial round where all motors will run at least once
    while motor_counts:
        threads = []
        remaining_motors = []

        # Add motors to be run this round, and decrement the count for each motor
        for motor, count in motor_counts.items():
            if count > 0:
                # Deciding which Arduino to send the motor to
                if motor in ['1', '2', '3', '4']:
                    threads.append(threading.Thread(target=run_motor, args=(arduino1, motor, 1)))
                elif motor in ['5', '6', '7']:
                    threads.append(threading.Thread(target=run_motor, args=(arduino2, motor, 1)))
                remaining_motors.append((motor, count - 1))  # Decrement the count after this round

        # Start the threads
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Update the motor_counts for the next round
        motor_counts = {motor: count for motor, count in remaining_motors if count > 0}
        print(f"Remaining motor counts: {motor_counts}")

        time.sleep(0.5)  # Pause before next round

def control_motor(port1='/dev/ttyACM0', port2='/dev/ttyACM1', baud_rate=9600, motor_counts=None):
    if motor_counts is None:
        motor_counts = {'1': 1, '3': 2, '5': 3, '7': 4}  # Default counts as specified

    # Set up the serial connection to both Arduinos
    arduino1 = serial.Serial(port1, baud_rate)
    arduino2 = serial.Serial(port2, baud_rate)
    time.sleep(2)  # Wait for the connection to establish

    print(f"Connected to Arduino 1 on {port1} and Arduino 2 on {port2}")

    # Run motors based on the provided motor counts
    run_motors_with_counts(arduino1, arduino2, motor_counts)

    # Stop all motors by sending the 'R' command to both Arduinos
    arduino1.write(b'R')
    arduino2.write(b'R')
    print("All motors stopped.")

    # Close the serial connections after use
    arduino1.close()
    arduino2.close()


def convert_and_save_medicine_data(input_file_path, output_file_path):
    # Step 1: Read input dictionary from file (assuming JSON-like input)
    import json
    with open(input_file_path, 'r') as infile:
        medicine_data = json.load(infile)

    converted_data = {}

    # Step 2: Convert medicine names to shelf numbers
    for med_name, quantity in medicine_data.items():
        try:
            shelf = MedShelfMapper.objects.get(medname=med_name)
            converted_data[str(shelf.shelfno)] = quantity
        except MedShelfMapper.DoesNotExist:
            print(f"Medicine '{med_name}' not found in MedShelfMapper.")
            continue

    # Step 3: Save output in Python dict format (NOT JSON)
    with open(output_file_path, 'w') as outfile:
        outfile.write(str(converted_data))  # Writing as string

    print(f"Conversion complete! Output saved to {output_file_path}")
    return converted_data



def build_motor_dictionary(cart_data):
    """Helper function to build {medname: quantity} dictionary."""
    return {item['name']: item['quantity'] for item in cart_data}

@csrf_exempt  # Disable CSRF for testing (only if necessary)
def cart2(request):
    if request.method == "POST":
        try:
            # Get the cart data from the POST request sent by the JS code
            data = json.loads(request.body)
            cart_data = data.get("cart_data", [])

            # Update Django session with the posted cart data
            request.session["cart_data"] = json.dumps(cart_data)
            request.session.modified = True

            # Build the medicine dictionary from the latest cart data
            medicine_dict = {item["name"]: item["quantity"] for item in cart_data}

            # Save the dictionary as a text file (overwrite every time)
            file_path = os.path.join(settings.MEDIA_ROOT, "medicine_data.txt")
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(medicine_dict, f, indent=4)

            # Debug prints in the terminal
            print(f"✅ Updated Medicine Dictionary: {medicine_dict}")
            print(f"🔹 Final Session Data: {request.session.get('cart_data')}")
            return JsonResponse({"message": "Cart updated", "cart_data": cart_data})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        # For GET requests, use the session data (if any) to render the page
        cart_data = json.loads(request.session.get("cart_data", "[]"))
        total = sum(item["price"] * item["quantity"] for item in cart_data)
        return render(request, "cart2.html", {
            "cart_data": cart_data,
            "total_amount": total,
            "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID
        })

    

def log_cart_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Receive JSON data
            print("Received Cart Data:", data)  # Print in Django terminal
            return JsonResponse({"status": "success", "message": "Data logged"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
    

@csrf_exempt
def create_razorpay_order(request):
    if request.method == "POST":
        try:
            # Parse and validate request data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            if 'amount' not in data:
                return JsonResponse({"error": "Amount is required"}, status=400)

            try:
                amount = float(data['amount'])
            except (ValueError, TypeError):
                return JsonResponse({"error": "Invalid amount format"}, status=400)

            # Convert to paise and validate
            amount_paise = int(amount)  # Convert rupees to paise
            if amount_paise < 100:
                return JsonResponse({"error": "Minimum amount is ₹1"}, status=400)

            # Create Razorpay order
            order = client.order.create({
                "amount": amount_paise*100,
                "currency": "INR",
                "payment_capture": 1
            })

            # Save payment record
            Payment.objects.create(
                razorpay_order_id=order['id'],
                amount_paid=amount,
                payment_method="Razorpay",
                # cart_data=data.get('items', [])
            )

            return JsonResponse({
                "razorpay_order_id": order['id'],
                "amount": order['amount'],
                "currency": order['currency']
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def payment_status(request):
    if request.method == "POST":
        try:
            params = {
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': request.POST.get('razorpay_signature')
            }

            # Verify payment signature
            client.utility.verify_payment_signature(params)

            # Update payment record
            payment = Payment.objects.get(razorpay_order_id=params['razorpay_order_id'])
            payment.razorpay_payment_id = params['razorpay_payment_id']
            payment.ispaid = True
            payment.save()

            # Clear session cart
            if 'cart' in request.session:
                del request.session['cart']

            return JsonResponse({"success": True})

        except Payment.DoesNotExist:
            return JsonResponse({"success": False, "error": "Payment record not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


from medicliq_database.models import tentrans  # update path if needed

from django.db import transaction

from django.db.models import F
def payment_success(request):
    # Get the latest payment
    try:
        payment = Payment.objects.latest('payment_date_time')
    except Payment.DoesNotExist:
        payment = None

    # Get initial latest 10 entries
    latest_entries = tentrans.objects.all().order_by('-time_date')[:10]

    # Render the page immediately
    response = render(request, 'payment_success.html', {
        'payment': payment,
        'status': True if payment else False,
        'entries_1_to_10': latest_entries,
    })

    # Background task with enhanced debugging
    def background_task():
        try:
            # 1. Read and parse medicine data with validation
            try:
                with open('/home/utkagrawal/checkpoint5/src/temp/medicine_updated_data.txt', 'r') as file:
                    content = file.read().strip()
                    print(f"Raw file content: {content}")  # Debug

                    # Handle both JSON and Python dict formats
                    try:
                        medicine_data = json.loads(content)
                    except json.JSONDecodeError:
                        medicine_data = json.loads(content.replace("'", '"'))
                    
                    print(f"Validated medicine data: {medicine_data}")  # Debug

            except Exception as e:
                print(f"Error reading medicine data: {str(e)}")
                return

            # 2. Get latest payment for transaction record
            try:
                latest_payment = Payment.objects.latest('payment_date_time')
            except Payment.DoesNotExist:
                print("No payment found - skipping tentrans creation")
                latest_payment = None

            # 3. Process updates in single atomic transaction
            with transaction.atomic():
                # Update shelf quantities with strict type checking
                for shelf_no_str, quantity in medicine_data.items():
                    try:
                        shelf_no = int(shelf_no_str)
                        quantity = int(quantity)
                        
                        shelf = MedShelfMapper.objects.get(shelfno=shelf_no)
                        print(f"Updating shelf {shelf_no}: {shelf.avail_quantity} -> {shelf.avail_quantity - quantity}")  # Debug
                        
                        shelf.avail_quantity = F('avail_quantity') - quantity
                        shelf.save()
                        
                    except (MedShelfMapper.DoesNotExist, ValueError) as e:
                        print(f"Skipping shelf {shelf_no_str}: {str(e)}")
                        continue

                # Create transaction record if payment exists
                if latest_payment:
                    try:
                        # Get current quantities using bulk query for efficiency
                        shelves = MedShelfMapper.objects.filter(shelfno__in=range(1, 9))
                        shelf_data = {s.shelfno: s.avail_quantity for s in shelves}
                        
                        # Create new tentrans record with precise values
                        tentrans.objects.create(
                            payment_id=latest_payment.razorpay_order_id,
                            amount=latest_payment.amount_paid,
                            time_date=latest_payment.payment_date_time,
                            medastock=shelf_data.get(1, 0),
                            medbstock=shelf_data.get(2, 0),
                            medcstock=shelf_data.get(3, 0),
                            meddstock=shelf_data.get(4, 0),
                            medestock=shelf_data.get(5, 0),
                            medfstock=shelf_data.get(6, 0),
                            medgstock=shelf_data.get(7, 0),
                            medhstock=shelf_data.get(8, 0)
                        )
                        print("Successfully created transaction record")

                    except Exception as e:
                        print(f"Transaction record creation failed: {str(e)}")

            # 4. Execute motor control after successful updates
            try:
                data = convert_and_save_medicine_data(
                    '/home/utkagrawal/checkpoint5/src/temp/medicine_data.txt',
                    '/home/utkagrawal/checkpoint5/src/temp/medicine_updated_data.txt'
                )
                control_motor('/dev/ttyACM0', '/dev/ttyACM1', motor_counts=data)
                print("Motor control executed successfully")
                
            except Exception as e:
                print(f"Motor control error: {str(e)}")

        except Exception as e:
            print(f"Background task failed: {str(e)}")

    # Start background processing
    Thread(target=background_task).start()
    return response