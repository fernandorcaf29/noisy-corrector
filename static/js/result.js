document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('correctionForm');
  const submitBtn = form?.querySelector('button[type="submit"]');
  const resultsSection = document.getElementById('results-section');
  const diffContainer = document.getElementById('diff-container');
  const downloadBtn = document.getElementById('download-btn');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const pageInfo = document.getElementById('page-info');

  if (!form || !submitBtn) return;

  const originalBtn = submitBtn.innerHTML;
  let isSubmitting = false;
  let currentFileContent = '';
  let currentFilename = '';
  let currentRedlines = [];
  let currentPage = 0;

  const setLoading = (isLoading) => {
    isSubmitting = isLoading;
    submitBtn.disabled = isLoading;
    submitBtn.innerHTML = isLoading
      ? `
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
               xmlns="http://www.w3.org/2000/svg" fill="none"
               viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10"
                    stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0
                     5.373 0 12h4zm2 5.291A7.962 7.962
                     0 014 12H0c0 3.042 1.135 5.824
                     3 7.938l3-2.647z"></path>
          </svg>
          Processing...
        `
      : originalBtn;
  };

  let isUpdating = false;

  const updatePagination = () => {
    if (isUpdating) return;
    isUpdating = true;

    try {
      if (!pageInfo || !currentRedlines) return;

      const totalPages = Math.max(1, currentRedlines.length);
      const currentPageNumber = Math.min(currentPage, totalPages - 1);

      if (currentPage !== currentPageNumber) {
        currentPage = currentPageNumber;
      }

      pageInfo.textContent = `${currentPage + 1}/${totalPages}`;

      if (prevBtn) prevBtn.disabled = currentPage <= 0;
      if (nextBtn) nextBtn.disabled = currentPage >= totalPages - 1;

      showCurrentPage();
    } catch (error) {
      console.error('Error in updatePagination:', error);
    } finally {
      isUpdating = false;
    }
  };

  const showCurrentPage = () => {
    if (!diffContainer) return;

    if (!currentRedlines || currentRedlines.length === 0) {
      diffContainer.innerHTML =
        '<div class="text-gray-500 text-center py-8">No text to display.</div>';
      return;
    }

    currentPage = Math.max(
      0,
      Math.min(currentPage, currentRedlines.length - 1),
    );
    const redline = currentRedlines[currentPage];
    if (!redline) return;

    try {
      const content = `
              <div class="prose ">
                </h3>
                <div class="p-2 bg-white rounded border border-gray-200 max-w-none h-[200px] overflow-y-auto">
                  ${marked.parse(redline.markdown_diff || '')}
                </div>
              </div>
            `;
      diffContainer.innerHTML = content;
    } catch (error) {
      console.error('Error rendering content:', error);
      diffContainer.innerHTML = `
            <div class="prose max-w-none">
              <div class="p-2 bg-white rounded border border-gray-200 max-w-none h-[200px] overflow-y-auto">
                <p>Error displaying content. The corrected text has been downloaded.</p>
              </div>
            </div>
          `;
    }

    if (diffContainer.scrollTo) {
      diffContainer.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      diffContainer.scrollTop = 0;
    }
  };

  const downloadFile = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  form.addEventListener('submit', async (e) => {
    if (isSubmitting) return;
    e.preventDefault();
    setLoading(true);
    if (resultsSection) resultsSection.classList.add('hidden');

    currentRedlines = [];
    currentPage = 0;

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: new FormData(form),
      });

      if (!response.ok) throw new Error('Network error');
      const data = await response.json();

      if (data.status === 'success') {
        currentFileContent = data.file_content;
        currentFilename = data.filename;
        currentRedlines = data.redlines;
        currentPage = 0;

        form.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        updatePagination();
        showCurrentPage();
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to process file. Please try again.');
    } finally {
      setLoading(false);
    }
  });

  prevBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentPage > 0) {
      currentPage--;
      updatePagination();
    }
  });

  nextBtn?.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentPage < currentRedlines.length - 1) {
      currentPage++;
      updatePagination();
    }
  });

  downloadBtn?.addEventListener('click', () => {
    if (currentFileContent && currentFilename) {
      downloadFile(currentFileContent, currentFilename);
    }
  });
});
