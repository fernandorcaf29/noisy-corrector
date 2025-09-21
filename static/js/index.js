document.querySelector('form').addEventListener('submit', function (e) {
  const submitBtn = document.getElementById('submitBtn');
  const buttonText = document.getElementById('buttonText');
  const buttonSpinner = document.getElementById('buttonSpinner');

  submitBtn.disabled = true;
  buttonText.classList.add('hidden');
  buttonSpinner.classList.remove('hidden');
});
