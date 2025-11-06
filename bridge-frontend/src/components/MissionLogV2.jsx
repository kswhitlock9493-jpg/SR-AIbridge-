/**
 * Mission Log v2 - Upgraded with Blueprint integration
 * Shows mission details with hierarchical task tree and agent deliberation
 */
import { useState, useEffect } from 'react';
import api from '../api';
import Tree from './ui/Tree';
import AgentDeliberationPanel from './AgentDeliberationPanel';

export default function MissionLogV2({ missionId }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!missionId) return;
    
    async function fetchMissionDetails() {
      setLoading(true);
      setError(null);

      try {
      // Fetch mission jobs
      const response = await api.get(`/missions/${missionId}/jobs`);
      setJobs(response.data || []);
    } catch (err) {
      console.error('Failed to fetch mission jobs:', err);
      setError(err.message || 'Failed to load mission details');
    } finally {
      setLoading(false);
    }
  }
  
    fetchMissionDetails();
  }, [missionId]);

  // Convert flat jobs list into tree structure
  function buildTaskTree(jobs) {
    if (!jobs || jobs.length === 0) return [];

    // Group jobs by task_key prefix to create hierarchy
    const nodes = jobs.map((job) => ({
      id: job.task_key,
      label: `${job.task_key} · ${job.status}`,
      status: job.status,
      children: [],
      data: job
    }));

    // Sort by task_key
    nodes.sort((a, b) => a.id.localeCompare(b.id));

    return nodes;
  }

  const taskTree = buildTaskTree(jobs);

  const getStatusSummary = () => {
    if (jobs.length === 0) return null;

    const summary = {
      total: jobs.length,
      queued: jobs.filter(j => j.status === 'queued').length,
      running: jobs.filter(j => j.status === 'running').length,
      done: jobs.filter(j => j.status === 'done').length,
      failed: jobs.filter(j => j.status === 'failed').length,
      skipped: jobs.filter(j => j.status === 'skipped').length
    };

    return summary;
  };

  const statusSummary = getStatusSummary();

  if (!missionId) {
    return (
      <div className="text-center text-gray-500 py-8">
        Select a mission to view details
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center text-gray-500 py-8">
        Loading mission details...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="mission-detail-v2 grid md:grid-cols-3 gap-4">
      <div className="md:col-span-2 space-y-4">
        <div className="bg-white border border-gray-300 rounded-lg shadow-sm p-4">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Mission #{missionId} - Task Tree
          </h2>

          {statusSummary && (
            <div className="bg-gray-50 border border-gray-200 rounded p-3 mb-4">
              <div className="text-sm text-gray-700 space-y-1">
                <div className="font-medium mb-2">Status Summary:</div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="text-yellow-600">⏳ Queued: {statusSummary.queued}</div>
                  <div className="text-blue-600">▶️ Running: {statusSummary.running}</div>
                  <div className="text-green-600">✓ Done: {statusSummary.done}</div>
                  <div className="text-red-600">✗ Failed: {statusSummary.failed}</div>
                  <div className="text-gray-500">⊘ Skipped: {statusSummary.skipped}</div>
                  <div className="text-gray-700 font-medium">Total: {statusSummary.total}</div>
                </div>
              </div>
            </div>
          )}

          {jobs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              No blueprint jobs found for this mission.
              <div className="text-sm mt-2">
                Create a blueprint and commit it to this mission to see tasks here.
              </div>
            </div>
          ) : (
            <Tree nodes={taskTree} />
          )}
        </div>

        <div className="bg-white border border-gray-300 rounded-lg shadow-sm p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Task Details</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {jobs.map((job) => (
              <div key={job.id} className="border border-gray-200 rounded p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="font-mono text-sm font-medium text-gray-700">
                      {job.task_key}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {job.task_desc}
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    job.status === 'done' ? 'bg-green-100 text-green-800' :
                    job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                    job.status === 'queued' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status}
                  </div>
                </div>
                {job.agent_name && (
                  <div className="text-xs text-gray-500 mt-2">
                    Assigned to: {job.agent_name}
                  </div>
                )}
                {job.inputs?.depends_on && job.inputs.depends_on.length > 0 && (
                  <div className="text-xs text-gray-500 mt-1">
                    Depends on: {job.inputs.depends_on.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="md:col-span-1">
        <AgentDeliberationPanel missionId={missionId} />
      </div>
    </div>
  );
}
