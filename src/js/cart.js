document.addEventListener('DOMContentLoaded', () => {
    const cartList = document.querySelector('.cart-list');
    const totalAmountElement = document.getElementById('totalAmount');
    const cartCountElement = document.getElementById('cartCount');
  
    // Sample cart data (replace with actual data from your storage or API)
    const cartItems = [
      { name: 'Medicine A', price: 20, quantity: 2 },
      { name: 'Medicine C', price: 25, quantity: 1 },
      // Add more items as needed
    ];
  
    function renderCartItems() {
      cartList.innerHTML = '';
      let totalAmount = 0;
  
      cartItems.forEach(item => {
        const cartItem = document.createElement('div');
        cartItem.classList.add('cart-item');
        
        const itemInfo = document.createElement('div');
        itemInfo.classList.add('cart-item-info');
        itemInfo.innerHTML = `
          <span class="cart-item-name">${item.name}</span>
          <span class="cart-item-price">$${item.price}</span>
        `;
        
        const quantityControls = document.createElement('div');
        quantityControls.classList.add('quantity-controls');
        quantityControls.innerHTML = `
          <button class="quantity-decrease">-</button>
          <input type="number" class="quantity-input" value="${item.quantity}" min="0" />
          <button class="quantity-increase">+</button>
        `;
        
        quantityControls.querySelector('.quantity-decrease').addEventListener('click', () => {
          const input = quantityControls.querySelector('.quantity-input');
          let quantity = parseInt(input.value);
          if (quantity > 0) {
            quantity--;
            input.value = quantity;
            updateTotalAmount();
          }
        });
        
        quantityControls.querySelector('.quantity-increase').addEventListener('click', () => {
          const input = quantityControls.querySelector('.quantity-input');
          let quantity = parseInt(input.value);
          quantity++;
          input.value = quantity;
          updateTotalAmount();
        });
        
        cartItem.appendChild(itemInfo);
        cartItem.appendChild(quantityControls);
        cartList.appendChild(cartItem);
  
        totalAmount += item.price * item.quantity;
      });
  
      totalAmountElement.textContent = totalAmount.toFixed(2);
      cartCountElement.textContent = cartItems.length;
    }
  
    function updateTotalAmount() {
      let totalAmount = 0;
  
      cartItems.forEach(item => {
        const cartItemElement = [...cartList.children].find(element => 
          element.querySelector('.cart-item-name').textContent === item.name
        );
        
        const quantityInput = cartItemElement.querySelector('.quantity-input');
        const quantity = parseInt(quantityInput.value) || 0;
        
        totalAmount += item.price * quantity;
      });
  
      totalAmountElement.textContent = totalAmount.toFixed(2);
    }
  
    function proceedToCheckout() {
      alert('Proceeding to checkout!');
    }
  
    renderCartItems();
  });
  