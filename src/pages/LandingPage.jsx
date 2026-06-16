import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex flex-col items-center justify-center relative overflow-hidden font-sans">
      {/* Dynamic Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob"></div>
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-20%] left-[20%] w-[40%] h-[40%] bg-blue-600 rounded-full mix-blend-multiply filter blur-[128px] opacity-40 animate-blob animation-delay-4000"></div>
      </div>

      {/* Content Container */}
      <div className="relative z-10 max-w-5xl w-full px-6 flex flex-col items-center text-center">
        
        {/* Header Section */}
        <div className="mb-16">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
            Welcome to Edgechurn
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed">
            Advanced AI-powered solutions designed to accelerate workflows and unlock actionable insights. Select a platform to continue.
          </p>
        </div>

        {/* Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
          
          {/* Moove Card */}
          <div 
            onClick={() => navigate('/moove')}
            className="group relative cursor-pointer rounded-2xl border border-gray-800 bg-gray-900/50 backdrop-blur-xl p-8 hover:bg-gray-800/50 hover:border-indigo-500/50 transition-all duration-300 shadow-2xl overflow-hidden flex flex-col items-center text-center"
          >
            {/* Card Hover Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            <div className="h-16 w-16 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6 border border-indigo-500/30 group-hover:scale-110 transition-transform duration-300">
              <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            
            <h2 className="text-2xl font-bold text-white mb-3 tracking-wide">Moove</h2>
            <p className="text-gray-400 text-sm leading-relaxed mb-6">
              Advanced motion analysis platform for physiotherapists, athletes, and coaches. Measure, track, and optimize human movement with AI.
            </p>
            
            <div className="mt-auto flex items-center text-indigo-400 text-sm font-semibold group-hover:text-indigo-300 transition-colors">
              Launch Moove
              <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>
          </div>

          {/* Legal Analysis Card */}
          <div 
            onClick={() => window.location.href = '/LegalAnalysis'}
            className="group relative cursor-pointer rounded-2xl border border-gray-800 bg-gray-900/50 backdrop-blur-xl p-8 hover:bg-gray-800/50 hover:border-emerald-500/50 transition-all duration-300 shadow-2xl overflow-hidden flex flex-col items-center text-center"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            <div className="h-16 w-16 bg-emerald-500/20 rounded-2xl flex items-center justify-center mb-6 border border-emerald-500/30 group-hover:scale-110 transition-transform duration-300">
              <svg className="w-8 h-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            
            <h2 className="text-2xl font-bold text-white mb-3 tracking-wide">Legal Analysis</h2>
            <p className="text-gray-400 text-sm leading-relaxed mb-6">
              AI-driven legal document processing and strategy generation. Intelligently extract entities, match precedents, and formulate legal positions.
            </p>
            
            <div className="mt-auto flex items-center text-emerald-400 text-sm font-semibold group-hover:text-emerald-300 transition-colors">
              Launch Analyzer
              <svg className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default LandingPage;
