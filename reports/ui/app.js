/**
 * Sandbox Performance & Evidence Dashboard Application Logic
 * Integrates benchmark bundle with interactive charts and views.
 */

(function () {
  'use strict';

  // Application State
  const state = {
    data: null,
    activeTab: 'overview',
    selectedSuite: 'all',
    selectedProviders: new Set(),
    latencyMetric: 'p50', // 'p50' or 'p95'
    scaleMode: 'linear',  // 'linear' or 'log'
    theme: localStorage.getItem('sb_theme') || 'dark',

    // Simulator State
    sim: {
      jobs: 50000,
      durationSec: 1.5,
      memoryGb: 2,
      concurrency: 4,
      storageGb: 5,
    },

    // Inspector Filter State
    inspector: {
      provider: 'all',
      suite: 'all',
      outcome: 'all',
      query: '',
      page: 1,
      pageSize: 25,
      selectedAttempt: null,
    },

    // Chart instances
    charts: {},
  };

  // Helper functions
  const fmtMs = (v) => ChartUtils.formatMs(v);
  const fmtCost = (v) => ChartUtils.formatCost(v);
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function measuredRows(suite) {
    const newest = new Map();
    for (const row of state.data.summaries || []) {
      if (row.suite !== suite || row.runtime_kind !== 'remote_runtime' || row.concurrency !== 1 ||
          !state.selectedProviders.has(row.provider) || !row.eligible) continue;
      const previous = newest.get(row.provider);
      if (!previous || row.last_measured_at > previous.last_measured_at) newest.set(row.provider, row);
    }
    return [...newest.values()];
  }
  const chartSuite = () => state.selectedSuite === 'all' ? 'cpu_stress' : state.selectedSuite;
  const cohortLabel = row => `${state.data.providers[row.provider]?.name || row.provider} · ${row.config_id.slice(0, 8)}`;

  // Initialize Application
  async function init() {
    applyTheme(state.theme);

    // Load data from window.BENCHMARK_DATA or data.json
    if (window.BENCHMARK_DATA) {
      state.data = window.BENCHMARK_DATA;
    } else {
      try {
        const resp = await fetch('data.json');
        state.data = await resp.json();
      } catch (err) {
        console.error('Failed to load benchmark data bundle:', err);
        showError('Could not load data.json or data.js. Ensure build_ui.py has been run.');
        return;
      }
    }

    // Populate all provider IDs into selected set by default
    Object.keys(state.data.providers).forEach(p => state.selectedProviders.add(p));

    renderHeaderKPIs();
    buildFilterBar();
    setupNavigation();
    setupSimulatorControls();
    setupInspectorEvents();
    setupGlobalControls();

    // Render initial active tab
    switchTab('overview');
  }

  function applyTheme(theme) {
    state.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('sb_theme', theme);
    const btn = document.getElementById('btn-theme-toggle');
    if (btn) btn.innerHTML = theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';

    // Re-render active charts
    Object.values(state.charts).forEach(c => {
      if (c && typeof c.render === 'function') c.render();
    });
  }

  function renderHeaderKPIs() {
    const meta = state.data.metadata || {};
    const totalRuns = meta.total_attempts ?? state.data.attempts.length;
    const totalProv = Object.keys(state.data.providers).length;
    const totalSuites = Object.keys(state.data.suites).length;
    const totalCampaigns = state.data.campaigns.length;

    const bar = document.getElementById('header-kpis');
    if (bar) {
      bar.innerHTML = `
        <div class="kpi-chip"><span>Runs:</span><strong>${totalRuns.toLocaleString()}</strong></div>
        <div class="kpi-chip"><span>Providers:</span><strong>${totalProv}</strong></div>
        <div class="kpi-chip"><span>Suites:</span><strong>${totalSuites}</strong></div>
        <div class="kpi-chip"><span>Campaigns:</span><strong>${totalCampaigns}</strong></div>
      `;
    }
  }

  function buildFilterBar() {
    // Populate Suite Selector
    const suiteSelect = document.getElementById('select-suite-filter');
    if (suiteSelect) {
      suiteSelect.innerHTML = `<option value="all">⚡ All Benchmark Suites</option>`;
      Object.entries(state.data.suites).forEach(([id, s]) => {
        suiteSelect.innerHTML += `<option value="${id}">${s.icon} ${s.name}</option>`;
      });
      suiteSelect.addEventListener('change', (e) => {
        state.selectedSuite = e.target.value;
        refreshCurrentTab();
      });
    }

    // Populate Provider Chips
    const chipsContainer = document.getElementById('provider-chips-container');
    if (chipsContainer) {
      chipsContainer.innerHTML = '';
      Object.entries(state.data.providers).forEach(([id, p]) => {
        const active = state.selectedProviders.has(id);
        const chip = document.createElement('button');
        chip.className = `provider-chip ${active ? 'active' : ''}`;
        chip.innerHTML = `
          <span class="chip-dot" style="background:${p.color};"></span>
          <span>${p.name}</span>
        `;
        chip.addEventListener('click', () => {
          if (state.selectedProviders.has(id)) {
            if (state.selectedProviders.size > 1) {
              state.selectedProviders.delete(id);
              chip.classList.remove('active');
            }
          } else {
            state.selectedProviders.add(id);
            chip.classList.add('active');
          }
          refreshCurrentTab();
        });
        chipsContainer.appendChild(chip);
      });
    }
  }

  function setupNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.getAttribute('data-tab');
        switchTab(target);
      });
    });
  }

  function switchTab(targetTab) {
    state.activeTab = targetTab;

    // Update tab button classes
    document.querySelectorAll('.nav-tab').forEach(t => {
      const name = t.getAttribute('data-tab');
      const selected = name === targetTab;
      t.classList.toggle('active', selected);
      t.setAttribute('aria-selected', selected ? 'true' : 'false');
      t.id = `tab-button-${name}`;
      t.setAttribute('aria-controls', `tab-${name}`);
    });

    // Update tab pane visibility
    document.querySelectorAll('.tab-pane').forEach(p => {
      p.classList.toggle('active', p.id === `tab-${targetTab}`);
      p.setAttribute('aria-labelledby', `tab-button-${p.id.replace('tab-', '')}`);
    });

    // Render corresponding view
    if (targetTab === 'overview') renderOverview();
    else if (targetTab === 'latency') renderLatencyStudio();
    else if (targetTab === 'phases') renderPhaseStudio();
    else if (targetTab === 'reliability') renderReliability();
    else if (targetTab === 'cost') renderCostFrontier();
    else if (targetTab === 'scale') renderThroughputScale();
    else if (targetTab === 'matrix') renderFeatureMatrix();
    else if (targetTab === 'inventory') renderHardwareInventory();
    else if (targetTab === 'simulator') renderCostSimulator();
    else if (targetTab === 'inspector') renderAttemptInspector();
  }

  function refreshCurrentTab() {
    switchTab(state.activeTab);
  }

  // ==========================================
  // VIEW 1: Overview & Executive Summary
  // ==========================================
  function renderOverview() {
    // 1. Calculate Quick Leaders
    const stats = state.data.provider_stats;
    const providers = state.data.providers;

    const heroContainer = document.getElementById('overview-hero-kpis');
    if (heroContainer) {
      const counts = [
        ['RETAINED ATTEMPTS', state.data.attempts.length, 'Includes failures and historical observations'],
        ['ELIGIBLE TASK / SETUP COHORTS', state.data.summaries.length, 'Workload, adapter and client identities remain separate'],
        ['PROVIDER SPECIFICATIONS', Object.keys(state.data.specifications).length, 'Documented contracts, not measured feature scores'],
        ['RECORDED CAMPAIGNS', state.data.campaigns.length, 'Pilot coverage, not a production SLA']
      ];
      heroContainer.innerHTML = counts.map(([label, value, note]) => `<div class="kpi-hero-card"><div class="kpi-hero-header">${label}</div><div class="kpi-hero-val">${value}</div><div class="kpi-hero-sub">${note}</div></div>`).join('');
    }

    // 2. Radar Chart (Top 5 Providers across 6 Dimensions)
    const radarContainer = document.getElementById('overview-radar-chart');
    if (radarContainer) {
      radarContainer.innerHTML = '<p>There is no measured composite security, cost, GPU or EU-residency score. Select a workload to inspect its cohort; use the feature matrix for documented contracts and the decision filter for hard requirements.</p><a href="../variant/index.html">Open architecture decision filter →</a>';
    }

    // 3. Quick Latency Bar Chart (Cold Start Comparison)
    const barContainer = document.getElementById('overview-bar-chart');
    if (barContainer) {
      if (!state.charts.overviewBar) {
        state.charts.overviewBar = new BarChart(barContainer, {
          yLabel: 'Readiness client lifecycle (p50 ms)',
          showErrorBars: true,
          onBarClick: (item) => {
            state.inspector.provider = item.meta?.pid || 'all';
            switchTab('inspector');
          }
        });
      }

      const barData = [];
      measuredRows('cold_start').forEach(s => {
        const pid = s.provider;
        if (s.latency_ms.p50) {
          barData.push({
            label: cohortLabel(s),
            value: s.latency_ms.p50,
            p95: s.latency_ms.p95,
            color: providers[pid].color,
            sublabel: `${s.outcomes.pass || 0}/${s.n} pass · latest serial cohort`,
            attempts: s.n,
            meta: { pid }
          });
        }
      });
      barData.sort((a, b) => a.value - b.value);
      state.charts.overviewBar.setData(barData);
    }

    // 4. Key Insights Cards
    const insightsContainer = document.getElementById('overview-insights-cards');
    if (insightsContainer && state.data.insights) {
      insightsContainer.innerHTML = '';
      state.data.insights.slice(0, 6).forEach(ins => {
        const card = document.createElement('div');
        const cat = ins.category || 'warning';
        card.className = `insight-card ${cat}`;
        card.innerHTML = `
          <div class="insight-title">
            <span>${cat === 'failure' ? '❌' : cat === 'warning' ? '⚠️' : '💡'}</span>
             <strong>${escapeHtml(ins.title)}</strong>
          </div>
          <div class="insight-desc">${escapeHtml(ins.finding)}</div>
          <div style="font-size:11px; margin-top:6px; color:var(--text-subtle);"><strong>Implication:</strong> ${escapeHtml(ins.implication)}</div>
        `;
        insightsContainer.appendChild(card);
      });
    }

    // 5. Providers Summary Snapshot Table
    const tableBody = document.getElementById('overview-providers-tbody');
    if (tableBody) {
      tableBody.innerHTML = '';
      Object.entries(stats).forEach(([pid, s]) => {
        const meta = providers[pid];
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="width:10px; height:10px; border-radius:50%; background:${meta.color};"></span>
              <strong>${meta.name}</strong>
            </div>
            <div style="font-size:11px; color:var(--text-subtle); margin-left:18px;">${meta.category}</div>
          </td>
          <td><span class="badge badge-neutral">${meta.badge}</span></td>
          <td class="mono"><strong>${fmtMs(measuredRows('cold_start').find(row => row.provider === pid)?.latency_ms.p50)}</strong></td>
          <td class="mono">${s.suites_tested.length}</td>
          <td class="mono">${s.passes} / ${s.fails} / ${s.total_attempts - s.passes - s.fails}</td>
          <td class="mono">${s.total_attempts}</td>
          <td>
            <button class="btn btn-icon-only" style="padding:4px 8px; font-size:12px;" onclick="window.viewProviderRuns('${pid}')">
              Inspect ↗
            </button>
          </td>
        `;
        tableBody.appendChild(tr);
      });
    }
  }

  // ==========================================
  // VIEW 2: Latency & Performance Studio
  // ==========================================
  function renderLatencyStudio() {
    const container = document.getElementById('latency-bar-chart');
    if (!container) return;

    if (!state.charts.latencyBar) {
      state.charts.latencyBar = new BarChart(container, {
        yLabel: 'Execution Latency (ms)',
        showErrorBars: true,
        onBarClick: (item) => {
          state.inspector.provider = item.meta?.pid || 'all';
          if (item.meta?.suite) state.inspector.suite = item.meta.suite;
          switchTab('inspector');
        }
      });
    }

    const summaries = state.data.summaries || [];
    const providers = state.data.providers;
    const selectedSuite = state.selectedSuite;

    const barData = [];

      measuredRows(chartSuite()).forEach(sum => {
          const lat = sum.latency_ms || sum.attempt_latency_ms || {};
          const val = state.latencyMetric === 'p95' ? lat.p95 : lat.p50;
          if (val) {
            barData.push({
              label: cohortLabel(sum),
              value: val,
              p95: lat.p95,
              color: providers[sum.provider]?.color || '#3b82f6',
              sublabel: `${sum.outcomes.pass || 0}/${sum.n} pass · ${chartSuite()}`,
              attempts: sum.attempts,
              passRate: sum.pass_rate,
              meta: { pid: sum.provider, suite: sum.suite }
            });
          }
      });

    barData.sort((a, b) => a.value - b.value);
    state.charts.latencyBar.setData(barData);

    // Update details table
    const tbody = document.getElementById('latency-details-tbody');
    if (tbody) {
      tbody.innerHTML = '';
      barData.forEach((row, rank) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>#${rank + 1}</td>
          <td>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="width:8px; height:8px; border-radius:50%; background:${row.color};"></span>
              <strong>${row.label}</strong>
            </div>
          </td>
          <td class="mono"><strong>${fmtMs(row.value)}</strong></td>
          <td class="mono">${fmtMs(row.p95)}</td>
          <td class="mono">${row.attempts}</td>
          <td class="mono">${row.sublabel}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  // ==========================================
  // VIEW 3: Lifecycle Phase Breakdown Studio
  // ==========================================
  function renderPhaseStudio() {
    const container = document.getElementById('phase-stacked-chart');
    if (!container) return;

    if (!state.charts.phaseStacked) {
      state.charts.phaseStacked = new PhaseStackedChart(container);
    }

    const summaries = state.data.summaries || [];
    const providers = state.data.providers;
    const selectedSuite = state.selectedSuite === 'all' ? 'data_pipeline' : state.selectedSuite;

    // Filter summaries for phase data
    const phaseItems = [];

    summaries.forEach(sum => {
      if ((sum.suite === selectedSuite || (selectedSuite === 'all' && sum.suite === 'data_pipeline')) &&
          state.selectedProviders.has(sum.provider)) {
        const ph = sum.phases_ms || {};
        const getPhaseVal = (p) => (ph[p] ? ph[p].p50 || ph[p].mean || 0 : 0);

        const initVal = getPhaseVal('initialize_ms');
        const prepVal = getPhaseVal('prepare_ms');
        const execVal = getPhaseVal('execute_ms');
        const colVal = getPhaseVal('collect_ms');
        const cleanVal = getPhaseVal('cleanup_ms');

        const total = initVal + prepVal + execVal + colVal + cleanVal;
        if (total > 0) {
          phaseItems.push({
            providerName: providers[sum.provider]?.name || sum.provider,
            providerId: sum.provider,
            suite: sum.suite,
            phases: {
              initialize: initVal,
              prepare: prepVal,
              execute: execVal,
              collect: colVal,
              cleanup: cleanVal,
            },
            totalMs: total,
          });
        }
      }
    });

    phaseItems.sort((a, b) => a.totalMs - b.totalMs);
    state.charts.phaseStacked.setData(phaseItems);

    const titleEl = document.getElementById('phase-suite-title');
    if (titleEl) {
      titleEl.innerText = `Lifecycle Phases for Suite: ${state.data.suites[selectedSuite]?.name || selectedSuite}`;
    }
  }

  // ==========================================
  // VIEW 4: Reliability & Pass Rate Heatmap
  // ==========================================
  function renderReliability() {
    // 1. Bar Chart with Wilson 95% Confidence Intervals
    const barContainer = document.getElementById('reliability-bar-chart');
    if (barContainer) {
      if (!state.charts.reliabilityBar) {
        state.charts.reliabilityBar = new BarChart(barContainer, {
          yLabel: 'Pass Rate (%)',
          showErrorBars: true,
        });
      }

      const barData = [];
      const providers = state.data.providers;

      measuredRows(chartSuite()).forEach(s => {
        const pid = s.provider;
        barData.push({
          label: cohortLabel(s),
          value: s.pass_rate * 100,
          p95: null, // Confidence interval rendered separately
          color: s.pass_rate >= 0.9 ? '#10b981' : s.pass_rate >= 0.7 ? '#f59e0b' : '#f43f5e',
          sublabel: `${chartSuite()} · ${s.outcomes.pass || 0}/${s.n} · Wilson 95% ${(s.success_ci95[0]*100).toFixed(1)}–${(s.success_ci95[1]*100).toFixed(1)}%`,
          attempts: s.n,
          passRate: s.pass_rate,
        });
      });
      barData.sort((a, b) => b.value - a.value);
      state.charts.reliabilityBar.setData(barData);
    }

    // 2. 2D Heatmap Grid (Providers vs Suites)
    const heatmapContainer = document.getElementById('reliability-heatmap-grid');
    if (heatmapContainer) {
      const providers = state.data.providers;
      const suites = state.data.suites;
      const summaries = state.data.summaries || [];

      // Map (provider, suite) -> summary
      const sumMap = {};
      Object.keys(suites).forEach(suite => measuredRows(suite).forEach(s => {sumMap[`${s.provider}:${s.suite}`] = s;}));

      let html = `<table class="heatmap-table"><thead><tr><th style="padding:8px 12px; text-align:left;">Provider</th>`;
      Object.entries(suites).forEach(([sid, s]) => {
        html += `<th title="${s.name}" style="padding:8px 4px; font-size:11px; text-align:center;">${s.icon}</th>`;
      });
      html += `</tr></thead><tbody>`;

      Object.entries(providers).forEach(([pid, p]) => {
        if (!state.selectedProviders.has(pid)) return;
        html += `<tr><td style="padding:6px 12px; font-size:12px; white-space:nowrap;"><strong>${p.name}</strong></td>`;
        Object.keys(suites).forEach(sid => {
          const match = sumMap[`${pid}:${sid}`];
          if (!match) {
            html += `<td><div class="heatmap-cell" style="background:var(--status-neutral-bg); color:var(--text-subtle); border:1px solid var(--border-subtle);" title="${p.name} - ${sid}: Not exercised">-</div></td>`;
          } else {
            const pr = match.pass_rate;
            let bg = 'var(--status-fail-bg)';
            let color = 'var(--status-fail)';
            let border = 'rgba(244, 63, 94, 0.4)';
            if (pr >= 0.99) {
              bg = 'var(--status-pass-bg)';
              color = 'var(--status-pass)';
              border = 'rgba(16, 185, 129, 0.4)';
            } else if (pr >= 0.5) {
              bg = 'var(--status-warn-bg)';
              color = 'var(--status-warn)';
              border = 'rgba(245, 158, 11, 0.4)';
            }
            html += `
              <td>
                <div class="heatmap-cell" 
                     style="background:${bg}; color:${color}; border:1px solid ${border};" 
                     title="${p.name} - ${sid}: latest serial setup ${match.config_id}, ${(pr * 100).toFixed(0)}% pass (${match.n} evaluated); not an SLA"
                     onclick="window.viewProviderSuiteRuns('${pid}', '${sid}')">
                  ${(pr * 100).toFixed(0)}
                </div>
              </td>
            `;
          }
        });
        html += `</tr>`;
      });

      html += `</tbody></table>`;
      heatmapContainer.innerHTML = html;
    }
  }

  // ==========================================
  // VIEW 5: Cost vs Latency Pareto Frontier
  // ==========================================
  function renderCostFrontier() {
    const container = document.getElementById('cost-scatter-plot');
    if (!container) return;

    container.innerHTML = '<p>Invoice-backed task costs were not recorded. Client wall time is not billed uptime, and saved unverified cost estimates cannot establish a cheapest-provider frontier.</p><p><a href="../variant/index.html#cost">Explore explicit published-rate scenarios →</a> · <a href="../executive/cost.svg">Model-agnostic worked example →</a></p>';
  }

  // ==========================================
  // VIEW 6: Scale & Burst Throughput
  // ==========================================
  function renderThroughputScale() {
    const container = document.getElementById('throughput-scale-chart');
    if (!container) return;

    if (!state.charts.scaleCurve) {
      state.charts.scaleCurve = new ThroughputScaleChart(container);
    }

    const campaigns = state.data.campaigns || [];
    const providers = state.data.providers;

    // Group campaigns by provider
    const provSeries = {};

    campaigns.forEach(c => {
      // Find provider from report_path
      const run = state.data.attempts.find(a => a.campaign_id === c.campaign_id);
      if (!run || run.runtime_kind !== 'remote_runtime' || !state.selectedProviders.has(run.provider) || !c.attempts ||
          !Number.isFinite(c.verified_completions_per_second_including_warmup_time)) return;
      const provId = run.provider;

      if (!provSeries[provId]) {
        provSeries[provId] = {
          name: providers[provId]?.name || provId,
          color: providers[provId]?.color || '#10b981',
          points: [],
        };
      }

      provSeries[provId].points.push({
        x: c.concurrency,
        y: c.verified_completions_per_second_including_warmup_time,
      });
    });

    state.charts.scaleCurve.setSeries(Object.values(provSeries));

    // Fill campaign details table
    const tbody = document.getElementById('scale-campaigns-tbody');
    if (tbody) {
      tbody.innerHTML = '';
      campaigns.slice(0, 15).forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="mono"><strong>${c.campaign_id}</strong></td>
          <td>${c.report_path}</td>
          <td class="mono"><strong>${c.concurrency}x</strong></td>
          <td class="mono">${c.passes} / ${c.attempts}</td>
          <td class="mono">${c.wall_seconds_including_warmups?.toFixed(2)}s</td>
          <td class="mono"><strong style="color:var(--accent-emerald);">${c.verified_completions_per_second_including_warmup_time?.toFixed(2)}</strong></td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  // ==========================================
  // VIEW 7: Feature & Specification Matrix
  // ==========================================
  function renderFeatureMatrix() {
    const tbody = document.getElementById('matrix-features-tbody');
    if (!tbody) return;

    const specs = state.data.specifications || {};
    const providers = state.data.providers;

    const coreFeatures = [
      { id: 'custom_image', label: 'Custom Docker Image' },
      { id: 'cpu_sizing', label: 'CPU Sizing Flexibility' },
      { id: 'memory_sizing', label: 'RAM Memory Sizing' },
      { id: 'gpu', label: 'Sandbox GPU Acceleration' },
      { id: 'network_policy', label: 'Network Policy Controls' },
      { id: 'runtime_packages', label: 'Offline Pip / Packages' },
      { id: 'session_reuse', label: 'Session Reuse (Documented)' },
      { id: 'cmek', label: 'CMEK (Documented Scope)' },
      { id: 'eu_residency', label: 'EU Data Residency' },
    ];

    tbody.innerHTML = '';

    Object.entries(providers).forEach(([pid, meta]) => {
      if (!state.selectedProviders.has(pid)) return;
      const provSpec = specs[pid] || {};
      const featList = provSpec.features || [];
      const featMap = {};
      featList.forEach(f => { featMap[f.id] = f; });

      const tr = document.createElement('tr');
      let cells = `
        <td>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:10px; height:10px; border-radius:50%; background:${meta.color};"></span>
            <strong>${meta.name}</strong>
          </div>
          <div style="font-size:11px; color:var(--text-subtle);">${provSpec.deployment || meta.badge}</div>
        </td>
      `;

      coreFeatures.forEach(feat => {
        const item = featMap[feat.id];
        let badgeClass = 'badge-neutral';
        let label = 'Unknown';

        if (item) {
          if (item.support === 'supported') {
            badgeClass = 'badge-pass';
            label = 'Supported';
          } else if (item.support === 'conditional') {
            badgeClass = 'badge-warn';
            label = 'Conditional';
          } else if (item.support === 'unsupported') {
            badgeClass = 'badge-fail';
            label = 'No';
          }
        }

        cells += `
          <td>
            <span class="badge ${badgeClass}" title="${escapeHtml(item?.notes || 'No specific notes')}">
              ${label}
            </span>
          </td>
        `;
      });

      tr.innerHTML = cells;
      tbody.appendChild(tr);
    });
  }

  // ==========================================
  // VIEW 8: Hardware & Guest Runtime Inventory
  // ==========================================
  function renderHardwareInventory() {
    const tbody = document.getElementById('inventory-details-tbody');
    if (!tbody) return;

    const configs = state.data.tested_configurations || [];
    const providers = state.data.providers;

    tbody.innerHTML = '';

    configs.forEach(cfg => {
      const pid = cfg.provider;
      if (!state.selectedProviders.has(pid)) return;
      const obs = cfg.observations?.[0]?.metrics || {};
      const cpu = obs.cpu?.visible_logical_cpus || 'Unknown';
      const memGb = obs.memory?.sysconf_physical_bytes ? (obs.memory.sysconf_physical_bytes / (1024**3)).toFixed(1) + ' GiB (host-visible)' : 'Unmeasured';
      const limit = obs.cgroup?.memory_max;
      const cgroupMax = typeof limit === 'number' && Number.isFinite(limit) ? (limit / (1024**3)).toFixed(1) + ' GiB' : 'Unrecorded / no mapped numeric limit';
      const pyVer = obs.runtime?.python || 'Unrecorded';
      const gpuProbe = obs.gpu?.probe || 'unavailable';

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="width:8px; height:8px; border-radius:50%; background:${providers[pid]?.color || '#fff'};"></span>
            <strong>${providers[pid]?.name || pid}</strong>
          </div>
          <div style="font-size:11px; color:var(--text-subtle);">${cfg.config_id}</div>
        </td>
        <td class="mono">${pyVer} (${obs.runtime?.os || 'Unrecorded'})</td>
        <td class="mono"><strong>${cpu} visible logical CPUs</strong></td>
        <td class="mono">${memGb}</td>
        <td class="mono">${cgroupMax}</td>
        <td>
          <span class="badge ${gpuProbe.includes('nvidia') ? 'badge-pass' : 'badge-neutral'}">
            ${gpuProbe}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  // ==========================================
  // VIEW 9: Scenario Cost Simulator
  // ==========================================
  function setupSimulatorControls() {
    const jobsSlider = document.getElementById('sim-jobs-slider');
    const durSlider = document.getElementById('sim-dur-slider');
    const memSlider = document.getElementById('sim-mem-slider');

    if (jobsSlider) {
      jobsSlider.addEventListener('input', (e) => {
        state.sim.jobs = parseInt(e.target.value, 10);
        document.getElementById('sim-jobs-val').innerText = state.sim.jobs.toLocaleString();
        renderCostSimulator();
      });
    }

    if (durSlider) {
      durSlider.addEventListener('input', (e) => {
        state.sim.durationSec = parseFloat(e.target.value);
        document.getElementById('sim-dur-val').innerText = `${state.sim.durationSec.toFixed(1)}s`;
        renderCostSimulator();
      });
    }

    if (memSlider) {
      memSlider.addEventListener('input', (e) => {
        state.sim.memoryGb = parseInt(e.target.value, 10);
        document.getElementById('sim-mem-val').innerText = `${state.sim.memoryGb} GiB`;
        renderCostSimulator();
      });
    }
  }

  function renderCostSimulator() {
    const container = document.getElementById('simulator-bar-chart');
    if (!container) return;

    if (!state.charts.simBar) {
      state.charts.simBar = new BarChart(container, {
        yLabel: 'Estimated Monthly Bill ($ USD)',
        showErrorBars: false,
      });
    }

    const { jobs, durationSec, memoryGb } = state.sim;
    const totalRuntimeHours = (jobs * durationSec) / 3600;

    // Unit-explicit request-only scenarios from the structured official-price snapshot.
    // No default guessed rate, consumed-resource proxy or proportional CPU/RAM multiplier.
    const estimates = [];
    for (const [id, unit, allocation] of [['modal', 'physical-core-second', '2 physical cores'], ['e2b', 'vCPU-second', '2 vCPU']]) {
      const rates = state.data.specifications[id]?.pricing?.rates || [];
      const cpu = rates.find(r => r.unit.includes(unit) && Number.isFinite(r.amount));
      const memory = rates.find(r => r.unit === 'GiB-second' && Number.isFinite(r.amount));
      if (cpu && memory) estimates.push({id, name: `${state.data.providers[id].name} (${allocation})`,
        color: state.data.providers[id].color, ratePerSec: 2*cpu.amount + memoryGb*memory.amount});
    }

    const simData = estimates.map(e => {
      const totalCost = jobs * durationSec * e.ratePerSec;
      return {
        label: e.name,
        value: totalCost,
        color: e.color,
        sublabel: `${fmtCost(totalCost / jobs)} / job`,
      };
    });

    simData.sort((a, b) => a.value - b.value);
    state.charts.simBar.setData(simData);

    const summaryEl = document.getElementById('sim-summary-text');
    if (summaryEl) {
      summaryEl.innerHTML = `
        Scenario: <strong>${jobs.toLocaleString()} jobs</strong>, <strong>${durationSec} billed seconds</strong> each,
        ${memoryGb} GiB RAM (${totalRuntimeHours.toFixed(1)} billed hours). Physical cores are not vCPUs.
        Only providers with mapped published CPU/RAM units are shown. Request-only compute estimates exclude
        bursting, region premiums, plan fees, storage, model charges, retries and tax; these are not invoices
        or a cheapest-provider ranking. <a href="../variant/index.html#cost">Full scenario conditions</a>.
      `;
    }
  }

  // ==========================================
  // VIEW 10: Deep-Dive Attempt Inspector
  // ==========================================
  function setupInspectorEvents() {
    const searchInput = document.getElementById('inspector-search-input');
    const outcomeSelect = document.getElementById('inspector-outcome-select');
    const provSelect = document.getElementById('inspector-prov-select');
    const suiteSelect = document.getElementById('inspector-suite-select');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        state.inspector.query = e.target.value.toLowerCase();
        state.inspector.page = 1;
        renderAttemptInspector();
      });
    }

    if (outcomeSelect) {
      outcomeSelect.addEventListener('change', (e) => {
        state.inspector.outcome = e.target.value;
        state.inspector.page = 1;
        renderAttemptInspector();
      });
    }

    if (provSelect) {
      provSelect.addEventListener('change', (e) => {
        state.inspector.provider = e.target.value;
        state.inspector.page = 1;
        renderAttemptInspector();
      });
    }

    if (suiteSelect) {
      suiteSelect.addEventListener('change', (e) => {
        state.inspector.suite = e.target.value;
        state.inspector.page = 1;
        renderAttemptInspector();
      });
    }

    // Drawer close buttons
    const closeBtn = document.getElementById('drawer-close-btn');
    const backdrop = document.getElementById('drawer-backdrop');
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (backdrop) backdrop.addEventListener('click', closeDrawer);
  }

  function renderAttemptInspector() {
    const attempts = state.data.attempts || [];
    const tbody = document.getElementById('inspector-table-tbody');
    if (!tbody) return;

    // Filter attempts
    const filtered = attempts.filter(a => {
      if (state.inspector.provider !== 'all' && a.provider !== state.inspector.provider) return false;
      if (state.inspector.suite !== 'all' && a.suite !== state.inspector.suite) return false;
      if (state.inspector.outcome !== 'all' && a.evaluation !== state.inspector.outcome) return false;
      if (state.inspector.query) {
        const q = state.inspector.query;
        return a.run_id.toLowerCase().includes(q) ||
               (a.stdout_preview && a.stdout_preview.toLowerCase().includes(q)) ||
               (a.stderr_preview && a.stderr_preview.toLowerCase().includes(q));
      }
      return true;
    });

    const total = filtered.length;
    const page = state.inspector.page;
    const pageSize = state.inspector.pageSize;
    const start = (page - 1) * pageSize;
    const end = Math.min(start + pageSize, total);
    const paged = filtered.slice(start, end);

    // Update count display
    const countEl = document.getElementById('inspector-match-count');
    if (countEl) countEl.innerText = `Showing ${start + 1}–${end} of ${total} runs`;

    tbody.innerHTML = '';
    paged.forEach(a => {
      const tr = document.createElement('tr');
      tr.style.cursor = 'pointer';
      tr.innerHTML = `
          <td class="mono"><strong>${escapeHtml(a.run_id)}</strong></td>
        <td>
          <div style="display:flex; align-items:center; gap:6px;">
            <span style="width:8px; height:8px; border-radius:50%; background:${state.data.providers[a.provider]?.color || '#fff'};"></span>
             ${escapeHtml(state.data.providers[a.provider]?.name || a.provider)}
          </div>
        </td>
        <td>${escapeHtml(state.data.suites[a.suite]?.name || a.suite)}</td>
        <td>
          <span class="badge ${a.evaluation === 'pass' ? 'badge-pass' : a.evaluation === 'fail' ? 'badge-fail' : 'badge-warn'}">
            ${a.evaluation.toUpperCase()}
          </span>
        </td>
        <td class="mono"><strong>${fmtMs(a.timings?.total_wall_clock_ms)}</strong></td>
        <td class="mono">${fmtCost(a.cost?.total_cost_usd)}</td>
        <td>
          <button class="btn btn-icon-only" style="padding:4px 8px; font-size:11px;">View ↗</button>
        </td>
      `;
      tr.addEventListener('click', () => openAttemptDrawer(a));
      tr.querySelector('button').addEventListener('click', event => {event.stopPropagation();openAttemptDrawer(a);});
      tbody.appendChild(tr);
    });

    renderInspectorPagination(total);
  }

  function renderInspectorPagination(total) {
    const pagContainer = document.getElementById('inspector-pagination');
    if (!pagContainer) return;
    const totalPages = Math.ceil(total / state.inspector.pageSize) || 1;
    const currentPage = state.inspector.page;

    pagContainer.innerHTML = `
      <button class="btn" ${currentPage === 1 ? 'disabled' : ''} id="pag-prev">‹ Previous</button>
      <span style="font-size:0.85rem; color:var(--text-muted); padding:0 12px;">Page ${currentPage} of ${totalPages}</span>
      <button class="btn" ${currentPage >= totalPages ? 'disabled' : ''} id="pag-next">Next ›</button>
    `;

    document.getElementById('pag-prev')?.addEventListener('click', () => {
      if (state.inspector.page > 1) {
        state.inspector.page--;
        renderAttemptInspector();
      }
    });

    document.getElementById('pag-next')?.addEventListener('click', () => {
      if (state.inspector.page < totalPages) {
        state.inspector.page++;
        renderAttemptInspector();
      }
    });
  }

  function openAttemptDrawer(a) {
    state.inspector.selectedAttempt = a;
    const backdrop = document.getElementById('drawer-backdrop');
    const panel = document.getElementById('drawer-panel');
    const body = document.getElementById('drawer-content');

    if (!backdrop || !panel || !body) return;

    const t = a.timings || {};
    const checks = a.checks || {};

    let checksHtml = '';
    Object.entries(checks).forEach(([chk, pass]) => {
      checksHtml += `
        <div style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid var(--border-subtle); font-size:12px;">
          <span class="mono">${escapeHtml(chk)}</span>
          <span class="badge ${pass ? 'badge-pass' : 'badge-fail'}">${pass ? 'PASS' : 'FAIL'}</span>
        </div>
      `;
    });

    body.innerHTML = `
      <div style="margin-bottom:18px;">
        <div style="font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Run Identifier</div>
        <div class="mono" style="font-size:1.1rem; font-weight:700;">${escapeHtml(a.run_id)}</div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:20px;">
        <div class="panel-card" style="padding:12px;">
          <div style="font-size:0.75rem; color:var(--text-muted);">Provider</div>
          <strong>${escapeHtml(state.data.providers[a.provider]?.name || a.provider)}</strong>
        </div>
        <div class="panel-card" style="padding:12px;">
          <div style="font-size:0.75rem; color:var(--text-muted);">Suite</div>
          <strong>${escapeHtml(state.data.suites[a.suite]?.name || a.suite)}</strong>
        </div>
        <div class="panel-card" style="padding:12px;">
          <div style="font-size:0.75rem; color:var(--text-muted);">Outcome</div>
          <span class="badge ${a.evaluation === 'pass' ? 'badge-pass' : 'badge-fail'}">${a.evaluation.toUpperCase()}</span>
        </div>
        <div class="panel-card" style="padding:12px;">
          <div style="font-size:0.75rem; color:var(--text-muted);">Total Wall Time</div>
          <strong class="mono">${fmtMs(t.total_wall_clock_ms)}</strong>
        </div>
      </div>

      <div style="margin-bottom:20px;">
        <h4 style="font-size:0.9rem; margin-bottom:8px;">Lifecycle Timings</h4>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:12px;" class="mono">
          <div>Init: <strong>${fmtMs(t.initialize_ms)}</strong></div>
          <div>Prepare: <strong>${fmtMs(t.prepare_ms)}</strong></div>
          <div>Execute: <strong>${fmtMs(t.execute_ms)}</strong></div>
          <div>Collect: <strong>${fmtMs(t.collect_ms)}</strong></div>
          <div>Cleanup: <strong>${fmtMs(t.cleanup_ms)}</strong></div>
          <div>Cost: <strong>${fmtCost(a.cost?.total_cost_usd)}</strong></div>
        </div>
      </div>

      <div style="margin-bottom:20px;">
        <h4 style="font-size:0.9rem; margin-bottom:8px;">Validation Checks</h4>
        <div style="background:var(--surface-card); padding:10px; border-radius:var(--radius-md);">
          ${checksHtml || '<span style="color:var(--text-muted); font-size:12px;">No checks recorded</span>'}
        </div>
      </div>

      <div style="margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <h4 style="font-size:0.9rem;">Captured Stdout</h4>
          <button id="copy-stdout-preview" class="btn" style="padding:2px 8px; font-size:11px;">Copy preview</button>
        </div>
        <div class="log-viewer">${escapeHtml(a.stdout_preview || '(empty stdout)')}</div>
        <p style="font-size:12px;">${a.is_truncated ? 'Preview only: original log is longer. ' : ''}Original stdout: ${a.stdout_chars} characters. <a id="raw-report-link">Open complete JSON</a></p>
      </div>

      <div>
        <h4 style="font-size:0.9rem; margin-bottom:6px;">Captured Stderr</h4>
        <div class="log-viewer" style="color:#f87171;">${escapeHtml(a.stderr_preview || '(empty stderr)')}</div>
      </div>
    `;

    document.getElementById('copy-stdout-preview').addEventListener('click', () => navigator.clipboard.writeText(a.stdout_preview));
    const reportUrl = new URL('../' + a.report_file, location.href);
    const reportRoot = new URL('../', location.href);
    if (reportUrl.protocol === reportRoot.protocol && reportUrl.host === reportRoot.host && reportUrl.pathname.startsWith(reportRoot.pathname)) {
      document.getElementById('raw-report-link').href = reportUrl.href;
    }
    backdrop.classList.add('open');
    panel.classList.add('open');
  }

  function closeDrawer() {
    document.getElementById('drawer-backdrop')?.classList.remove('open');
    document.getElementById('drawer-panel')?.classList.remove('open');
  }

  function setupGlobalControls() {
    // Theme toggle
    document.getElementById('btn-theme-toggle')?.addEventListener('click', () => {
      applyTheme(state.theme === 'dark' ? 'light' : 'dark');
    });

    // Metric toggle (p50 vs p95)
    document.getElementById('btn-metric-p50')?.addEventListener('click', () => {
      state.latencyMetric = 'p50';
      document.getElementById('btn-metric-p50').classList.add('btn-primary');
      document.getElementById('btn-metric-p95').classList.remove('btn-primary');
      renderLatencyStudio();
    });

    document.getElementById('btn-metric-p95')?.addEventListener('click', () => {
      state.latencyMetric = 'p95';
      document.getElementById('btn-metric-p95').classList.add('btn-primary');
      document.getElementById('btn-metric-p50').classList.remove('btn-primary');
      renderLatencyStudio();
    });

    // Export CSV
    document.getElementById('btn-export-csv')?.addEventListener('click', exportCSV);

    // Presentation view toggle
    document.getElementById('btn-presentation-mode')?.addEventListener('click', togglePresentationMode);
  }

  function exportCSV() {
    const attempts = state.data.attempts || [];
    let csv = 'RunID,Provider,Suite,Outcome,TotalWallMs,InitializeMs,ExecuteMs,CleanupMs,CostUSD\n';
    attempts.forEach(a => {
      const t = a.timings || {};
      csv += `${a.run_id},${a.provider},${a.suite},${a.evaluation},${t.total_wall_clock_ms || ''},${t.initialize_ms || ''},${t.execute_ms || ''},${t.cleanup_ms || ''},${a.cost?.total_cost_usd || ''}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sandbox_benchmark_attempts.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  function togglePresentationMode() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.().catch(() => {});
    } else {
      document.exitFullscreen?.().catch(() => {});
    }
  }

  function showError(msg) {
    const main = document.querySelector('.app-main');
    if (main) {
      main.innerHTML = `<div style="padding:40px; text-align:center; color:#f43f5e;"><h2>⚠️ Error</h2><p>${msg}</p></div>`;
    }
  }

    // Global helper hooks for inline HTML onclicks
    window.openAttempt = function (runId) {
      const match = (state.data.attempts || []).find(a => a.run_id === runId);
      if (match) openAttemptDrawer(match);
    };

    window.viewProviderRuns = function (pid) {
      state.inspector.provider = pid;
      state.inspector.suite = 'all';
      switchTab('inspector');
    };

    window.viewProviderSuiteRuns = function (pid, sid) {
      state.inspector.provider = pid;
      state.inspector.suite = sid;
      switchTab('inspector');
    };

    // Close drawer on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeDrawer();
    });

  // Bootstrap when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
