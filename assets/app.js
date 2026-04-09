// --- Shared helpers ---
function normalize(str) {
  return (str || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function stripFrontmatter(md) {
  return md.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
}

function parseFrontmatter(md) {
  var match = md.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  var data = {};
  match[1].split('\n').forEach(function(line) {
    var kv = line.match(/^(\w[\w_]*):\s*(.*)/);
    if (!kv) return;
    var val = kv[2].trim().replace(/^["']|["']$/g, '');
    data[kv[1]] = val;
  });
  return data;
}

// --- Nav + search + filter ---
(function() {
  var cards = Array.prototype.slice.call(document.querySelectorAll('.content-card'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.content-section'));
  var searchInput = document.getElementById('search');
  var tabsContainer = document.getElementById('navTabs');
  var noResults = document.getElementById('noResults');
  var searchCount = document.getElementById('searchCount');
  var activeTab = tabsContainer.querySelector('.nav-tab.active');

  tabsContainer.querySelectorAll('.nav-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      if (activeTab) activeTab.classList.remove('active');
      tab.classList.add('active');
      activeTab = tab;
      applyFilters();
    });
  });

  searchInput.addEventListener('input', applyFilters);

  document.addEventListener('keydown', function(e) {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
  });

  function currentType() {
    return activeTab ? activeTab.getAttribute('data-type') : 'all';
  }

  function applyFilters() {
    var query = normalize(searchInput.value.trim());
    var target = currentType();
    var totalVisible = 0;
    var perSection = {};

    cards.forEach(function(card) {
      var type = card.getAttribute('data-type') || '';
      var name = normalize(card.getAttribute('data-name') || '');
      var text = normalize(card.textContent || '');
      var typeKey = card.closest('.content-section').getAttribute('data-section');
      var matchesType = target === 'all' || typeKey === target;
      var matchesSearch = !query || name.indexOf(query) !== -1 || text.indexOf(query) !== -1;
      if (matchesType && matchesSearch) {
        card.classList.remove('hidden');
        totalVisible++;
        perSection[typeKey] = (perSection[typeKey] || 0) + 1;
      } else {
        card.classList.add('hidden');
      }
    });

    sections.forEach(function(section) {
      var key = section.getAttribute('data-section');
      var show = (target === 'all' || target === key) && (perSection[key] || 0) > 0;
      section.classList.toggle('hidden', !show);
    });

    if (query) {
      searchCount.style.display = 'block';
      searchCount.textContent = totalVisible + ' result' + (totalVisible !== 1 ? 's' : '') + ' found';
    } else {
      searchCount.style.display = 'none';
    }
    noResults.style.display = totalVisible === 0 ? 'block' : 'none';
  }
})();

// --- Detail overlay with hash routing ---
(function() {
  var overlay = document.getElementById('detailOverlay');
  var body = document.getElementById('detailBody');
  var closeBtn = document.getElementById('detailClose');
  var backBtn = document.getElementById('detailBack');

  function openOverlay() {
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    overlay.scrollTop = 0;
  }

  function closeOverlay() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    if (location.hash) {
      history.pushState(null, '', location.pathname + location.search);
    }
  }

  closeBtn.addEventListener('click', closeOverlay);
  backBtn.addEventListener('click', closeOverlay);
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) closeOverlay();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && overlay.classList.contains('active')) closeOverlay();
  });

  function renderMeta(meta) {
    var parts = [];
    if (meta.stage)   parts.push('Stage: ' + meta.stage);
    if (meta.persona) parts.push('Persona: ' + meta.persona);
    if (meta.section_id) parts.push('§ ' + meta.section_id);
    if (meta.source) {
      var domain = meta.source.replace(/^https?:\/\//, '').split('/')[0];
      parts.push('<a href="' + meta.source + '" target="_blank" rel="noopener">' + domain + '</a>');
    }
    if (!parts.length) return '';
    return '<div class="detail-meta">' + parts.map(function(p) { return '<span>' + p + '</span>'; }).join('') + '</div>';
  }

  function loadMarkdown(href) {
    body.innerHTML = '<p style="color:var(--text-muted);font-style:italic;">Loading…</p>';
    openOverlay();
    fetch(href)
      .then(function(r) {
        if (!r.ok) throw new Error('Not found');
        return r.text();
      })
      .then(function(md) {
        var meta = parseFrontmatter(md);
        var content = stripFrontmatter(md);
        body.innerHTML = renderMeta(meta) + marked.parse(content);
      })
      .catch(function() {
        body.innerHTML = '<p style="color:#c0392b;">Could not load content.</p>';
      });
  }

  // Markdown-backed card clicks (modules, plan-sections, case-studies, glossary)
  document.addEventListener('click', function(e) {
    var link = e.target.closest('a[href$=".md"]');
    if (!link) return;
    e.preventDefault();
    var href = link.getAttribute('href');
    // Derive hash: type/slug where type is the enclosing folder
    var parts = href.split('/');
    var folder = parts[parts.length - 2];
    var slug = parts[parts.length - 1].replace(/\.md$/, '');
    history.pushState(null, '', '#' + folder + '/' + slug);
    loadMarkdown(href);
  });

  // Calculator card clicks — delegated to calculators.js via custom event
  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-calc-slug]');
    if (!btn) return;
    e.preventDefault();
    var slug = btn.getAttribute('data-calc-slug');
    history.pushState(null, '', '#calculators/' + slug);
    window.openCalculator && window.openCalculator(slug, body, openOverlay);
  });

  function handleHash() {
    var hash = location.hash.slice(1);
    if (!hash) {
      if (overlay.classList.contains('active')) closeOverlay();
      return;
    }
    var parts = hash.split('/');
    if (parts.length !== 2) return;
    var folder = parts[0];
    var slug = parts[1];
    if (folder === 'calculators') {
      openOverlay();
      window.openCalculator && window.openCalculator(slug, body, openOverlay);
    } else {
      loadMarkdown('content/' + folder + '/' + slug + '.md');
    }
  }

  window.addEventListener('popstate', handleHash);
  if (location.hash) handleHash();

  // Expose for calculators.js
  window._openDetailOverlay = openOverlay;
})();
