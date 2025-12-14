"""
Genesis Inspector Panel UI
Visual web dashboard for environment oversight and one-click remediation
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import logging

logger = logging.getLogger(__name__)

ui_router = APIRouter(prefix="/genesis/envrecon", tags=["envrecon-ui"])


@ui_router.get("", response_class=HTMLResponse)
async def inspector_panel(request: Request):
    """
    Genesis Inspector Panel - Interactive environment management dashboard.
    Provides visual oversight and one-click remediation.
    """
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Genesis Inspector Panel - EnvRecon v2.0.2</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
        <style>
            .status-ok { color: #10b981; }
            .status-missing { color: #f59e0b; }
            .status-conflict { color: #ef4444; }
            .status-synced { color: #3b82f6; }
        </style>
    </head>
    <body class="bg-gray-50">
        <div id="app" class="container mx-auto px-4 py-8">
            <div class="bg-white shadow-lg rounded-lg p-6 mb-6">
                <h1 class="text-3xl font-bold text-gray-800 mb-2">
                    🧭 Genesis Inspector Panel
                </h1>
                <p class="text-gray-600 mb-4">EnvRecon v2.0.2 - Environment Synchronization Dashboard</p>
                
                <div class="flex gap-4 mb-6">
                    <button @click="runAudit" 
                            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold"
                            :disabled="loading">
                        {{ loading ? 'Auditing...' : '🔍 Run Audit' }}
                    </button>
                    <button @click="syncAll" 
                            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold"
                            :disabled="loading">
                        🔄 Sync All
                    </button>
                    <button @click="healNow" 
                            class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold"
                            :disabled="loading">
                        🩹 Heal Now
                    </button>
                    <button @click="loadReport" 
                            class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-semibold"
                            :disabled="loading">
                        📄 Refresh
                    </button>
                </div>
            </div>

            <!-- Summary Cards -->
            <div v-if="report" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div class="bg-white shadow rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Total Variables</h3>
                    <p class="text-3xl font-bold text-gray-800">{{ report.summary?.total_keys || 0 }}</p>
                </div>
                <div class="bg-white shadow rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Conflicts</h3>
                    <p class="text-3xl font-bold text-red-600">{{ Object.keys(report.conflicts || {}).length }}</p>
                </div>
                <div class="bg-white shadow rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Missing (Render)</h3>
                    <p class="text-3xl font-bold text-orange-600">{{ report.missing_in_render?.length || 0 }}</p>
                </div>
                <div class="bg-white shadow rounded-lg p-4">
                    <h3 class="text-sm font-semibold text-gray-600 mb-2">Auto-Fixed</h3>
                    <p class="text-3xl font-bold text-green-600">{{ report.autofixed?.length || 0 }}</p>
                </div>
            </div>

            <!-- Environment Parity Table -->
            <div v-if="report" class="bg-white shadow-lg rounded-lg p-6 mb-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Environment Parity Status</h2>
                
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Variable
                                </th>
                                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Render
                                </th>
                                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Netlify
                                </th>
                                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    GitHub
                                </th>
                                <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="item in parityItems" :key="item.name" class="hover:bg-gray-50">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {{ item.name }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center text-sm">
                                    <span :class="item.render ? 'text-green-600' : 'text-red-600'">
                                        {{ item.render ? '✅' : '❌' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center text-sm">
                                    <span :class="item.netlify ? 'text-green-600' : 'text-red-600'">
                                        {{ item.netlify ? '✅' : '❌' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center text-sm">
                                    <span :class="item.github ? 'text-green-600' : 'text-red-600'">
                                        {{ item.github ? '✅' : '❌' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-center text-sm">
                                    <span :class="getStatusClass(item.status)" class="px-2 py-1 rounded font-semibold">
                                        {{ item.status }}
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Conflicts Section -->
            <div v-if="report && Object.keys(report.conflicts || {}).length > 0" 
                 class="bg-white shadow-lg rounded-lg p-6 mb-6">
                <h2 class="text-xl font-bold text-red-600 mb-4">⚠️ Conflicts Detected</h2>
                <div v-for="(values, key) in report.conflicts" :key="key" class="mb-4 border-l-4 border-red-500 pl-4">
                    <h3 class="font-semibold text-gray-800">{{ key }}</h3>
                    <ul class="mt-2 space-y-1">
                        <li v-for="(value, platform) in values" :key="platform" class="text-sm text-gray-600">
                            <span class="font-medium">{{ platform }}:</span> 
                            <code class="bg-gray-100 px-2 py-1 rounded">{{ value }}</code>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Last Updated -->
            <div v-if="report" class="text-center text-gray-500 text-sm">
                Last updated: {{ formatTimestamp(report.timestamp) }}
            </div>

            <!-- Loading/Error State -->
            <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                <strong class="font-bold">Error:</strong>
                <span class="block sm:inline">{{ error }}</span>
            </div>
        </div>

        <script>
            const { createApp } = Vue;

            createApp({
                data() {
                    return {
                        report: null,
                        loading: false,
                        error: null,
                        autoRefresh: null
                    };
                },
                computed: {
                    parityItems() {
                        if (!this.report) return [];
                        
                        const items = [];
                        const allVars = new Set([
                            ...(this.report.missing_in_render || []),
                            ...(this.report.missing_in_netlify || []),
                            ...(this.report.missing_in_github || []),
                            ...Object.keys(this.report.conflicts || {})
                        ]);

                        allVars.forEach(varName => {
                            const inRender = !this.report.missing_in_render?.includes(varName);
                            const inNetlify = !this.report.missing_in_netlify?.includes(varName);
                            const inGithub = !this.report.missing_in_github?.includes(varName);
                            const hasConflict = varName in (this.report.conflicts || {});
                            const wasFixed = this.report.autofixed?.includes(varName);

                            let status = '✅ SYNCED';
                            if (wasFixed) status = '🔧 FIXED';
                            else if (hasConflict) status = '⚠️ CONFLICT';
                            else if (!inRender || !inNetlify) status = '⚠️ MISSING';

                            items.push({
                                name: varName,
                                render: inRender,
                                netlify: inNetlify,
                                github: inGithub,
                                status: status
                            });
                        });

                        return items;
                    }
                },
                methods: {
                    async loadReport() {
                        this.loading = true;
                        this.error = null;
                        try {
                            const resp = await fetch('/api/envrecon/report');
                            if (!resp.ok) {
                                if (resp.status === 404) {
                                    this.error = 'No report available. Run audit first.';
                                } else {
                                    throw new Error('Failed to load report');
                                }
                                return;
                            }
                            this.report = await resp.json();
                        } catch (err) {
                            this.error = err.message;
                        } finally {
                            this.loading = false;
                        }
                    },
                    async runAudit() {
                        this.loading = true;
                        this.error = null;
                        try {
                            const resp = await fetch('/api/envrecon/audit', { method: 'POST' });
                            if (!resp.ok) throw new Error('Audit failed');
                            const data = await resp.json();
                            this.report = data.report;
                        } catch (err) {
                            this.error = err.message;
                        } finally {
                            this.loading = false;
                        }
                    },
                    async syncAll() {
                        this.loading = true;
                        this.error = null;
                        try {
                            const resp = await fetch('/api/envrecon/sync', { method: 'POST' });
                            if (!resp.ok) throw new Error('Sync failed');
                            const data = await resp.json();
                            this.report = data.report;
                        } catch (err) {
                            this.error = err.message;
                        } finally {
                            this.loading = false;
                        }
                    },
                    async healNow() {
                        this.loading = true;
                        this.error = null;
                        try {
                            const resp = await fetch('/api/envrecon/heal', { method: 'POST' });
                            if (!resp.ok) throw new Error('Healing failed');
                            await this.loadReport();
                        } catch (err) {
                            this.error = err.message;
                        } finally {
                            this.loading = false;
                        }
                    },
                    formatTimestamp(ts) {
                        if (!ts) return 'N/A';
                        return new Date(ts).toLocaleString();
                    },
                    getStatusClass(status) {
                        if (status.includes('SYNCED')) return 'status-synced';
                        if (status.includes('FIXED')) return 'status-ok';
                        if (status.includes('MISSING')) return 'status-missing';
                        if (status.includes('CONFLICT')) return 'status-conflict';
                        return '';
                    }
                },
                mounted() {
                    // Load report on mount
                    this.loadReport();
                }
            }).mount('#app');
        </script>
    </body>
    </html>
    """
    
    return html_content
