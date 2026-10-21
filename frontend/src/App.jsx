import React, { useState } from 'react';
import InputZone from './components/InputZone';
import AttackMatrixView from './components/AttackMatrixView';
import D3fendRoadmap from './components/D3fendRoadmap';
import PipelineProgress from './components/PipelineProgress';
import ExportBar from './components/ExportBar';

export default function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-[#0a0d14] text-slate-100">
      <header className="border-b border-[#1f293d] bg-[#111726]/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-[#00ffb2] animate-pulse"></div>
          <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
            Threat Intel RAG: MITRE ATT&CK & D3FEND Classifier
          </h1>
        </div>
        <div className="text-xs px-3 py-1 rounded-full bg-[#1f293d] text-slate-400 border border-slate-700">
          GraphRAG + LangGraph + Neo4j
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        <InputZone onAnalyze={setAnalysisResult} setLoading={setLoading} />
        {loading && <PipelineProgress />}
        {analysisResult && (
          <>
            <ExportBar data={analysisResult} />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AttackMatrixView attacks={analysisResult.attack_ttps || []} />
              <D3fendRoadmap defenses={analysisResult.d3fend_defenses || []} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
