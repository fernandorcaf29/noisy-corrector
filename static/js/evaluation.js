document.addEventListener('DOMContentLoaded', () => {
  const diffContainer = document.getElementById('diff-container');
  const referenceContainer = document.getElementById('reference-container');
  const resultsList = document.getElementById('resultsList');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const pageInfo = document.getElementById('page-info');
  const downloadBtn = document.getElementById('download-btn');

  let currentPage = 0;
  let isUpdating = false;

  const showCurrentPage = () => {
    if (!diffContainer || !referenceContainer || !resultsList) return;

    if (!currentRedlines || currentRedlines.length === 0) {
      diffContainer.innerHTML =
        '<div class="text-gray-500 text-center py-8">No text to display.</div>';
      referenceContainer.innerHTML = '';
      resultsList.innerHTML = '';
      return;
    }

    const index = Math.max(0, Math.min(currentPage, currentRedlines.length - 1));

    // Review / Diff
    const redline = currentRedlines[index];
    diffContainer.innerHTML = `
      <div class="prose">
        <div class="p-2 bg-white rounded border border-gray-200 h-[200px] overflow-y-auto">
          ${marked.parse(redline.markdown_diff || '')}
        </div>
      </div>
    `;

    // Reference
    const referenceLine = referenceLines?.[index] || '';
    referenceContainer.innerHTML = `
      <div class="prose">
        <div class="p-2 bg-white rounded border border-gray-200 h-[200px] overflow-y-auto">
          ${marked.parse(referenceLine)}
        </div>
      </div>
    `;

    const result = metrics?.[index] || null;
    if (result) {
      resultsList.innerHTML = `
        <div class="border rounded-lg p-4 mb-4 ${result.error ? 'bg-red-50 border-red-200' : 'bg-white'}">
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="text-center p-2 bg-gray-50 rounded">
              <div class="font-semibold">Score semântico</div>
              <div class="text-2xl font-bold ${result.bleu_diff > 0 ? 'text-green-600' : 'text-red-600'}">
                ${result.bleu_corrected.toFixed(1)}%
              </div>
              <div class="text-xs text-gray-600">
                ${result.bleu_original.toFixed(1)}% → 
                <span class="${result.bleu_diff > 0 ? 'text-green-600' : 'text-red-600'}">
                  ${result.bleu_diff > 0 ? '+' : ''}${result.bleu_diff.toFixed(1)}%
                </span>
              </div>
            </div>
            <div class="text-center p-2 bg-gray-50 rounded">
              <div class="font-semibold">Score léxico</div>
              <div class="text-2xl font-bold ${result.bert_diff > 0 ? 'text-green-600' : 'text-red-600'}">
                ${result.bert_corrected.toFixed(1)}%
              </div>
              <div class="text-xs text-gray-600">
                ${result.bert_original.toFixed(1)}% → 
                <span class="${result.bert_diff > 0 ? 'text-green-600' : 'text-red-600'}">
                  ${result.bert_diff > 0 ? '+' : ''}${result.bert_diff.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      `;
    } else {
      resultsList.innerHTML = '';
    }

    // Scroll automático
    diffContainer.scrollTo?.({ top: 0, behavior: 'smooth' });
    referenceContainer.scrollTo?.({ top: 0, behavior: 'smooth' });
  };

  const updatePagination = () => {
    if (isUpdating) return;
    isUpdating = true;

    try {
      if (!pageInfo || !currentRedlines) return;

      const totalPages = Math.max(1, currentRedlines.length);
      currentPage = Math.min(currentPage, totalPages - 1);

      pageInfo.textContent = `${currentPage + 1}/${totalPages}`;
      prevBtn.disabled = currentPage <= 0;
      nextBtn.disabled = currentPage >= totalPages - 1;

      showCurrentPage();
    } catch (error) {
      console.error('Error in updatePagination:', error);
    } finally {
      isUpdating = false;
    }
  };

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
      const blob = new Blob([currentFileContent], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = currentFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  });

  updatePagination();
});
