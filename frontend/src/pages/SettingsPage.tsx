import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Settings, Server, Database, Save, CheckCircle2 } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [fastApiUrl, setFastApiUrl] = useState('http://127.0.0.1:8000/api/v1');
  const [renodePath, setRenodePath] = useState('C:\\Program Files\\Renode\\renode.exe');
  const [useLiveApi, setUseLiveApi] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      {/* Top Banner */}
      <Card className="p-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Framework & Data Settings</h1>
            <p className="text-xs text-slate-500">
              Configure dataset provider mode, backend REST API endpoints, and simulator paths
            </p>
          </div>
        </div>
      </Card>

      {/* Settings Form */}
      <Card className="p-5">
        <form onSubmit={handleSave} className="space-y-5">
          {/* Data Source Toggle */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-slate-600" /> Data Provider Source
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setUseLiveApi(false)}
                className={`p-3.5 rounded-md border text-left transition-all cursor-pointer ${
                  !useLiveApi
                    ? 'bg-slate-900 border-slate-900 text-white shadow-xs'
                    : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <div className="font-bold text-xs mb-1">Local Benchmark Dataset (.csv)</div>
                <div className="text-[11px] opacity-80 leading-snug">
                  Uses physical Renode benchmark simulation records from dataset/benchmark.csv.
                </div>
              </button>

              <button
                type="button"
                onClick={() => setUseLiveApi(true)}
                className={`p-3.5 rounded-md border text-left transition-all cursor-pointer ${
                  useLiveApi
                    ? 'bg-slate-900 border-slate-900 text-white shadow-xs'
                    : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <div className="font-bold text-xs mb-1">Backend REST API Endpoint</div>
                <div className="text-[11px] opacity-80 leading-snug">
                  Connects to FastAPI Python backend server for real-time model inference.
                </div>
              </button>
            </div>
          </div>

          {/* FastAPI Endpoint input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1 flex items-center gap-1.5">
              <Server className="w-4 h-4 text-slate-600" /> Backend REST API Base URL
            </label>
            <input
              type="text"
              value={fastApiUrl}
              onChange={(e) => setFastApiUrl(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 font-mono outline-none focus:border-slate-800"
            />
          </div>

          {/* Renode Executable Path */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Renode CLI Executable Path
            </label>
            <input
              type="text"
              value={renodePath}
              onChange={(e) => setRenodePath(e.target.value)}
              className="w-full bg-white border border-slate-300 rounded-md px-3 py-2 text-xs text-slate-900 font-mono outline-none focus:border-slate-800"
            />
          </div>

          {/* Save Button */}
          <div className="flex items-center gap-3 pt-3 border-t border-slate-200">
            <Button type="submit" variant="primary" size="sm" icon={<Save className="w-4 h-4" />}>
              Save Settings
            </Button>

            {savedSuccess && (
              <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Settings updated!
              </span>
            )}
          </div>
        </form>
      </Card>
    </div>
  );
};
