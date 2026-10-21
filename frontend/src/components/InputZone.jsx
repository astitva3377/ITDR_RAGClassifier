import React, { useState } from 'react';

export default function InputZone({ onAnalyze, setLoading }) {
  const [activeTab, setActiveTab] = useState('text');
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    // Placeholder handler
    setTimeout(() => {
      setLoading(false);
      onAnalyze({
        attack_ttps: [
          { id: 'T1059.001', name: 'PowerShell', tactic: 'Execution', confidence: 'High', evidence: 'Adversary executed base64 encoded PowerShell commands.' },
          { id: 'T1566.001', name: 'Spearphishing Attachment', tactic: 'Initial Access', confidence: 'High', evidence: 'Malicious macro-enabled Excel document received via email.' }
        ],
        d3fend_defenses: [
          { id: 'D3-PSA', name: 'Process Spawn Analysis', tactic: 'Detect', counters_attack: 'T1059.001', rationale: 'Inspect suspicious child processes spawned from PowerShell.' },
          { id: 'D3-EAM', name: 'Executable Allow Listing', tactic: 'Isolate', counters_attack: 'T1059.001', rationale: 'Enforce Constrained Language Mode and signed scripts.' }
        ]
      });
    }, 1000);
  };

  return (
    <div className="bg-[#111726] border border-[#1f293d] rounded-xl p-6 shadow-xl">
      <div className="flex gap-4 border-b border-[#1f293d] pb-3 mb-4">
        <button
          onClick={() => setActiveTab('text')}
          className={`text-sm font-semibold pb-1 ${activeTab === 'text' ? 'text-[#00ffb2] border-b-2 border-[#00ffb2]' : 'text-slate-400'}`}
        >
          Raw Text / Markdown
        </button>
        <button
          onClick={() => setActiveTab('url')}
          className={`text-sm font-semibold pb-1 ${activeTab === 'url' ? 'text-[#00ffb2] border-b-2 border-[#00ffb2]' : 'text-slate-400'}`}
        >
          Advisory URL
        </button>
        <button
          onClick={() => setActiveTab('file')}
          className={`text-sm font-semibold pb-1 ${activeTab === 'file' ? 'text-[#00ffb2] border-b-2 border-[#00ffb2]' : 'text-slate-400'}`}
        >
          Upload PDF / TXT
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {activeTab === 'text' && (
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            placeholder="Paste cyber threat advisory, malware analysis, or incident notes here..."
            className="w-full bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3 text-sm focus:outline-none focus:border-[#00ffb2] text-slate-200"
          />
        )}
        {activeTab === 'url' && (
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-..."
            className="w-full bg-[#0a0d14] border border-[#1f293d] rounded-lg p-3 text-sm focus:outline-none focus:border-[#00ffb2] text-slate-200"
          />
        )}
        {activeTab === 'file' && (
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-[#1f293d] file:text-slate-200 hover:file:bg-[#28354f]"
          />
        )}

        <button
          type="submit"
          className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 font-bold hover:brightness-110 transition shadow-lg shadow-teal-500/20"
        >
          Run GraphRAG Analysis
        </button>
      </form>
    </div>
  );
}
