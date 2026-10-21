import React from 'react';

export default function ExportBar({ data }) {
  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `threat-rag-analysis-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="flex justify-between items-center bg-[#111726] border border-[#1f293d] rounded-xl px-5 py-3">
      <span className="text-xs text-slate-400">Analysis Complete</span>
      <button
        onClick={downloadJSON}
        className="text-xs px-3 py-1.5 rounded bg-[#1f293d] hover:bg-[#28354f] text-slate-200 transition font-mono"
      >
        Export JSON Report
      </button>
    </div>
  );
}
