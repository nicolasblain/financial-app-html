// Client-side plan view. Reads the embedded JSON manifest produced by
// builder.renderers.plan_view.build_data() and renders a full-document
// view with a key-metrics panel + the plan narrative.
(function() {
  var dataScript = document.getElementById('planData');
  var PLANS = {};
  try {
    PLANS = JSON.parse(dataScript.textContent || '{}');
  } catch (e) {
    console.error('Failed to parse plan data', e);
  }

  function fmtDollar(v) {
    var n = parseFloat(v);
    if (isNaN(n)) return String(v);
    if (n < 0) return '-$ ' + Math.abs(n).toLocaleString(undefined, { maximumFractionDigits: 0 });
    return '$ ' + n.toLocaleString(undefined, { maximumFractionDigits: 0 });
  }

  function fmtPercent(v) {
    var n = parseFloat(v);
    if (isNaN(n)) return String(v);
    return n.toFixed(1) + ' %';
  }

  function fmtPlain(v) {
    return String(v);
  }

  function fmtValue(v, format) {
    if (format === '$') return fmtDollar(v);
    if (format === '%') return fmtPercent(v);
    return fmtPlain(v);
  }

  function renderMetricsGrid(metrics) {
    if (!metrics || !metrics.length) return '';
    var cells = metrics.map(function(m) {
      var formatted = fmtValue(m.value, m.format);
      var isNegative = parseFloat(m.value) < 0;
      var cls = 'plan-metric';
      if (isNegative) cls += ' plan-metric--negative';
      return (
        '<div class="' + cls + '">' +
          '<span class="plan-metric-value">' + formatted + '</span>' +
          '<span class="plan-metric-label">' + m.label + '</span>' +
        '</div>'
      );
    }).join('');
    return '<div class="plan-metrics-grid">' + cells + '</div>';
  }

  function renderHeader(plan) {
    var parts = [];
    if (plan.client) parts.push('<span>Client: <strong>' + plan.client + '</strong></span>');
    if (plan.date) parts.push('<span>Date: ' + plan.date + '</span>');
    if (plan.plan_status) {
      var s = plan.plan_status.toLowerCase();
      parts.push('<span class="plan-status plan-status--' + s + '">' + plan.plan_status + '</span>');
    }
    if (!parts.length) return '';
    return '<div class="plan-header-meta">' + parts.join('') + '</div>';
  }

  function renderFileHint(slug) {
    return (
      '<div class="plan-file-hint">' +
        'Source: <code>content/plans/' + slug + '.md</code>' +
      '</div>'
    );
  }

  function openPlanView(slug, container, openOverlay) {
    var plan = PLANS[slug];
    if (!plan) {
      container.innerHTML = '<p style="color:#c0392b;">Unknown plan: ' + slug + '</p>';
      openOverlay();
      return;
    }

    var html =
      '<div class="plan-view">' +
        '<h1>' + plan.title + '</h1>' +
        renderHeader(plan) +
        renderMetricsGrid(plan.metrics) +
        '<div class="plan-body">' + marked.parse(plan.body || '') + '</div>' +
        renderFileHint(slug) +
      '</div>';

    container.innerHTML = html;
    openOverlay();
  }

  window.openPlanView = openPlanView;
})();
