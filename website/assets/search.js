(() => {
  'use strict';

  const PAGE_SIZE = 20;
  const form = document.getElementById('search-form');
  const input = document.getElementById('search-input');
  const list = document.getElementById('results-list');
  const region = document.getElementById('results-region');
  const message = document.getElementById('state-message');
  const summary = document.getElementById('results-summary');
  const title = document.getElementById('results-title');
  const pagination = document.getElementById('pagination');
  const previous = document.getElementById('previous-page');
  const next = document.getElementById('next-page');
  const pageSummary = document.getElementById('page-summary');
  const dialog = document.getElementById('entry-dialog');
  const detail = document.getElementById('entry-detail');
  const initialParams = new URLSearchParams(window.location.search);
  let query = initialParams.get('q')?.slice(0, 200).trim() || '';
  let source = ['all', 'simeon', 'kaikki'].includes(initialParams.get('source')) ? initialParams.get('source') : 'all';
  let offset = Math.max(0, Number.parseInt(initialParams.get('offset'), 10) || 0);
  let total = 0;
  let timer;
  let controller;
  let requestNumber = 0;

  // Source text is always rendered as text, including definitions and citations.
  function text(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string') return value;
    if (Array.isArray(value)) return value.map(text).filter(Boolean).join('; ');
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }

  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = text(value);
    return node;
  }

  function sourceLabel(entry) {
    return text(entry.sourceLabel) || (text(entry.source).toLowerCase().includes('simeon') ? 'Rémi Siméon' : 'Wiktionary / Kaikki');
  }

  function definitions(entry) {
    return [
      { value: text(entry.definitionFr), label: 'French · Original definition', language: 'fr' },
      { value: text(entry.definitionEn), label: 'English definition', language: 'en' },
      { value: text(entry.definitionEs), label: 'Spanish definition', language: 'es' }
    ].filter(definition => definition.value.trim());
  }

  function safeSourceUrl(value) {
    try {
      const url = new URL(text(value));
      return ['https:', 'http:'].includes(url.protocol) ? url.href : '';
    } catch {
      return '';
    }
  }

  function metadataRow(parent, label, value) {
    if (!text(value).trim()) return;
    parent.append(element('dt', '', label), element('dd', '', value));
  }

  function definitionSection(parent, definition) {
    const section = element('section', 'detail-section');
    section.append(element('h3', '', definition.label));
    const paragraph = element('p', 'full-definition', definition.value);
    paragraph.lang = definition.language;
    section.append(paragraph);
    parent.append(section);
  }

  function chipsSection(parent, label, values) {
    if (!Array.isArray(values) || !values.length) return;
    const clean = values.map(text).filter(value => value.trim());
    if (!clean.length) return;
    const section = element('section', 'detail-section');
    const chips = element('div', 'detail-chip-list');
    clean.forEach(value => chips.append(element('span', 'detail-chip', value)));
    section.append(element('h3', '', label), chips);
    parent.append(section);
  }

  function openEntry(entry) {
    detail.replaceChildren();
    const heading = element('h2', 'detail-title', entry.headword || 'Untitled entry');
    heading.id = 'entry-title';
    heading.lang = 'nah';
    detail.append(heading, element('p', 'detail-source', `${sourceLabel(entry)}${entry.pos ? ' · ' + text(entry.pos) : ''}`));
    const availableDefinitions = definitions(entry);
    if (availableDefinitions.length) availableDefinitions.forEach(definition => definitionSection(detail, definition));
    else definitionSection(detail, { label: 'Definition', value: 'No definition is recorded for this entry.', language: 'en' });

    chipsSection(detail, 'Recorded variants', entry.variants);
    chipsSection(detail, 'Recorded roots', entry.roots);

    const provenance = element('section', 'detail-section');
    const metadata = element('dl', 'detail-metadata');
    metadataRow(metadata, 'Original headword', entry.headword);
    metadataRow(metadata, 'Source', sourceLabel(entry));
    metadataRow(metadata, 'Language variety', entry.variety);
    metadataRow(metadata, 'Part of speech', entry.pos);
    metadataRow(metadata, 'Citation', entry.citation);
    metadataRow(metadata, 'Source reference', entry.sourceReference);
    metadataRow(metadata, 'Record status', entry.status);
    metadataRow(metadata, 'Entry ID', entry.id);
    const sourceUrl = safeSourceUrl(entry.sourceUrl);
    if (sourceUrl) {
      const value = element('dd');
      const link = element('a', '', 'Open the source ↗');
      link.href = sourceUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      value.append(link);
      metadata.append(element('dt', '', 'Source link'), value);
    }
    provenance.append(element('h3', '', 'Source & provenance'), metadata);
    detail.append(provenance);

    if (entry.msn && [entry.msn.headword, entry.msn.poeticForm, entry.msn.spokenForm].some(value => text(value).trim())) {
      const modern = element('details', 'msn-details');
      const modernMetadata = element('dl', 'detail-metadata');
      metadataRow(modernMetadata, 'MSN form', entry.msn.headword);
      metadataRow(modernMetadata, 'Poetic form', entry.msn.poeticForm);
      metadataRow(modernMetadata, 'Spoken form', entry.msn.spokenForm);
      modern.append(element('summary', '', 'Related Modern Standard Nahuatl fields'), element('p', '', 'These project fields provide modern context alongside the source record.'), modernMetadata);
      detail.append(modern);
    }
    dialog.showModal();
    dialog.scrollTop = 0;
  }

  function renderEntries(entries) {
    const fragment = document.createDocumentFragment();
    entries.forEach(entry => {
      const row = element('button', 'entry-row');
      row.type = 'button';
      const word = text(entry.headword) || 'Untitled entry';
      row.setAttribute('aria-label', `Read ${word}, ${sourceLabel(entry)}`);
      const wordColumn = element('span');
      const headword = element('span', 'entry-word', word);
      headword.lang = 'nah';
      wordColumn.append(headword);
      if (entry.pos) wordColumn.append(element('span', 'entry-pos', entry.pos));
      const definitionColumn = element('span', 'entry-definition');
      const definition = definitions(entry)[0];
      const preview = element('span', 'definition-preview', definition?.value || 'No definition recorded.');
      if (definition) preview.lang = definition.language;
      definitionColumn.append(preview);
      if (definition) definitionColumn.append(element('span', 'definition-language', definition.language === 'fr' ? 'French' : definition.language === 'en' ? 'English' : 'Spanish'));
      const sourceColumn = element('span', 'entry-source');
      sourceColumn.append(element('span', 'source-label', sourceLabel(entry)), element('span', 'entry-open', 'Read entry ↗'));
      row.append(wordColumn, definitionColumn, sourceColumn);
      row.addEventListener('click', () => openEntry(entry));
      fragment.append(row);
    });
    list.replaceChildren(fragment);
  }

  function showMessage(heading, body, retry) {
    message.replaceChildren(element('h4', '', heading), element('p', '', body));
    if (retry) {
      const retryButton = element('button', 'retry-button', 'Try again');
      retryButton.type = 'button';
      retryButton.addEventListener('click', () => loadEntries());
      message.append(retryButton);
    }
    message.hidden = false;
  }

  function updateAddress() {
    const url = new URL(window.location.href);
    if (query) url.searchParams.set('q', query); else url.searchParams.delete('q');
    if (source !== 'all') url.searchParams.set('source', source); else url.searchParams.delete('source');
    if (offset) url.searchParams.set('offset', String(offset)); else url.searchParams.delete('offset');
    window.history.replaceState(null, '', url);
  }

  async function loadEntries(scrollToResults = false) {
    controller?.abort();
    controller = new AbortController();
    const request = ++requestNumber;
    region.setAttribute('aria-busy', 'true');
    summary.textContent = 'Loading entries…';
    title.textContent = query ? `Results for “${query}”` : 'Browse the collection';
    message.hidden = true;
    pagination.hidden = true;
    updateAddress();

    try {
      const url = new URL(window.AMOXCALLI_SEARCH_API || '/api/search', window.location.origin);
      url.searchParams.set('q', query);
      url.searchParams.set('source', source);
      url.searchParams.set('offset', String(offset));
      url.searchParams.set('limit', String(PAGE_SIZE));
      const response = await fetch(url, { signal: controller.signal, headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error('Search request failed');
      const data = await response.json();
      if (!Array.isArray(data.entries) || !Number.isFinite(Number(data.total))) throw new Error('Invalid search response');
      if (request !== requestNumber) return;
      total = Math.max(0, Number(data.total));
      offset = Math.max(0, Number(data.offset) || 0);
      const entries = data.entries.slice(0, 50);
      if (offset >= total && total > 0) {
        offset = Math.floor((total - 1) / PAGE_SIZE) * PAGE_SIZE;
        return loadEntries(scrollToResults);
      }
      renderEntries(entries);
      const first = total ? offset + 1 : 0;
      const last = Math.min(offset + entries.length, total);
      summary.textContent = total ? `${first.toLocaleString()}–${last.toLocaleString()} of ${total.toLocaleString()} ${total === 1 ? 'entry' : 'entries'}` : 'No entries found';
      if (!entries.length) showMessage('No matching entries.', 'Try another spelling, a shorter word, or a term in the French or English definitions. You can also choose All sources.');
      pagination.hidden = total <= PAGE_SIZE;
      previous.disabled = offset === 0;
      next.disabled = last >= total;
      pageSummary.textContent = `Page ${Math.floor(offset / PAGE_SIZE) + 1} of ${Math.max(1, Math.ceil(total / PAGE_SIZE)).toLocaleString()}`;
      if (scrollToResults) {
        title.tabIndex = -1;
        title.focus({ preventScroll: true });
        title.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      }
    } catch (error) {
      if (error.name === 'AbortError' || request !== requestNumber) return;
      list.replaceChildren();
      summary.textContent = 'Search is temporarily unavailable';
      showMessage('The archive couldn’t be reached.', 'Please try again in a moment. The complete collection is also available through the database download below.', true);
    } finally {
      if (request === requestNumber) region.setAttribute('aria-busy', 'false');
    }
  }

  function searchNow() {
    clearTimeout(timer);
    query = input.value.trim().slice(0, 200);
    source = form.querySelector('input[name="source"]:checked').value;
    offset = 0;
    loadEntries();
  }

  form.addEventListener('submit', event => { event.preventDefault(); searchNow(); });
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(searchNow, 350); });
  form.querySelectorAll('input[name="source"]').forEach(radio => radio.addEventListener('change', searchNow));
  previous.addEventListener('click', () => { offset = Math.max(0, offset - PAGE_SIZE); loadEntries(true); });
  next.addEventListener('click', () => { if (offset + PAGE_SIZE < total) { offset += PAGE_SIZE; loadEntries(true); } });
  document.getElementById('close-entry').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  input.value = query;
  form.querySelector(`input[name="source"][value="${source}"]`).checked = true;
  loadEntries();
})();
