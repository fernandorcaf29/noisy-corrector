document.addEventListener('DOMContentLoaded', () => {
  const diffContainer = document.getElementById('diff-container');
  const downloadBtn = document.getElementById('download-btn');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const pageInfo = document.getElementById('page-info');

  let currentPage = 0;

  let isUpdating = false;

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
              <div class="prose">
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

  showCurrentPage();

  updatePagination();

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
