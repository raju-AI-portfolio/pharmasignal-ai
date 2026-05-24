import React, { useState } from 'react';
import CaseQueue from './components/CaseQueue';
import CaseDetail from './components/CaseDetail';
import './App.css';

function App() {
  const [selectedCase, setSelectedCase] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'pending' | 'all'>('pending');

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>PharmaSignal AI</h1>
          <span className="subtitle">Pharmacovigilance Review Dashboard</span>
        </div>
        <div className="header-right">
          <span className="user">Dr. Smith — Safety Scientist</span>
        </div>
      </header>

      <div className="main">
        {selectedCase ? (
          <CaseDetail
            reportId={selectedCase}
            onBack={() => setSelectedCase(null)}
          />
        ) : (
          <CaseQueue
            onSelectCase={setSelectedCase}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        )}
      </div>
    </div>
  );
}

export default App;
