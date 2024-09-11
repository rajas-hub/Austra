document.addEventListener('DOMContentLoaded', () => {
    const orderDetailsElement = document.getElementById('orderDetails');
    const totalAmountElement = document.getElementById('totalAmount');
    const cartCountElement = document.getElementById('cartCount');
    const paymentForm = document.getElementById('paymentForm');
    const cardDetails = document.getElementById('cardDetails');
  
    // Sample cart data (replace with actual data from your storage or API)
    const cartItems = [
      { name: 'Medicine A', price: 20, quantity: 2 },
      { name: 'Medicine C', price: 25, quantity: 1 },
      // Add more items as needed
    ];
  
    function renderOrderSummary() {
      let totalAmount = 0;
      orderDetailsElement.innerHTML = '';
  
      cartItems.forEach(item => {
        const itemDetail = document.createElement('div');
        itemDetail.classList.add('order-item');
        itemDetail.innerHTML = `
          <span>${item.name} - $${item.price} x ${item.quantity}</span>
        `;
        orderDetailsElement.appendChild(itemDetail);
  
        totalAmount += item.price * item.quantity;
      });
  
      totalAmountElement.textContent = totalAmount.toFixed(2);
      cartCountElement.textContent = cartItems.length;
    }
  
    function handlePaymentMethodChange() {
      const selectedPaymentMethod = [...paymentForm.elements]
        .find(element => element.checked)
        ?.value;
  
      if (selectedPaymentMethod === 'creditCard') {
        cardDetails.style.display = 'block';
      } else {
        cardDetails.style.display = 'none';
      }
    }
  
    function submitOrder() {
      const selectedPaymentMethod = [...paymentForm.elements]
        .find(element => element.checked)
        ?.value;
  
      if (!selectedPaymentMethod) {
        alert('Please select a payment method.');
        return;
      }
  
      if (selectedPaymentMethod === 'creditCard') {
        const cardNumber = document.getElementById('cardNumber').value;
        const expiryDate = document.getElementById('expiryDate').value;
        const cvv = document.getElementById('cvv').value;
  
        if (!cardNumber || !expiryDate || !cvv) {
          alert('Please fill out all card details.');
          return;
        }
      }
  
      // Handle order submission (e.g., send data to server)
      console.log('Order submitted with payment method:', selectedPaymentMethod);
  
      // Generate PDF and send email (this would be done server-side)
      alert('Your order has been placed. A confirmation email with the receipt will be sent to you.');
    }
  
    renderOrderSummary();
  
    // Add event listener for payment method changes
    [...paymentForm.elements].forEach(element => {
      if (element.type === 'radio') {
        element.addEventListener('change', handlePaymentMethodChange);
      }
    });
  });
  