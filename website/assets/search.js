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
  const LANGUAGES = ['en', 'es', 'fr'];
  const LANGUAGE_NAMES = { en: 'English', es: 'Español', fr: 'Français' };
  const COPY = {
    en: { language: 'Definition language', original: 'Original definition', machine: 'Machine translation', definition: 'Definition', missing: 'The source has no recorded definition for this entry.', unavailable: 'The English definition is not available yet.', sourceMissing: 'No source definition', pending: 'Translation unavailable', originalToggle: 'Read the original definition', machineNote: 'Machine translation from {language}; not yet reviewed.', languageHelp: 'Original definitions and machine translations are labeled. Records without source text are identified.', searchHelp: 'Search words and definitions in English, Spanish, or French.', untitled: 'Untitled entry', read: 'Read', readEntry: 'Read entry ↗', loading: 'Loading entries…', browse: 'Browse the collection', results: 'Results for', entries: 'entries', entry: 'entry', foundNone: 'No entries found', empty: 'No matching entries.', emptyHelp: 'Try another spelling, a shorter word, or a term in any of the three definition languages. You can also choose All sources.', error: 'Search is temporarily unavailable', errorTitle: 'The archive couldn’t be reached.', errorHelp: 'Please try again in a moment. The complete collection is also available through the database download below.', retry: 'Try again', page: 'Page', of: 'of', previous: 'Previous', next: 'Next', variants: 'Recorded variants', roots: 'Recorded roots', provenance: 'Source & provenance', headword: 'Original headword', source: 'Source', variety: 'Language variety', pos: 'Part of speech', citation: 'Citation', reference: 'Source reference', status: 'Record status', id: 'Entry ID', sourceLink: 'Source link', openSource: 'Open the source ↗', modern: 'Related Modern Standard Nahuatl fields', modernNote: 'These project fields provide modern context alongside the source record.', msn: 'MSN form', poetic: 'Poetic form', spoken: 'Spoken form', close: 'Close', provider: 'Translation provider', model: 'Translation model', translationStatus: 'Translation status' },
    es: { language: 'Idioma de las definiciones', original: 'Definición original', machine: 'Traducción automática', definition: 'Definición', missing: 'La fuente no contiene una definición para esta entrada.', unavailable: 'La definición en español aún no está disponible.', sourceMissing: 'Sin definición en la fuente', pending: 'Traducción no disponible', originalToggle: 'Leer la definición original', machineNote: 'Traducción automática del {language}; aún no revisada.', languageHelp: 'Las definiciones originales y las traducciones automáticas están identificadas. Se indican las entradas sin texto en la fuente.', searchHelp: 'Busca palabras y definiciones en inglés, español o francés.', untitled: 'Entrada sin título', read: 'Leer', readEntry: 'Leer entrada ↗', loading: 'Cargando entradas…', browse: 'Explorar la colección', results: 'Resultados para', entries: 'entradas', entry: 'entrada', foundNone: 'No se encontraron entradas', empty: 'No hay entradas coincidentes.', emptyHelp: 'Prueba otra grafía, una palabra más corta o un término en cualquiera de los tres idiomas. También puedes elegir todas las fuentes.', error: 'La búsqueda no está disponible temporalmente', errorTitle: 'No se pudo acceder al archivo.', errorHelp: 'Inténtalo de nuevo en un momento. También puedes descargar la colección completa mediante el enlace a la base de datos.', retry: 'Intentar de nuevo', page: 'Página', of: 'de', previous: 'Anterior', next: 'Siguiente', variants: 'Variantes registradas', roots: 'Raíces registradas', provenance: 'Fuente y procedencia', headword: 'Forma original', source: 'Fuente', variety: 'Variedad lingüística', pos: 'Categoría gramatical', citation: 'Cita', reference: 'Referencia de la fuente', status: 'Estado del registro', id: 'ID de la entrada', sourceLink: 'Enlace a la fuente', openSource: 'Abrir la fuente ↗', modern: 'Campos relacionados con el Náhuatl Estándar Moderno', modernNote: 'Estos campos del proyecto aportan contexto moderno junto al registro de la fuente.', msn: 'Forma MSN', poetic: 'Forma poética', spoken: 'Forma hablada', close: 'Cerrar', provider: 'Proveedor de la traducción', model: 'Modelo de la traducción', translationStatus: 'Estado de la traducción' },
    fr: { language: 'Langue des définitions', original: 'Définition originale', machine: 'Traduction automatique', definition: 'Définition', missing: 'La source ne contient pas de définition pour cette entrée.', unavailable: 'La définition en français n’est pas encore disponible.', sourceMissing: 'Aucune définition dans la source', pending: 'Traduction indisponible', originalToggle: 'Lire la définition originale', machineNote: 'Traduction automatique depuis le {language} ; pas encore révisée.', languageHelp: 'Les définitions originales et les traductions automatiques sont identifiées. Les entrées sans texte source sont signalées.', searchHelp: 'Recherchez des mots et des définitions en anglais, espagnol ou français.', untitled: 'Entrée sans titre', read: 'Lire', readEntry: 'Lire l’entrée ↗', loading: 'Chargement des entrées…', browse: 'Explorer la collection', results: 'Résultats pour', entries: 'entrées', entry: 'entrée', foundNone: 'Aucune entrée trouvée', empty: 'Aucune entrée correspondante.', emptyHelp: 'Essayez une autre graphie, un mot plus court ou un terme dans l’une des trois langues. Vous pouvez aussi choisir toutes les sources.', error: 'La recherche est temporairement indisponible', errorTitle: 'Impossible de joindre les archives.', errorHelp: 'Veuillez réessayer dans un instant. La collection complète est également disponible via le lien de téléchargement de la base de données.', retry: 'Réessayer', page: 'Page', of: 'sur', previous: 'Précédent', next: 'Suivant', variants: 'Variantes enregistrées', roots: 'Racines enregistrées', provenance: 'Source et provenance', headword: 'Forme originale', source: 'Source', variety: 'Variété linguistique', pos: 'Catégorie grammaticale', citation: 'Citation', reference: 'Référence de la source', status: 'État de l’entrée', id: 'ID de l’entrée', sourceLink: 'Lien vers la source', openSource: 'Ouvrir la source ↗', modern: 'Champs associés au nahuatl standard moderne', modernNote: 'Ces champs du projet apportent un contexte moderne à côté de l’entrée source.', msn: 'Forme MSN', poetic: 'Forme poétique', spoken: 'Forme parlée', close: 'Fermer', provider: 'Fournisseur de traduction', model: 'Modèle de traduction', translationStatus: 'État de la traduction' }
  };
  Object.assign(COPY.en, { unclear: 'The source definition is unreadable.', sourceUnclear: 'Unreadable source definition', transcription: 'View the original source transcription', languageHelp: 'Original definitions and machine translations are labeled. Missing or unreadable source definitions are identified.' });
  Object.assign(COPY.es, { unclear: 'La definición de la fuente es ilegible.', sourceUnclear: 'Definición ilegible en la fuente', transcription: 'Ver la transcripción original de la fuente', languageHelp: 'Se identifican las definiciones originales, las traducciones automáticas y las definiciones ausentes o ilegibles en la fuente.' });
  Object.assign(COPY.fr, { unclear: 'La définition de la source est illisible.', sourceUnclear: 'Définition source illisible', transcription: 'Voir la transcription originale de la source', languageHelp: 'Les définitions originales, les traductions automatiques et les définitions absentes ou illisibles dans la source sont identifiées.', machineNote: 'Traduction automatique, source : {language} ; pas encore révisée.' });
  let savedLanguage;
  try { savedLanguage = window.localStorage.getItem('amoxcalli.definitionLanguage'); } catch { /* Storage can be unavailable in private browsing. */ }
  let language = LANGUAGES.includes(initialParams.get('lang')) ? initialParams.get('lang') : LANGUAGES.includes(savedLanguage) ? savedLanguage : 'en';
  let query = initialParams.get('q')?.slice(0, 200).trim() || '';
  let source = ['all', 'simeon', 'kaikki'].includes(initialParams.get('source')) ? initialParams.get('source') : 'all';
  let offset = Math.max(0, Number.parseInt(initialParams.get('offset'), 10) || 0);
  let total = 0;
  let timer;
  let controller;
  let requestNumber = 0;
  let currentEntries = [];
  let currentEntry = null;
  let resultState = 'loading';

  function copy(key) { return COPY[language][key]; }

  function localizedLanguage(code) {
    const names = { en: { en: 'English', es: 'Spanish', fr: 'French' }, es: { en: 'inglés', es: 'español', fr: 'francés' }, fr: { en: 'anglais', es: 'espagnol', fr: 'français' } };
    return names[language][code] || code;
  }

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

  function definitionIn(entry, selectedLanguage) {
    const fields = { fr: 'definitionFr', en: 'definitionEn', es: 'definitionEs' };
    const value = text(entry[fields[selectedLanguage]]);
    const metadata = entry.translations?.[selectedLanguage] || {};
    const originalLanguage = text(metadata.sourceLanguage) || (text(entry.source).toLowerCase().includes('simeon') ? 'fr' : 'en');
    const missingSource = entry.sourceDefinitionMissing === true || metadata.kind === 'source_missing';
    const unclearSource = entry.sourceDefinitionUnclear === true || metadata.kind === 'source_unclear';
    const kind = metadata.kind || (selectedLanguage === originalLanguage ? 'original' : 'unknown');
    return { value: missingSource ? copy('missing') : unclearSource ? copy('unclear') : value.trim() ? value : copy('unavailable'), language: selectedLanguage, metadata, kind, originalLanguage, missingSource, unclearSource, available: !missingSource && !unclearSource && Boolean(value.trim()), label: missingSource ? copy('sourceMissing') : unclearSource ? copy('sourceUnclear') : !value.trim() ? copy('pending') : kind === 'original' ? copy('original') : kind === 'machine' ? copy('machine') : copy('definition') };
  }

  function languageSelector(name) {
    const fieldset = element('fieldset', 'language-filter');
    fieldset.append(element('legend', '', copy('language')));
    LANGUAGES.forEach(code => {
      const label = element('label');
      const radio = element('input');
      radio.type = 'radio';
      radio.name = name;
      radio.value = code;
      radio.checked = code === language;
      const caption = element('span', '', LANGUAGE_NAMES[code]);
      caption.lang = code;
      label.append(radio, caption);
      fieldset.append(label);
      radio.addEventListener('change', () => changeLanguage(code, true));
    });
    return fieldset;
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
    section.append(element('h3', '', `${LANGUAGE_NAMES[definition.language]} · ${definition.label}`));
    const paragraph = element('p', `full-definition${definition.available ? '' : ' definition-unavailable'}`, definition.value);
    paragraph.lang = definition.language;
    section.append(paragraph);
    if (definition.kind === 'machine' && definition.available) {
      section.append(element('p', 'translation-provenance', copy('machineNote').replace('{language}', localizedLanguage(definition.originalLanguage))));
    }
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

  function renderEntry(entry) {
    detail.replaceChildren();
    const heading = element('h2', 'detail-title', entry.headword || copy('untitled'));
    heading.id = 'entry-title';
    heading.lang = 'nah';
    detail.append(heading, element('p', 'detail-source', `${sourceLabel(entry)}${entry.pos ? ' · ' + text(entry.pos) : ''}`));
    const controls = element('div', 'entry-language-controls');
    controls.append(languageSelector('entry-language'));
    detail.append(controls);
    const definition = definitionIn(entry, language);
    definitionSection(detail, definition);
    if (!definition.missingSource && (definition.originalLanguage !== language || definition.unclearSource)) {
      const originalFields = { fr: 'definitionFr', en: 'definitionEn', es: 'definitionEs' };
      const originalValue = text(entry[originalFields[definition.originalLanguage]]);
      if (originalValue.trim()) {
        const originalDisclosure = element('details', 'original-definition');
        const originalText = element('p', 'full-definition', originalValue);
        originalText.lang = definition.originalLanguage;
        originalDisclosure.append(element('summary', '', `${copy(definition.unclearSource ? 'transcription' : 'originalToggle')} · ${LANGUAGE_NAMES[definition.originalLanguage]}`), originalText);
        detail.append(originalDisclosure);
      }
    }

    chipsSection(detail, copy('variants'), entry.variants);
    chipsSection(detail, copy('roots'), entry.roots);

    const provenance = element('section', 'detail-section');
    const metadata = element('dl', 'detail-metadata');
    metadataRow(metadata, copy('headword'), entry.headword);
    metadataRow(metadata, copy('source'), sourceLabel(entry));
    metadataRow(metadata, copy('variety'), entry.variety);
    metadataRow(metadata, copy('pos'), entry.pos);
    metadataRow(metadata, copy('citation'), entry.citation);
    metadataRow(metadata, copy('reference'), entry.sourceReference);
    metadataRow(metadata, copy('status'), entry.status);
    metadataRow(metadata, copy('id'), entry.id);
    const sourceUrl = safeSourceUrl(entry.sourceUrl);
    if (sourceUrl) {
      const value = element('dd');
      const link = element('a', '', copy('openSource'));
      link.href = sourceUrl;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      value.append(link);
      metadata.append(element('dt', '', copy('sourceLink')), value);
    }
    provenance.append(element('h3', '', copy('provenance')), metadata);
    detail.append(provenance);

    if (entry.msn && [entry.msn.headword, entry.msn.poeticForm, entry.msn.spokenForm].some(value => text(value).trim())) {
      const modern = element('details', 'msn-details');
      const modernMetadata = element('dl', 'detail-metadata');
      metadataRow(modernMetadata, copy('msn'), entry.msn.headword);
      metadataRow(modernMetadata, copy('poetic'), entry.msn.poeticForm);
      metadataRow(modernMetadata, copy('spoken'), entry.msn.spokenForm);
      modern.append(element('summary', '', copy('modern')), element('p', '', copy('modernNote')), modernMetadata);
      detail.append(modern);
    }
    detail.lang = language;
  }

  function openEntry(entry) {
    currentEntry = entry;
    renderEntry(entry);
    dialog.showModal();
    dialog.scrollTop = 0;
  }

  function renderEntries(entries) {
    const fragment = document.createDocumentFragment();
    entries.forEach(entry => {
      const row = element('button', 'entry-row');
      row.type = 'button';
      row.dataset.entryId = text(entry.id);
      const word = text(entry.headword) || copy('untitled');
      row.setAttribute('aria-label', `${copy('read')} ${word}, ${sourceLabel(entry)}`);
      const wordColumn = element('span');
      const headword = element('span', 'entry-word', word);
      headword.lang = 'nah';
      wordColumn.append(headword);
      if (entry.pos) wordColumn.append(element('span', 'entry-pos', entry.pos));
      const definitionColumn = element('span', 'entry-definition');
      const definition = definitionIn(entry, language);
      const preview = element('span', `definition-preview${definition.available ? '' : ' definition-unavailable'}`, definition.value);
      preview.lang = definition.language;
      definitionColumn.append(preview);
      const languageLabel = element('span', 'definition-language');
      languageLabel.append(element('span', '', LANGUAGE_NAMES[language]), element('span', 'definition-origin', definition.label));
      definitionColumn.append(languageLabel);
      const sourceColumn = element('span', 'entry-source');
      sourceColumn.append(element('span', 'source-label', sourceLabel(entry)), element('span', 'entry-open', copy('readEntry')));
      row.append(wordColumn, definitionColumn, sourceColumn);
      row.addEventListener('click', () => openEntry(entry));
      fragment.append(row);
    });
    list.replaceChildren(fragment);
  }

  function showMessage(heading, body, retry) {
    message.replaceChildren(element('h4', '', heading), element('p', '', body));
    if (retry) {
      const retryButton = element('button', 'retry-button', copy('retry'));
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
    url.searchParams.set('lang', language);
    window.history.replaceState(null, '', url);
  }

  function arrowButton(button, label, arrow, before) {
    const symbol = element('span', '', arrow);
    symbol.setAttribute('aria-hidden', 'true');
    button.replaceChildren(...(before ? [symbol, document.createTextNode(` ${label}`)] : [document.createTextNode(`${label} `), symbol]));
  }

  function refreshLanguageControls() {
    form.querySelectorAll('input[name="language"]').forEach(radio => { radio.checked = radio.value === language; });
    document.querySelector('#language-filter legend').textContent = copy('language');
    document.getElementById('search-help').textContent = copy('searchHelp');
    document.getElementById('language-help').textContent = copy('languageHelp');
    document.getElementById('search-help').lang = language;
    document.getElementById('language-help').lang = language;
    arrowButton(previous, copy('previous'), '←', true);
    arrowButton(next, copy('next'), '→', false);
    const closeSymbol = element('span', '', '×');
    closeSymbol.setAttribute('aria-hidden', 'true');
    const close = document.getElementById('close-entry');
    close.replaceChildren(document.createTextNode(copy('close') + ' '), closeSymbol);
    close.setAttribute('aria-label', copy('close'));
    title.textContent = query ? `${copy('results')} “${query}”` : copy('browse');
    title.lang = language;
    summary.lang = language;
    list.lang = language;
    pageSummary.lang = language;
    if (resultState === 'loading') summary.textContent = copy('loading');
    else if (resultState === 'error') {
      summary.textContent = copy('error');
      showMessage(copy('errorTitle'), copy('errorHelp'), true);
    } else {
      const first = total ? offset + 1 : 0;
      const last = Math.min(offset + currentEntries.length, total);
      summary.textContent = total ? `${first.toLocaleString(language)}–${last.toLocaleString(language)} ${copy('of')} ${total.toLocaleString(language)} ${copy(total === 1 ? 'entry' : 'entries')}` : copy('foundNone');
      if (!currentEntries.length) showMessage(copy('empty'), copy('emptyHelp'));
      pageSummary.textContent = `${copy('page')} ${Math.floor(offset / PAGE_SIZE) + 1} ${copy('of')} ${Math.max(1, Math.ceil(total / PAGE_SIZE)).toLocaleString(language)}`;
    }
  }

  function changeLanguage(code, fromEntry = false) {
    if (!LANGUAGES.includes(code)) return;
    language = code;
    try { window.localStorage.setItem('amoxcalli.definitionLanguage', language); } catch { /* The URL still preserves the choice. */ }
    updateAddress();
    refreshLanguageControls();
    renderEntries(currentEntries);
    if (dialog.open && currentEntry) {
      const scrollPosition = dialog.scrollTop;
      renderEntry(currentEntry);
      dialog.scrollTop = scrollPosition;
      if (fromEntry) detail.querySelector(`input[name="entry-language"][value="${language}"]`).focus({ preventScroll: true });
    }
  }

  async function loadEntries(scrollToResults = false) {
    controller?.abort();
    controller = new AbortController();
    const request = ++requestNumber;
    region.setAttribute('aria-busy', 'true');
    resultState = 'loading';
    refreshLanguageControls();
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
      currentEntries = entries;
      resultState = 'ready';
      renderEntries(currentEntries);
      const last = Math.min(offset + entries.length, total);
      refreshLanguageControls();
      pagination.hidden = total <= PAGE_SIZE;
      previous.disabled = offset === 0;
      next.disabled = last >= total;
      if (scrollToResults) {
        title.tabIndex = -1;
        title.focus({ preventScroll: true });
        title.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      }
    } catch (error) {
      if (error.name === 'AbortError' || request !== requestNumber) return;
      currentEntries = [];
      resultState = 'error';
      list.replaceChildren();
      refreshLanguageControls();
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
  form.querySelectorAll('input[name="language"]').forEach(radio => radio.addEventListener('change', () => changeLanguage(radio.value)));
  previous.addEventListener('click', () => { offset = Math.max(0, offset - PAGE_SIZE); loadEntries(true); });
  next.addEventListener('click', () => { if (offset + PAGE_SIZE < total) { offset += PAGE_SIZE; loadEntries(true); } });
  document.getElementById('close-entry').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    if (currentEntry) {
      const returnTarget = Array.from(list.querySelectorAll('.entry-row')).find(row => row.dataset.entryId === text(currentEntry.id));
      returnTarget?.focus({ preventScroll: true });
    }
    currentEntry = null;
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  input.value = query;
  form.querySelector(`input[name="source"][value="${source}"]`).checked = true;
  try { window.localStorage.setItem('amoxcalli.definitionLanguage', language); } catch { /* URL language works without storage. */ }
  loadEntries();
})();
