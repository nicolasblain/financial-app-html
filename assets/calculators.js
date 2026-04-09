// Client-side calculator runtime. Reads the embedded JSON manifest
// produced by builder.renderers.calculator.build_data().
(function() {
  var dataScript = document.getElementById('calculatorData');
  var CALCULATORS = {};
  try {
    CALCULATORS = JSON.parse(dataScript.textContent || '{}');
  } catch (e) {
    console.error('Failed to parse calculator data', e);
  }

  // Whitelist of allowed characters in a formula.
  // Permits: digits, identifiers (input names), operators, parens, Math.*, dots, commas, whitespace.
  var SAFE_FORMULA = /^[A-Za-z0-9_+\-*/().,\s]*$/;

  function compileFormula(formula, inputNames) {
    if (!SAFE_FORMULA.test(formula)) {
      throw new Error('Formula contains disallowed characters');
    }
    // Build a function from the input names. Math is available via the `Math` arg.
    var args = inputNames.concat(['Math']);
    // eslint-disable-next-line no-new-func
    return new Function(args.join(','), 'return (' + formula + ');');
  }

  function formatNumber(n) {
    if (!isFinite(n)) return String(n);
    if (Math.abs(n) >= 1000) {
      return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    return (Math.round(n * 100) / 100).toString();
  }

  function openCalculator(slug, container, openOverlay) {
    var calc = CALCULATORS[slug];
    if (!calc) {
      container.innerHTML = '<p style="color:#c0392b;">Unknown calculator: ' + slug + '</p>';
      return;
    }

    var inputs = calc.inputs || [];
    var labels = calc.labels && calc.labels.length ? calc.labels : inputs;
    var defaults = calc.defaults || [];

    var formFields = inputs.map(function(name, i) {
      var label = labels[i] || name;
      var val = defaults[i] != null ? defaults[i] : 0;
      return (
        '<div class="calc-field">' +
          '<label for="calc-' + slug + '-' + name + '">' + label + '</label>' +
          '<input type="number" step="any" id="calc-' + slug + '-' + name + '" ' +
          'name="' + name + '" value="' + val + '">' +
        '</div>'
      );
    }).join('');

    container.innerHTML =
      '<h1>' + calc.title + '</h1>' +
      (calc.summary ? '<p style="color:var(--text-secondary);">' + calc.summary + '</p>' : '') +
      '<form class="calc-form" id="calcForm">' + formFields + '</form>' +
      '<div class="calc-result" id="calcResult"></div>' +
      (calc.body ? '<div style="margin-top:1.5rem;">' + marked.parse(calc.body) + '</div>' : '');

    var form = container.querySelector('#calcForm');
    var resultEl = container.querySelector('#calcResult');

    var fn;
    try {
      fn = compileFormula(calc.formula, inputs);
    } catch (e) {
      resultEl.innerHTML = '<span class="calc-error">' + e.message + '</span>';
      return;
    }

    function recompute() {
      var values = inputs.map(function(name) {
        var el = form.querySelector('[name="' + name + '"]');
        return parseFloat(el.value) || 0;
      });
      try {
        var result = fn.apply(null, values.concat([Math]));
        var text = (calc.output || 'Result: {result}').replace('{result}', formatNumber(result));
        resultEl.textContent = text;
      } catch (e) {
        resultEl.innerHTML = '<span class="calc-error">' + e.message + '</span>';
      }
    }

    form.addEventListener('input', recompute);
    recompute();
  }

  window.openCalculator = openCalculator;
})();
