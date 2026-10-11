/**
 * Modern High-Fidelity Chart Engine for Benchmark Data Visualization
 * Pure Vanilla JS, zero external dependencies, 100% offline & Retina-sharp.
 */

class ChartUtils {
  static setupCanvas(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = rect.width || canvas.width || 600;
    const height = rect.height || canvas.height || 360;

    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);

    const ctx = canvas.getContext('2d');
    ctx.resetTransform?.();
    ctx.scale(dpr, dpr);
    return { ctx, width, height, dpr };
  }

  static getThemeColors() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    return {
      isLight,
      text: isLight ? '#1e293b' : '#f1f5f9',
      textMuted: isLight ? '#64748b' : '#94a3b8',
      grid: isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.08)',
      cardBg: isLight ? '#ffffff' : '#111827',
      tooltipBg: isLight ? 'rgba(255, 255, 255, 0.96)' : 'rgba(15, 23, 42, 0.95)',
      tooltipBorder: isLight ? 'rgba(0, 0, 0, 0.12)' : 'rgba(255, 255, 255, 0.15)',
    };
  }

  static formatMs(ms) {
    if (ms === null || ms === undefined || isNaN(ms)) return 'N/A';
    if (ms < 1) return `${(ms * 1000).toFixed(0)} µs`;
    if (ms < 1000) return `${ms.toFixed(1)} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  }

  static formatCost(usd) {
    if (usd === null || usd === undefined || isNaN(usd)) return 'N/A';
    if (usd === 0) return '$0.00';
    if (usd < 0.0001) return `$${usd.toExponential(2)}`;
    if (usd < 0.01) return `$${usd.toFixed(5)}`;
    if (usd < 1) return `$${usd.toFixed(3)}`;
    return `$${usd.toFixed(2)}`;
  }

  static createTooltip() {
    let tooltip = document.getElementById('chart-global-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'chart-global-tooltip';
      tooltip.className = 'chart-tooltip';
      tooltip.style.cssText = `
        position: fixed;
        pointer-events: none;
        z-index: 9999;
        display: none;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 12px;
        line-height: 1.4;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(12px);
        transition: opacity 0.12s ease;
      `;
      document.body.appendChild(tooltip);
    }
    return tooltip;
  }
}

// Global tooltip instance
const globalTooltip = ChartUtils.createTooltip();

/**
 * 1. Horizontal / Vertical Grouped & Single Bar Chart
 */
class BarChart {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    this.options = Object.assign({
      orientation: 'vertical', // 'vertical' or 'horizontal'
      isLog: false,
      title: '',
      yLabel: 'Latency (ms)',
      xLabel: '',
      showErrorBars: true,
      animate: true,
      onBarClick: null
    }, options);

    this.data = [];
    this.hoverIndex = -1;
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chart-wrapper">
        <canvas class="chart-canvas"></canvas>
      </div>
    `;
    this.canvas = this.container.querySelector('canvas');
    this.attachEvents();
  }

  setData(data) {
    // data: Array of { label, value, p95, color, sublabel, meta }
    this.data = data;
    this.render();
  }

  attachEvents() {
    const handleMove = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      this.handleHover(x, y, e.clientX, e.clientY);
    };

    const handleLeave = () => {
      this.hoverIndex = -1;
      globalTooltip.style.display = 'none';
      this.render();
    };

    const handleClick = () => {
      if (this.hoverIndex >= 0 && this.options.onBarClick) {
        this.options.onBarClick(this.data[this.hoverIndex]);
      }
    };

    this.canvas.addEventListener('mousemove', handleMove);
    this.canvas.addEventListener('mouseleave', handleLeave);
    this.canvas.addEventListener('click', handleClick);

    window.addEventListener('resize', () => {
      if (this.data && this.data.length > 0) this.render();
    });
  }

  handleHover(mouseX, mouseY, screenX, screenY) {
    if (!this.barBounds || this.barBounds.length === 0) return;
    let found = -1;
    for (let i = 0; i < this.barBounds.length; i++) {
      const b = this.barBounds[i];
      if (mouseX >= b.x && mouseX <= b.x + b.w && mouseY >= b.y && mouseY <= b.y + b.h) {
        found = i;
        break;
      }
    }

    if (found !== this.hoverIndex) {
      this.hoverIndex = found;
      this.render();
    }

    if (found >= 0) {
      const item = this.data[found];
      const colors = ChartUtils.getThemeColors();
      globalTooltip.style.backgroundColor = colors.tooltipBg;
      globalTooltip.style.borderColor = colors.tooltipBorder;
      globalTooltip.style.border = `1px solid ${colors.tooltipBorder}`;
      globalTooltip.style.color = colors.text;

      let extra = '';
      if (item.p95 !== undefined && item.p95 !== null) {
        extra += `<div style="display:flex; justify-content:space-between; gap:16px;"><span>p95 Tail:</span><strong>${ChartUtils.formatMs(item.p95)}</strong></div>`;
      }
      if (item.attempts !== undefined) {
        extra += `<div style="display:flex; justify-content:space-between; gap:16px;"><span>Attempts:</span><span>${item.attempts}</span></div>`;
      }
      if (item.passRate !== undefined) {
        extra += `<div style="display:flex; justify-content:space-between; gap:16px;"><span>Pass Rate:</span><strong>${(item.passRate * 100).toFixed(1)}%</strong></div>`;
      }

      globalTooltip.innerHTML = `
        <div style="font-weight:600; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
          <span style="width:10px; height:10px; border-radius:50%; background:${item.color}; display:inline-block;"></span>
          ${item.label}
        </div>
        <div style="font-size:11px; color:${colors.textMuted}; margin-bottom:6px;">${item.sublabel || ''}</div>
        <div style="display:flex; justify-content:space-between; gap:16px; margin-bottom:2px;">
          <span>Median (p50):</span>
          <strong style="color:${item.color}">${ChartUtils.formatMs(item.value)}</strong>
        </div>
        ${extra}
      `;
      globalTooltip.style.display = 'block';
      globalTooltip.style.left = `${screenX + 14}px`;
      globalTooltip.style.top = `${screenY - 10}px`;
    } else {
      globalTooltip.style.display = 'none';
    }
  }

  render() {
    const { ctx, width, height } = ChartUtils.setupCanvas(this.canvas);
    if (!this.data || this.data.length === 0) {
      ctx.fillStyle = ChartUtils.getThemeColors().textMuted;
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data matching selected filters', width / 2, height / 2);
      return;
    }

    const theme = ChartUtils.getThemeColors();
    const padding = { top: 24, right: 30, bottom: 56, left: 64 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Calculate value range
    let maxVal = Math.max(...this.data.map(d => Math.max(d.value || 0, d.p95 || 0)), 10);
    maxVal = maxVal * 1.15; // margin

    // Draw horizontal grid lines
    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.grid;
    ctx.fillStyle = theme.textMuted;
    ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace';
    ctx.textAlign = 'right';

    const gridLines = 5;
    for (let i = 0; i <= gridLines; i++) {
      const val = (maxVal / gridLines) * i;
      const y = padding.top + chartH - (chartH / gridLines) * i;

      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();

      const valStr = val >= 1000 ? `${(val / 1000).toFixed(1)}s` : `${Math.round(val)}ms`;
      ctx.fillText(valStr, padding.left - 8, y + 4);
    }

    // Draw bars
    const n = this.data.length;
    const barWidth = Math.min(chartW / n * 0.65, 52);
    const step = chartW / n;
    this.barBounds = [];

    this.data.forEach((item, idx) => {
      const x = padding.left + step * idx + (step - barWidth) / 2;
      const val = Math.max(item.value || 0, 0);
      const barH = (val / maxVal) * chartH;
      const y = padding.top + chartH - barH;

      this.barBounds.push({ x, y, w: barWidth, h: barH, index: idx });

      const isHovered = this.hoverIndex === idx;

      // Bar shadow / glow on hover
      if (isHovered) {
        ctx.shadowColor = item.color;
        ctx.shadowBlur = 12;
      } else {
        ctx.shadowBlur = 0;
      }

      // Rounded bar top
      const r = Math.min(5, barWidth / 2, barH);
      ctx.fillStyle = isHovered ? item.color : item.color;
      ctx.beginPath();
      ctx.moveTo(x, y + barH);
      ctx.lineTo(x, y + r);
      ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.lineTo(x + barWidth - r, y);
      ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + r);
      ctx.lineTo(x + barWidth, y + barH);
      ctx.closePath();
      ctx.fill();

      ctx.shadowBlur = 0;

      // Draw p95 error line / whisker if available
      if (this.options.showErrorBars && item.p95 && item.p95 > val) {
        const p95H = (item.p95 / maxVal) * chartH;
        const p95Y = padding.top + chartH - p95H;

        ctx.strokeStyle = theme.isLight ? 'rgba(0,0,0,0.5)' : 'rgba(255,255,255,0.7)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        // vertical stem
        ctx.moveTo(x + barWidth / 2, y);
        ctx.lineTo(x + barWidth / 2, p95Y);
        // top whisker cap
        ctx.moveTo(x + barWidth / 2 - 5, p95Y);
        ctx.lineTo(x + barWidth / 2 + 5, p95Y);
        ctx.stroke();
      }

      // X Label
      ctx.save();
      ctx.fillStyle = isHovered ? theme.text : theme.textMuted;
      ctx.font = isHovered ? '600 11px sans-serif' : '11px sans-serif';
      ctx.textAlign = 'center';

      // Truncate label if too long
      let displayLabel = item.label;
      if (n > 8 && displayLabel.length > 10) {
        displayLabel = displayLabel.slice(0, 9) + '…';
      }
      ctx.fillText(displayLabel, x + barWidth / 2, padding.top + chartH + 18);

      // Sublabel / pass rate badge
      if (item.sublabel) {
        ctx.fillStyle = theme.textMuted;
        ctx.font = '10px monospace';
        ctx.fillText(item.sublabel, x + barWidth / 2, padding.top + chartH + 32);
      }
      ctx.restore();
    });

    // Y Axis Title
    ctx.save();
    ctx.translate(16, padding.top + chartH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillStyle = theme.textMuted;
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(this.options.yLabel, 0, 0);
    ctx.restore();
  }
}

/**
 * 2. Phase Breakdown Stacked Bar Chart
 * Shows Initialize, Prepare, Execute, Collect, Cleanup ms
 */
class PhaseStackedChart {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    this.options = Object.assign({
      title: 'Lifecycle Phase Breakdown',
      onBarClick: null
    }, options);
    this.data = [];
    this.hoverInfo = null;

    this.phaseColors = {
      initialize: '#6366f1', // Indigo
      prepare: '#3b82f6',    // Blue
      execute: '#10b981',    // Emerald
      collect: '#f59e0b',    // Amber
      cleanup: '#ec4899',    // Pink
    };

    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chart-wrapper">
        <div class="chart-legend" style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:12px; font-size:12px;">
          <span style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:3px; background:${this.phaseColors.initialize};"></span> Initialize</span>
          <span style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:3px; background:${this.phaseColors.prepare};"></span> Prepare / Stage</span>
          <span style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:3px; background:${this.phaseColors.execute};"></span> Execute Workload</span>
          <span style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:3px; background:${this.phaseColors.collect};"></span> Collect Artifacts</span>
          <span style="display:flex; align-items:center; gap:6px;"><span style="width:10px; height:10px; border-radius:3px; background:${this.phaseColors.cleanup};"></span> Cleanup / Teardown</span>
        </div>
        <canvas class="chart-canvas"></canvas>
      </div>
    `;
    this.canvas = this.container.querySelector('canvas');
    this.attachEvents();
  }

  setData(data) {
    // Array of { providerName, phases: { initialize, prepare, execute, collect, cleanup }, totalMs }
    this.data = data;
    this.render();
  }

  attachEvents() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      this.handleHover(x, y, e.clientX, e.clientY);
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.hoverInfo = null;
      globalTooltip.style.display = 'none';
      this.render();
    });

    window.addEventListener('resize', () => {
      if (this.data && this.data.length > 0) this.render();
    });
  }

  handleHover(mouseX, mouseY, screenX, screenY) {
    if (!this.segmentBounds) return;
    let found = null;
    for (const b of this.segmentBounds) {
      if (mouseX >= b.x && mouseX <= b.x + b.w && mouseY >= b.y && mouseY <= b.y + b.h) {
        found = b;
        break;
      }
    }

    if (found !== this.hoverInfo) {
      this.hoverInfo = found;
      this.render();
    }

    if (found) {
      const colors = ChartUtils.getThemeColors();
      globalTooltip.style.backgroundColor = colors.tooltipBg;
      globalTooltip.style.borderColor = colors.tooltipBorder;
      globalTooltip.style.border = `1px solid ${colors.tooltipBorder}`;
      globalTooltip.style.color = colors.text;

      const p = found.item.phases;
      const pct = found.item.totalMs > 0 ? ((found.val / found.item.totalMs) * 100).toFixed(1) : 0;

      globalTooltip.innerHTML = `
        <div style="font-weight:600; margin-bottom:4px;">${found.item.providerName}</div>
        <div style="font-size:11px; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
          <span style="width:8px; height:8px; border-radius:2px; background:${this.phaseColors[found.phase]}"></span>
          <strong>${found.phase.toUpperCase()}:</strong> ${ChartUtils.formatMs(found.val)} (${pct}%)
        </div>
        <hr style="border:none; border-top:1px solid ${colors.grid}; margin:6px 0;">
        <div style="font-size:11px; display:grid; grid-template-columns:1fr auto; gap:4px 12px;">
          <span>Init:</span><span>${ChartUtils.formatMs(p.initialize)}</span>
          <span>Prepare:</span><span>${ChartUtils.formatMs(p.prepare)}</span>
          <span>Execute:</span><span>${ChartUtils.formatMs(p.execute)}</span>
          <span>Collect:</span><span>${ChartUtils.formatMs(p.collect)}</span>
          <span>Cleanup:</span><span>${ChartUtils.formatMs(p.cleanup)}</span>
          <strong style="margin-top:4px;">Total Lifecycle:</strong><strong style="margin-top:4px;">${ChartUtils.formatMs(found.item.totalMs)}</strong>
        </div>
      `;
      globalTooltip.style.display = 'block';
      globalTooltip.style.left = `${screenX + 14}px`;
      globalTooltip.style.top = `${screenY - 10}px`;
    } else {
      globalTooltip.style.display = 'none';
    }
  }

  render() {
    const { ctx, width, height } = ChartUtils.setupCanvas(this.canvas);
    if (!this.data || this.data.length === 0) {
      ctx.fillStyle = ChartUtils.getThemeColors().textMuted;
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No phase timing data available', width / 2, height / 2);
      return;
    }

    const theme = ChartUtils.getThemeColors();
    const padding = { top: 16, right: 30, bottom: 20, left: 160 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    const maxTotal = Math.max(...this.data.map(d => d.totalMs || 10), 10) * 1.1;

    // Draw vertical background grid lines
    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.grid;
    ctx.fillStyle = theme.textMuted;
    ctx.font = '11px monospace';
    ctx.textAlign = 'center';

    for (let i = 0; i <= 5; i++) {
      const val = (maxTotal / 5) * i;
      const x = padding.left + (chartW / 5) * i;
      ctx.beginPath();
      ctx.moveTo(x, padding.top);
      ctx.lineTo(x, padding.top + chartH);
      ctx.stroke();

      const label = val >= 1000 ? `${(val / 1000).toFixed(1)}s` : `${Math.round(val)}ms`;
      ctx.fillText(label, x, padding.top + chartH + 16);
    }

    // Horizontal stacked bars
    const n = this.data.length;
    const barH = Math.min(chartH / n * 0.68, 28);
    const step = chartH / n;
    this.segmentBounds = [];

    const phases = ['initialize', 'prepare', 'execute', 'collect', 'cleanup'];

    this.data.forEach((item, idx) => {
      const y = padding.top + step * idx + (step - barH) / 2;

      // Provider Label on Y Axis
      ctx.fillStyle = theme.text;
      ctx.font = '500 12px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(item.providerName, padding.left - 12, y + barH / 2 + 4);

      let currentX = padding.left;

      phases.forEach(phase => {
        const val = item.phases[phase] || 0;
        if (val <= 0) return;
        const segW = (val / maxTotal) * chartW;

        const isHovered = this.hoverInfo && this.hoverInfo.item === item && this.hoverInfo.phase === phase;

        ctx.fillStyle = this.phaseColors[phase];
        if (isHovered) {
          ctx.shadowColor = this.phaseColors[phase];
          ctx.shadowBlur = 8;
        } else {
          ctx.shadowBlur = 0;
        }

        ctx.fillRect(currentX, y, segW, barH);
        ctx.shadowBlur = 0;

        this.segmentBounds.push({
          x: currentX,
          y,
          w: segW,
          h: barH,
          phase,
          val,
          item
        });

        currentX += segW;
      });

      // Total label at the end of bar
      ctx.fillStyle = theme.textMuted;
      ctx.font = '11px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(ChartUtils.formatMs(item.totalMs), currentX + 8, y + barH / 2 + 4);
    });
  }
}

/**
 * 3. Cost vs Latency Pareto Frontier Scatter / Bubble Plot
 */
class ScatterBubblePlot {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    this.options = Object.assign({
      title: 'Cost vs Latency Trade-Off',
      xLog: true,
      yLog: true,
      onPointClick: null
    }, options);
    this.points = [];
    this.hoverPoint = null;
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chart-wrapper">
        <canvas class="chart-canvas"></canvas>
      </div>
    `;
    this.canvas = this.container.querySelector('canvas');
    this.attachEvents();
  }

  setData(points) {
    // Array of { label, provider, suite, x: latencyMs, y: costUsd, size, color, meta }
    this.points = points.filter(p => p.x > 0 && p.y > 0);
    this.render();
  }

  attachEvents() {
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      this.handleHover(x, y, e.clientX, e.clientY);
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.hoverPoint = null;
      globalTooltip.style.display = 'none';
      this.render();
    });

    this.canvas.addEventListener('click', () => {
      if (this.hoverPoint && this.options.onPointClick) {
        this.options.onPointClick(this.hoverPoint);
      }
    });

    window.addEventListener('resize', () => {
      if (this.points.length > 0) this.render();
    });
  }

  handleHover(mouseX, mouseY, screenX, screenY) {
    if (!this.renderedPoints) return;
    let found = null;
    let minDist = 14;

    for (const p of this.renderedPoints) {
      const dist = Math.hypot(mouseX - p.screenX, mouseY - p.screenY);
      if (dist < minDist + p.radius) {
        minDist = dist;
        found = p;
      }
    }

    if (found !== this.hoverPoint) {
      this.hoverPoint = found;
      this.render();
    }

    if (found) {
      const colors = ChartUtils.getThemeColors();
      globalTooltip.style.backgroundColor = colors.tooltipBg;
      globalTooltip.style.borderColor = colors.tooltipBorder;
      globalTooltip.style.border = `1px solid ${colors.tooltipBorder}`;
      globalTooltip.style.color = colors.text;

      globalTooltip.innerHTML = `
        <div style="font-weight:600; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
          <span style="width:10px; height:10px; border-radius:50%; background:${found.color};"></span>
          ${found.providerName}
        </div>
        <div style="font-size:11px; color:${colors.textMuted}; margin-bottom:6px;">Suite: ${found.suiteName || found.suite}</div>
        <div style="display:flex; justify-content:space-between; gap:16px;">
          <span>Latency (p50):</span><strong>${ChartUtils.formatMs(found.x)}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; gap:16px;">
          <span>Estimated Cost:</span><strong>${ChartUtils.formatCost(found.y)}</strong>
        </div>
        ${found.passRate !== undefined ? `<div style="display:flex; justify-content:space-between; gap:16px;"><span>Pass Rate:</span><strong>${(found.passRate * 100).toFixed(0)}%</strong></div>` : ''}
      `;
      globalTooltip.style.display = 'block';
      globalTooltip.style.left = `${screenX + 14}px`;
      globalTooltip.style.top = `${screenY - 10}px`;
    } else {
      globalTooltip.style.display = 'none';
    }
  }

  render() {
    const { ctx, width, height } = ChartUtils.setupCanvas(this.canvas);
    if (!this.points || this.points.length === 0) {
      ctx.fillStyle = ChartUtils.getThemeColors().textMuted;
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No cost & latency points to plot', width / 2, height / 2);
      return;
    }

    const theme = ChartUtils.getThemeColors();
    const padding = { top: 24, right: 30, bottom: 50, left: 74 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Log scales
    const xVals = this.points.map(p => p.x);
    const yVals = this.points.map(p => p.y);

    const minX = Math.min(...xVals) * 0.7;
    const maxX = Math.max(...xVals) * 1.4;
    const minY = Math.min(...yVals) * 0.7;
    const maxY = Math.max(...yVals) * 1.5;

    const logMinX = Math.log10(minX);
    const logMaxX = Math.log10(maxX);
    const logMinY = Math.log10(minY);
    const logMaxY = Math.log10(maxY);

    const getScreenX = (val) => padding.left + ((Math.log10(val) - logMinX) / (logMaxX - logMinX)) * chartW;
    const getScreenY = (val) => padding.top + chartH - ((Math.log10(val) - logMinY) / (logMaxY - logMinY)) * chartH;

    // Grid lines for X (Log powers of 10)
    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.grid;
    ctx.fillStyle = theme.textMuted;
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';

    const xDecades = [10, 50, 100, 500, 1000, 5000, 10000, 50000];
    xDecades.forEach(v => {
      if (v >= minX && v <= maxX) {
        const sx = getScreenX(v);
        ctx.beginPath();
        ctx.moveTo(sx, padding.top);
        ctx.lineTo(sx, padding.top + chartH);
        ctx.stroke();
        ctx.fillText(v >= 1000 ? `${v / 1000}s` : `${v}ms`, sx, padding.top + chartH + 16);
      }
    });

    // Grid lines for Y (Log powers of 10)
    ctx.textAlign = 'right';
    const yDecades = [0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1];
    yDecades.forEach(v => {
      if (v >= minY && v <= maxY) {
        const sy = getScreenY(v);
        ctx.beginPath();
        ctx.moveTo(padding.left, sy);
        ctx.lineTo(padding.left + chartW, sy);
        ctx.stroke();
        ctx.fillText(`$${v < 0.001 ? v.toExponential(0) : v.toFixed(3)}`, padding.left - 8, sy + 4);
      }
    });

    // Axis Labels
    ctx.fillText('Latency (p50, log scale)', padding.left + chartW / 2 + 30, padding.top + chartH + 36);

    ctx.save();
    ctx.translate(16, padding.top + chartH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillText('Cost / Execution ($ USD, log scale)', 0, 0);
    ctx.restore();

    // Render Points
    this.renderedPoints = [];

    // Draw Pareto boundary curve if we can find optimal points
    const sorted = [...this.points].sort((a, b) => a.x - b.x);
    const pareto = [];
    let minCost = Infinity;
    for (const p of sorted) {
      if (p.y < minCost) {
        pareto.push(p);
        minCost = p.y;
      }
    }

    if (pareto.length > 1) {
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.35)';
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();
      pareto.forEach((p, idx) => {
        const sx = getScreenX(p.x);
        const sy = getScreenY(p.y);
        if (idx === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }

    this.points.forEach((p) => {
      const sx = getScreenX(p.x);
      const sy = getScreenY(p.y);
      const radius = Math.min(Math.max((p.size || 1) * 3, 6), 14);

      const isHovered = this.hoverPoint && this.hoverPoint === p;

      ctx.save();
      if (isHovered) {
        ctx.shadowColor = p.color;
        ctx.shadowBlur = 14;
      }

      ctx.beginPath();
      ctx.arc(sx, sy, isHovered ? radius + 3 : radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = isHovered ? 1.0 : 0.85;
      ctx.fill();

      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#ffffff';
      ctx.stroke();
      ctx.restore();

      this.renderedPoints.push({
        ...p,
        screenX: sx,
        screenY: sy,
        radius
      });
    });
  }
}

/**
 * 4. Multi-Pillar Provider Radar Chart (Spider Web)
 */
class RadarChart {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    this.options = Object.assign({
      title: 'Sandbox Capability Spectrum',
      axes: ['Speed', 'Reliability', 'Throughput', 'Cost Efficiency', 'Customization', 'Security & EU'],
    }, options);
    this.datasets = [];
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chart-wrapper">
        <canvas class="chart-canvas"></canvas>
      </div>
    `;
    this.canvas = this.container.querySelector('canvas');
  }

  setDatasets(datasets) {
    // Array of { name, color, values: [0-100, 0-100, ... for each axis] }
    this.datasets = datasets;
    this.render();
  }

  render() {
    const { ctx, width, height } = ChartUtils.setupCanvas(this.canvas);
    if (!this.datasets || this.datasets.length === 0) return;

    const theme = ChartUtils.getThemeColors();
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(centerX, centerY) - 45;
    const axes = this.options.axes;
    const numAxes = axes.length;

    // Draw concentric polygons
    const levels = 4;
    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.grid;

    for (let l = 1; l <= levels; l++) {
      const r = (radius / levels) * l;
      ctx.beginPath();
      for (let i = 0; i < numAxes; i++) {
        const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
        const x = centerX + Math.cos(angle) * r;
        const y = centerY + Math.sin(angle) * r;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.stroke();
    }

    // Draw axis spokes and labels
    ctx.fillStyle = theme.textMuted;
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';

    for (let i = 0; i < numAxes; i++) {
      const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;

      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();

      // Axis label offset
      const labelX = centerX + Math.cos(angle) * (radius + 20);
      const labelY = centerY + Math.sin(angle) * (radius + 16) + 4;
      ctx.fillText(axes[i], labelX, labelY);
    }

    // Draw datasets
    this.datasets.forEach((ds) => {
      ctx.beginPath();
      for (let i = 0; i < numAxes; i++) {
        const val = Math.max(Math.min(ds.values[i] || 0, 100), 0) / 100;
        const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
        const x = centerX + Math.cos(angle) * (radius * val);
        const y = centerY + Math.sin(angle) * (radius * val);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();

      // Fill area with transparency
      ctx.fillStyle = ds.color.replace(')', ', 0.18)').replace('rgb', 'rgba');
      ctx.fill();

      // Outline stroke
      ctx.lineWidth = 2;
      ctx.strokeStyle = ds.color;
      ctx.stroke();

      // Data points
      for (let i = 0; i < numAxes; i++) {
        const val = Math.max(Math.min(ds.values[i] || 0, 100), 0) / 100;
        const angle = (Math.PI * 2 / numAxes) * i - Math.PI / 2;
        const x = centerX + Math.cos(angle) * (radius * val);
        const y = centerY + Math.sin(angle) * (radius * val);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = ds.color;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });
  }
}

/**
 * 5. Scale & Burst Throughput Curve (Line Chart)
 */
class ThroughputScaleChart {
  constructor(containerId, options = {}) {
    this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
    this.options = Object.assign({
      yLabel: 'Completions / Second',
      xLabel: 'Independent Workers (Concurrency)'
    }, options);
    this.series = [];
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chart-wrapper">
        <canvas class="chart-canvas"></canvas>
      </div>
    `;
    this.canvas = this.container.querySelector('canvas');
  }

  setSeries(series) {
    // Array of { name, color, points: [ { x: concurrency, y: completionsPerSec } ] }
    this.series = series;
    this.render();
  }

  render() {
    const { ctx, width, height } = ChartUtils.setupCanvas(this.canvas);
    if (!this.series || this.series.length === 0) return;

    const theme = ChartUtils.getThemeColors();
    const padding = { top: 24, right: 30, bottom: 48, left: 60 };
    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Determine scale limits
    let maxX = 1;
    let maxY = 1;
    this.series.forEach(s => {
      s.points.forEach(p => {
        if (p.x > maxX) maxX = p.x;
        if (p.y > maxY) maxY = p.y;
      });
    });
    maxX = Math.max(maxX, 16);
    maxY = maxY * 1.2;

    // Draw horizontal grid lines
    ctx.lineWidth = 1;
    ctx.strokeStyle = theme.grid;
    ctx.fillStyle = theme.textMuted;
    ctx.font = '11px monospace';
    ctx.textAlign = 'right';

    for (let i = 0; i <= 5; i++) {
      const val = (maxY / 5) * i;
      const y = padding.top + chartH - (chartH / 5) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();
      ctx.fillText(val.toFixed(1), padding.left - 8, y + 4);
    }

    // Draw vertical grid lines
    ctx.textAlign = 'center';
    const xSteps = [1, 2, 4, 8, 12, 16];
    xSteps.forEach(workers => {
      if (workers <= maxX) {
        const x = padding.left + (workers / maxX) * chartW;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, padding.top + chartH);
        ctx.stroke();
        ctx.fillText(`${workers}x`, x, padding.top + chartH + 18);
      }
    });

    // Labels
    ctx.fillStyle = theme.textMuted;
    ctx.font = '12px sans-serif';
    ctx.fillText(this.options.xLabel, padding.left + chartW / 2, padding.top + chartH + 38);

    ctx.save();
    ctx.translate(16, padding.top + chartH / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText(this.options.yLabel, 0, 0);
    ctx.restore();

    // Draw line series
    this.series.forEach(s => {
      if (!s.points || s.points.length === 0) return;
      const sorted = [...s.points].sort((a, b) => a.x - b.x);

      ctx.strokeStyle = s.color;
      ctx.lineWidth = 3;
      ctx.beginPath();

      sorted.forEach((p, idx) => {
        const sx = padding.left + (p.x / maxX) * chartW;
        const sy = padding.top + chartH - (p.y / maxY) * chartH;
        if (idx === 0) ctx.moveTo(sx, sy);
        else ctx.lineTo(sx, sy);
      });
      ctx.stroke();

      // Points
      sorted.forEach(p => {
        const sx = padding.left + (p.x / maxX) * chartW;
        const sy = padding.top + chartH - (p.y / maxY) * chartH;

        ctx.beginPath();
        ctx.arc(sx, sy, 5, 0, Math.PI * 2);
        ctx.fillStyle = s.color;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });
    });
  }
}

// Export global chart classes
window.ChartUtils = ChartUtils;
window.BarChart = BarChart;
window.PhaseStackedChart = PhaseStackedChart;
window.ScatterBubblePlot = ScatterBubblePlot;
window.RadarChart = RadarChart;
window.ThroughputScaleChart = ThroughputScaleChart;
