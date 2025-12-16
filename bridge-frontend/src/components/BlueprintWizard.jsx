/**
 * Blueprint Wizard Component
 * Creates mission blueprints from free-form briefs
 * Flow: Draft → Preview → Refine → Commit to Mission
 */
import React, { useState } from 'react';
import api from '../api';

export default function BlueprintWizard({ captain, onComplete }) {
  const [title, setTitle] = useState('');
  const [brief, setBrief] = useState('');
  const [blueprint, setBlueprint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function draft() {
    if (!title || !brief) {
      setError('Please provide both title and brief');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/blueprint/draft', {
        title,
        brief,
        captain: captain || 'Captain-Alpha'
      });
      
      setBlueprint(response.data);
    } catch (err) {
      setError(err.message || 'Failed to draft blueprint');
      console.error('Blueprint draft error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function commit() {
    const missionIdStr = prompt('Enter Mission ID to commit this blueprint:');
    if (!missionIdStr) return;

    const missionId = parseInt(missionIdStr, 10);
    if (isNaN(missionId)) {
      setError('Invalid mission ID');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post(
        `/blueprint/${blueprint.id}/commit?mission_id=${missionId}`
      );
      
      alert(`Success! Created ${response.data.created_jobs} agent jobs for mission ${missionId}`);
      
      if (onComplete) {
        onComplete(blueprint, missionId);
      }
      
      // Reset form
      setTitle('');
      setBrief('');
      setBlueprint(null);
    } catch (err) {
      setError(err.message || 'Failed to commit blueprint');
      console.error('Blueprint commit error:', err);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setBlueprint(null);
    setError(null);
  }

  return (
    <div className="blueprint-wizard bg-white border border-gray-300 rounded-lg shadow-sm p-6 max-w-4xl">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Mission Blueprint</h2>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!blueprint ? (
        <div className="draft-form space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Q4 Marketing Launch"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mission Brief
            </label>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your mission in plain language..."
              rows={8}
              value={brief}
              onChange={(e) => setBrief(e.target.value)}
              disabled={loading}
            />
          </div>

          <button
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={draft}
            disabled={loading || !title || !brief}
          >
            {loading ? 'Drafting...' : 'Draft Blueprint'}
          </button>
        </div>
      ) : (
        <div className="blueprint-preview space-y-4">
          <h3 className="text-xl font-semibold text-gray-800">
            Preview: {blueprint.title}
          </h3>

          <div className="bg-gray-900 text-gray-100 p-4 rounded overflow-auto max-h-96">
            <pre className="text-sm">
              {JSON.stringify(blueprint.plan, null, 2)}
            </pre>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <h4 className="font-medium text-blue-900 mb-2">Blueprint Summary</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• {blueprint.plan.objectives?.length || 0} objectives</li>
              <li>• {blueprint.plan.tasks?.length || 0} tasks</li>
              <li>• {blueprint.plan.artifacts?.length || 0} artifacts</li>
              <li>• {blueprint.plan.success_criteria?.length || 0} success criteria</li>
            </ul>
          </div>

          <div className="flex gap-3">
            <button
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-6 rounded disabled:opacity-50"
              onClick={commit}
              disabled={loading}
            >
              {loading ? 'Committing...' : 'Commit to Mission'}
            </button>
            <button
              className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded"
              onClick={reset}
              disabled={loading}
            >
              Start Over
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
