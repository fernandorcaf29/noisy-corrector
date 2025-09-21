let metricsChart = null;
document.addEventListener('DOMContentLoaded', () => {
  const diffContainer = document.getElementById('diff-container');
  const referenceContainer = document.getElementById('reference-container');
  const resultsList = document.getElementById('resultsList');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const pageInfo = document.getElementById('page-info');
  const showSummaryBtn = document.getElementById('show-summary-btn');
  const summaryModal = document.getElementById('summary-modal');
  const closeSummaryBtn = document.getElementById('close-summary-btn');
  const summaryStats = document.getElementById('summaryStats');

  let currentPage = 0;
  let isUpdating = false;

  const showCurrentPage = () => {
    if (!diffContainer || !referenceContainer || !resultsList) return;

    if (!currentRedlines || currentRedlines.length === 0) {
      diffContainer.innerHTML = '<div class="text-gray-500 text-center py-8">No text to display.</div>';
      referenceContainer.innerHTML = '';
      resultsList.innerHTML = '';
      return;
    }

    const index = Math.max(0, Math.min(currentPage, currentRedlines.length - 1));
    const redline = currentRedlines[index];
    diffContainer.innerHTML = `<div class="prose"><div class="p-2 bg-white rounded border border-gray-200 h-[200px] overflow-y-auto">${marked.parse(redline.markdown_diff || '')}</div></div>`;

    const referenceLine = referenceLines?.[index] || '';
    referenceContainer.innerHTML = `<div class="prose"><div class="p-2 bg-white rounded border border-gray-200 h-[200px] overflow-y-auto">${marked.parse(referenceLine)}</div></div>`;

    const result = metrics?.[index] || null;
    if (result) {
      resultsList.innerHTML = `<div class="border rounded-lg p-4 mb-4 ${result.error ? 'bg-red-50 border-red-200' : 'bg-white'}">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="text-center p-2 bg-gray-50 rounded">
            <div class="font-semibold">Semantic Score</div>
            <div class="text-2xl font-bold ${result.bleu_diff > 0 ? 'text-green-600' : 'text-red-600'}">${result.bleu_corrected.toFixed(1)}%</div>
            <div class="text-xs text-gray-600">${result.bleu_original.toFixed(1)}% → <span class="${result.bleu_diff > 0 ? 'text-green-600' : 'text-red-600'}">${result.bleu_diff > 0 ? '+' : ''}${result.bleu_diff.toFixed(1)}%</span></div>
          </div>
          <div class="text-center p-2 bg-gray-50 rounded">
            <div class="font-semibold">Lexic Score</div>
            <div class="text-2xl font-bold ${result.bert_diff > 0 ? 'text-green-600' : 'text-red-600'}">${result.bert_corrected.toFixed(1)}%</div>
            <div class="text-xs text-gray-600">${result.bert_original.toFixed(1)}% → <span class="${result.bert_diff > 0 ? 'text-green-600' : 'text-red-600'}">${result.bert_diff > 0 ? '+' : ''}${result.bert_diff.toFixed(1)}%</span></div>
          </div>
        </div>
      </div>`;
    } else resultsList.innerHTML = '';

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
    } finally { isUpdating = false; }
  };

  prevBtn?.addEventListener('click', e => { e.preventDefault(); if (currentPage>0) {currentPage--; updatePagination();} });
  nextBtn?.addEventListener('click', e => { e.preventDefault(); if (currentPage<currentRedlines.length-1){currentPage++;updatePagination();} });

  showSummaryBtn?.addEventListener('click', () => { displaySummary(); summaryModal.classList.remove('hidden'); });
  closeSummaryBtn?.addEventListener('click', () => summaryModal.classList.add('hidden'));

  const displaySummary = () => {
    const totalLines = metrics.length;
    const avg_bleu_improvement = Math.round(metrics.reduce((a,m)=>a+(m.bleu_diff||0),0) /totalLines * 100) / 100;
    const avg_bert_improvement = Math.round(metrics.reduce((a,m)=>a+(m.bert_diff||0),0) / totalLines * 100) / 100;

    const avg_bleu_original = Math.round(metrics.reduce((a,m)=>a+(m.bleu_original||0),0) / totalLines * 100) / 100;
    const avg_bert_original = Math.round(metrics.reduce((a,m)=>a+(m.bert_original||0),0) / totalLines * 100) / 100;
    const avg_bleu_corrected = Math.round(metrics.reduce((a,m)=>a+(m.bleu_corrected||0),0) / totalLines * 100) / 100;
    const avg_bert_corrected = Math.round(metrics.reduce((a,m)=>a+(m.bert_corrected||0),0) / totalLines * 100) / 100;


    summaryStats.innerHTML = `
      <div class="text-center p-4 bg-blue-50 rounded-lg">
        <div class="text-2xl font-bold text-blue-600">${avg_bleu_corrected}</div>
        <div class="text-sm text-blue-800">Semantic Score</div>
      </div>
      <div class="text-center p-4 bg-green-50 rounded-lg">
        <div class="text-2xl font-bold text-green-600">${avg_bert_corrected}</div>
        <div class="text-sm text-green-800">Lexic Score</div>
      </div>
      <div class="text-center p-4 bg-purple-50 rounded-lg">
        <div class="text-2xl font-bold text-purple-600">${avg_bleu_improvement.toFixed(2)}%</div>
        <div class="text-sm text-purple-800">Semantic Improvement</div>
      </div>
      <div class="text-center p-4 bg-orange-50 rounded-lg">
        <div class="text-2xl font-bold text-orange-600">${avg_bert_improvement.toFixed(2)}%</div>
        <div class="text-sm text-orange-800">Lexic Improvement</div>
      </div>
    `;
    createChart({avg_bleu_original, avg_bert_original, avg_bleu_corrected, avg_bert_corrected});
  };

  const createChart = (summary) => {
    const ctx = document.getElementById('metricsChart').getContext('2d');
    if (metricsChart) metricsChart.destroy();
    metricsChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['BLEU Score', 'BERT Score'],
        datasets: [
          { label:'Before Correction', data:[summary.avg_bleu_original, summary.avg_bert_original], backgroundColor:'rgba(239,68,68,0.7)', borderColor:'rgba(239,68,68,1)', borderWidth:1 },
          { label:'After Correction', data:[summary.avg_bleu_corrected, summary.avg_bert_corrected], backgroundColor:'rgba(34,197,94,0.7)', borderColor:'rgba(34,197,94,1)', borderWidth:1 }
        ]
      },
      options: { responsive:true, scales:{y:{beginAtZero:true, max:100, title:{display:true,text:'Score (%)'}}}, plugins:{legend:{position:'top'}, title:{display:true,text:'Comparison of Metrics Before and After Correction'}} }
    });
  };

  updatePagination();
});
