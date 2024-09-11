document.getElementById("glowButton").addEventListener("click", function() {
    this.classList.add("glow");

    // Delay navigation to the next page to allow the glow effect to be visible
    setTimeout(navigateToImage, 1000); // 1 second delay
});

function navigateToImage() {
    // Example navigation function, update this with your actual functionality
    window.location.href = "prescription_image.html"; // Replace with your target page
  }
  // Example of adding interactivity if needed
function navigateToNextStep() {
    // Example function for navigating to the next step or showing a message
    alert("Prescription scanning complete! Proceed to the next step.");
  }
  function goBack() {
    window.history.back();
}
