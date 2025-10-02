document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.getElementById('evaluationForm');
    const submitBtn = document.getElementById('submitBtn');
    const buttonText = document.getElementById('buttonText');
    const buttonSpinner = document.getElementById('buttonSpinner');
    
    // Step navigation
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    
    // Buttons
    const nextBtn1 = document.getElementById('nextBtn1');
    const nextBtn2 = document.getElementById('nextBtn2');
    const nextBtn3 = document.getElementById('nextBtn3');
    const backBtn1 = document.getElementById('backBtn1');
    const backBtn2 = document.getElementById('backBtn2');
    const backBtn3 = document.getElementById('backBtn3');
    
    // File inputs
    const referenceFileInput = document.getElementById('reference_file');
    const testFileInput = document.getElementById('test_file');
    const apiKeyInput = document.getElementById('api_key');
    const modelSelect = document.getElementById('model');

    // Initialize button states
    nextBtn1.disabled = true;
    nextBtn2.disabled = true;

    // Handle reference file selection
    referenceFileInput.addEventListener('change', function() {
      nextBtn1.disabled = !(this.files && this.files.length > 0);
    });
  
    // Handle test file selection
    testFileInput.addEventListener('change', function() {
      nextBtn2.disabled = !(this.files && this.files.length > 0);
    });
  
    // Navigation between steps
    nextBtn1.addEventListener('click', function() {
      step1.classList.add('hidden');
      step2.classList.remove('hidden');
    });
  
    nextBtn2.addEventListener('click', function() {
      step2.classList.add('hidden');
      step3.classList.remove('hidden');
    });

    nextBtn3.addEventListener('click', function() {
        step3.classList.add('hidden');
        step4.classList.remove('hidden');
    });

    backBtn1.addEventListener('click', function() {
      step2.classList.add('hidden');
      step1.classList.remove('hidden');
    });
  
    backBtn2.addEventListener('click', function() {
      step3.classList.add('hidden');
      step2.classList.remove('hidden');
    });

    backBtn3.addEventListener('click', function() {
        step4.classList.add('hidden');
        step3.classList.remove('hidden');
    });

    // Form submission with loading state
    form.addEventListener('submit', function(e) {
      // Basic validation
      if (!referenceFileInput.files || referenceFileInput.files.length === 0) {
        e.preventDefault();
        alert('Please select a reference file first');
        step4.classList.add('hidden');
        step3.classList.add('hidden');
        step2.classList.add('hidden');
        step1.classList.remove('hidden');
        return;
      }
      
      if (!testFileInput.files || testFileInput.files.length === 0) {
        e.preventDefault();
        alert('Please select a test file');
        step4.classList.add('hidden');
        step3.classList.add('hidden');
        step2.classList.remove('hidden');
        step1.classList.add('hidden');
        return;
      }
  
      if (!apiKeyInput.value) {
        e.preventDefault();
        alert('Please enter your API key');
        step4.classList.add('hidden');
        step3.classList.remove('hidden');
        step2.classList.add('hidden');
        step1.classList.add('hidden');
        return;
      }

      if (!modelSelect.value) {
        e.preventDefault();
        alert('Please select a model');
        step4.classList.add('hidden');
        step3.classList.remove('hidden');
        step2.classList.add('hidden');
        step1.classList.add('hidden');
        return;
      }
  
      // Show loading state
      buttonText.classList.add('hidden');
      buttonSpinner.classList.remove('hidden');
      submitBtn.disabled = true;
    });
  });