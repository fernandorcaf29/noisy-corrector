document.querySelector('form').addEventListener('submit', function (e) {
  const submitBtn = document.getElementById('submitBtn');
  const buttonText = document.getElementById('buttonText');
  const buttonSpinner = document.getElementById('buttonSpinner');

  submitBtn.disabled = true;
  buttonText.classList.add('hidden');
  buttonSpinner.classList.remove('hidden');
});

document.addEventListener('DOMContentLoaded', function() {
  const documentInput = document.getElementById('document');
  const nextBtn = document.getElementById('nextBtn');
  const backBtn = document.getElementById('backBtn');
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const form = document.getElementById('correctionForm');
  const submitBtn = document.getElementById('submitBtn');
  const modelSelect = document.getElementById('model');
  const apiKeyInput = document.getElementById('api_key');

  documentInput.addEventListener('change', function() {
    if (this.files && this.files.length > 0) {
      nextBtn.disabled = false;
    } else {
      nextBtn.disabled = true;
    }
  });

  nextBtn.addEventListener('click', function() {
    step1.classList.add('hidden');
    step2.classList.remove('hidden');
  });

  backBtn.addEventListener('click', function() {
    step2.classList.add('hidden');
    step1.classList.remove('hidden');
  });

  form.addEventListener('submit', function(e) {
    if (!documentInput.files || documentInput.files.length === 0) {
      e.preventDefault();
      alert('Please select a file first');
      step2.classList.add('hidden');
      step1.classList.remove('hidden');
    } else if (!modelSelect.value) {
      e.preventDefault();
      alert('Please select a model');
    } else if (!apiKeyInput.value) {
      e.preventDefault();
      alert('Please enter your API key');
    } else {

      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
      `;
    }
  });
});