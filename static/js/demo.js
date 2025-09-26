document.addEventListener('DOMContentLoaded', function() {
    const demoBtn = document.getElementById('demoBtn');
    const demoButtonText = document.getElementById('demoButtonText');
    const demoButtonSpinner = document.getElementById('demoButtonSpinner');

    if (demoBtn) {
        demoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            demoButtonText.classList.add('hidden');
            demoButtonSpinner.classList.remove('hidden');
            demoBtn.disabled = true;
            
            window.location.href = demoBtn.dataset.demoUrl || "/demo";
        });
    }
});