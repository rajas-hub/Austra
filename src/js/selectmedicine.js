document.addEventListener('DOMContentLoaded', () => {
    const medicineItems = document.querySelectorAll('.medicine-item');
    const totalAmountElement = document.getElementById('totalAmount');
    const cartCountElement = document.getElementById('cartCount');
  
    medicineItems.forEach(item => {
      const quantityInput = item.querySelector('.quantity-input');
      const quantityDecrease = item.querySelector('.quantity-decrease');
      const quantityIncrease = item.querySelector('.quantity-increase');
      const availability = item.dataset.availability === 'yes';
  
      // Initialize quantity input state
      quantityInput.disabled = !availability;
      quantityDecrease.disabled = !availability;
      quantityIncrease.disabled = !availability;
  
      // Click event for medicine item
      item.addEventListener('click', () => {
        if (availability) {
          const checkbox = item.querySelector('input[type="checkbox"]');
          checkbox.checked = !checkbox.checked;
          updateTotalAmount();
        }
      });
  
      // Quantity change event handlers
      quantityDecrease.addEventListener('click', () => {
        if (parseInt(quantityInput.value) > 0) {
          quantityInput.value = parseInt(quantityInput.value) - 1;
          updateTotalAmount();
        }
      });
  
      quantityIncrease.addEventListener('click', () => {
        quantityInput.value = parseInt(quantityInput.value) + 1;
        updateTotalAmount();
      });
  
      quantityInput.addEventListener('input', updateTotalAmount);
    });
  
    function updateTotalAmount() {
      let totalAmount = 0;
      let cartCount = 0;
  
      medicineItems.forEach(item => {
        const quantityInput = item.querySelector('.quantity-input');
        const price = parseFloat(item.dataset.price);
        const quantity = parseInt(quantityInput.value) || 0;
        const checkbox = item.querySelector('input[type="checkbox"]');
  
        if (checkbox && checkbox.checked && !quantityInput.disabled && quantity > 0) {
          totalAmount += price * quantity;
          cartCount++;
        }
      });
  
      totalAmountElement.textContent = totalAmount.toFixed(2);
      cartCountElement.textContent = cartCount;
    }
  
    function submitOrder() {
      alert("Order submitted successfully!");
    }
  });
  