(function(){
  const entriesEl = document.getElementById('entries');
  const detailTitle = document.getElementById('detailTitle');
  const origText = document.getElementById('origText');
  const editor = document.getElementById('extractionEditor');
  const applyBtn = document.getElementById('applyBtn');
  const revertBtn = document.getElementById('revertBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  const loadBuiltin = document.getElementById('loadBuiltin');
  const fileInput = document.getElementById('fileInput');
  const saveServerBtn = document.getElementById('saveServerBtn');

  let rows = [];
  let currentIndex = -1;
  const bulkFieldSelect = document.getElementById('bulkFieldSelect');
  const bulkCopyBtn = document.getElementById('bulkCopyBtn');
  const exportNeedsFix = document.getElementById('exportNeedsFix');
  const sortByConfidence = document.getElementById('sortByConfidence');
  const previewTopN = document.getElementById('previewTopN');
  const previewBtn = document.getElementById('previewBtn');
  const previewPanel = document.getElementById('previewPanel');
  const previewList = document.getElementById('previewList');
  const downloadPreview = document.getElementById('downloadPreview');
  const closePreview = document.getElementById('closePreview');
  const confidenceInput = document.getElementById('confidenceInput');

  function renderList(){
    entriesEl.innerHTML = '';
    rows.forEach((r,i)=>{
      const li = document.createElement('li');
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.dataset.index = i;
      cb.addEventListener('click', (e)=>{ e.stopPropagation(); });
      const span = document.createElement('span');
      span.textContent = r.text.length>80? r.text.slice(0,80)+'...': r.text;
      li.appendChild(cb);
      li.appendChild(span);
      li.addEventListener('click', ()=>{ selectIndex(i); });
      if(i===currentIndex) li.classList.add('active');
      entriesEl.appendChild(li);
    });
  }

  function selectIndex(i){
    currentIndex = i;
    renderList();
    const r = rows[i];
    detailTitle.textContent = 'Entry ' + i;
    origText.textContent = r.text;
    editor.value = JSON.stringify(r.extraction||{}, null, 2);
    // populate confidence input if present
    confidenceInput.value = (r.extraction && typeof r.extraction.confidence !== 'undefined') ? r.extraction.confidence : '';
  }

  applyBtn.addEventListener('click', ()=>{
    if(currentIndex<0) return alert('Select an entry first');
    try{
      const v = JSON.parse(editor.value);
      // attach confidence if provided
      const confRaw = confidenceInput.value;
      if(confRaw !== ''){
        const conf = parseFloat(confRaw);
        if(!Number.isFinite(conf) || conf<0 || conf>1) return alert('Confidence must be number between 0 and 1');
        v.confidence = conf;
      } else {
        if(v.hasOwnProperty('confidence')) delete v.confidence;
      }
      rows[currentIndex].extraction = v;
      alert('Applied to in-memory row.');
    }catch(e){
      alert('Invalid JSON: '+e.message);
    }
  });

  bulkCopyBtn.addEventListener('click', ()=>{
    const field = bulkFieldSelect.value;
    if(!field) return alert('Choose a field to copy');
    // take value from current editor if JSON contains that field or prompt for value
    let value = null;
    try{
      const obj = JSON.parse(editor.value);
      if(obj && obj[field]!==undefined){ value = obj[field]; }
    }catch(e){ /* ignore */ }
    if(value===null){ value = prompt('Value to set for field '+field);
      if(value===null) return; // cancelled
    }
    // apply to all checked items
    const checks = entriesEl.querySelectorAll('input[type=checkbox]:checked');
    if(!checks.length) return alert('No entries selected');
    checks.forEach(ch=>{
      const i = parseInt(ch.dataset.index,10);
      rows[i].extraction = rows[i].extraction || {};
      rows[i].extraction[field] = value;
    });
    alert(`Applied ${field} to ${checks.length} entries`);
    renderList();
  });

  exportNeedsFix.addEventListener('click', ()=>{
    const sel = Array.from(document.getElementById('needsFieldsSelect').selectedOptions).map(o=>o.value);
    if(!sel.length) return alert('Select at least one field to consider as missing');
    const sortBy = document.getElementById('sortByMissing').checked;
    const items = rows.map((r,i)=>({i, text:r.text, extraction:r.extraction||{}}))
      .map(n=>{
        const missing = [];
        sel.forEach(f=>{ if(!n.extraction || n.extraction[f]===undefined || n.extraction[f]===null || (Array.isArray(n.extraction[f]) && n.extraction[f].length===0)) missing.push(f); });
        return {...n, missing};
      })
      .filter(n=>n.missing.length>0);
    if(!items.length) return alert('No entries missing selected fields');
    if(sortBy) items.sort((a,b)=>b.missing.length - a.missing.length);
    // optionally sort by confidence (desc) if requested
    if(sortByConfidence && sortByConfidence.checked){
      items.sort((a,b)=>{
        const ac = (a.extraction && typeof a.extraction.confidence === 'number') ? a.extraction.confidence : -Infinity;
        const bc = (b.extraction && typeof b.extraction.confidence === 'number') ? b.extraction.confidence : -Infinity;
        return bc - ac;
      });
    }
    const lines = ['index,text,missing_fields'];
    items.forEach(n=>{
      const safeText = '"'+(n.text.replace(/"/g,'""'))+'"';
      lines.push(`${n.i},${safeText},"${n.missing.join(';')}"`);
    });
    const blob = new Blob([lines.join('\n')], {type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download='needs_fix.csv'; a.click(); URL.revokeObjectURL(url);
  });

  // preview generation
  function buildPreviewItems(){
    const sel = Array.from(document.getElementById('needsFieldsSelect').selectedOptions).map(o=>o.value);
    const items = rows.map((r,i)=>({i, text:r.text, extraction:r.extraction||{}}))
      .map(n=>{
        const missing = [];
        sel.forEach(f=>{ if(!n.extraction || n.extraction[f]===undefined || n.extraction[f]===null || (Array.isArray(n.extraction[f]) && n.extraction[f].length===0)) missing.push(f); });
        return {...n, missing};
      })
      .filter(n=>n.missing.length>0);
    // optional sorts
    const sortBy = document.getElementById('sortByMissing').checked;
    if(sortBy) items.sort((a,b)=>b.missing.length - a.missing.length);
    if(sortByConfidence && sortByConfidence.checked){
      items.sort((a,b)=>{
        const ac = (a.extraction && typeof a.extraction.confidence === 'number') ? a.extraction.confidence : -Infinity;
        const bc = (b.extraction && typeof b.extraction.confidence === 'number') ? b.extraction.confidence : -Infinity;
        return bc - ac;
      });
    }
    return items;
  }

  previewBtn.addEventListener('click', ()=>{
    const topN = parseInt(previewTopN.value,10) || 10;
    const items = buildPreviewItems().slice(0, topN);
    previewList.innerHTML = '';
    items.forEach(it=>{
      const li = document.createElement('li');
      li.textContent = `#${it.i} (${it.missing.join(',')}) ` + (it.extraction && it.extraction.confidence!==undefined ? `[conf=${it.extraction.confidence}] ` : '') + (it.text.length>80? it.text.slice(0,80)+'...': it.text);
      previewList.appendChild(li);
    });
    previewPanel.style.display = 'block';
  });

  closePreview.addEventListener('click', ()=>{ previewPanel.style.display='none'; });

  downloadPreview.addEventListener('click', ()=>{
    const items = buildPreviewItems();
    const topN = parseInt(previewTopN.value,10) || 10;
    const sel = items.slice(0, topN);
    if(!sel.length) return alert('No items to download');
    const lines = ['index,text,missing_fields,confidence'];
    sel.forEach(n=>{
      const safeText = '"'+(n.text.replace(/"/g,'""'))+'"';
      const conf = (n.extraction && typeof n.extraction.confidence === 'number') ? n.extraction.confidence : '';
      lines.push(`${n.i},${safeText},"${n.missing.join(';')}",${conf}`);
    });
    const blob = new Blob([lines.join('\n')], {type:'text/csv'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download='needs_fix_preview.csv'; a.click(); URL.revokeObjectURL(url);
  });

  revertBtn.addEventListener('click', ()=>{
    if(currentIndex<0) return;
    editor.value = JSON.stringify(rows[currentIndex].extraction||{}, null, 2);
  });

  downloadBtn.addEventListener('click', ()=>{
    const blob = new Blob([JSON.stringify(rows, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'diagnose_report_edited.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  loadBuiltin.addEventListener('click', ()=>{
    fetch('diagnose_report.json').then(r=>r.json()).then(j=>{ rows = j; fillMissingConfidences(rows); currentIndex=0; renderList(); selectIndex(0); }).catch(e=>alert('Failed to load builtin diagnose_report.json: '+e.message));
  });

  fileInput.addEventListener('change', (ev)=>{
    const f = ev.target.files[0];
    if(!f) return;
    const reader = new FileReader();
    reader.onload = ()=>{
      try{
        rows = JSON.parse(reader.result);
        fillMissingConfidences(rows);
        currentIndex=0; renderList(); selectIndex(0);
      }catch(e){ alert('Invalid JSON file: '+e.message); }
    };
    reader.readAsText(f);
  });

  function estimateConfidenceFromExtraction(out){
    let score = 0.0;
    if(out && out.fs) score += 0.3;
    if(out && out.data_path) score += 0.25;
    if(out && out.methods && out.methods.length>0) score += 0.2;
    if(out && out.bandpass) score += 0.15;
    if(out && out.filters && out.filters.length>0) score += 0.1;
    if(score > 1.0) score = 1.0;
    return Math.round(score * 1000)/1000;
  }

  function fillMissingConfidences(rows){
    rows.forEach(r=>{
      if(!r.extraction) r.extraction = {};
      if(typeof r.extraction.confidence === 'undefined' || r.extraction.confidence === null){
        r.extraction.confidence = estimateConfidenceFromExtraction(r.extraction);
      }
    });
  }

  saveServerBtn.addEventListener('click', ()=>{
    if(!confirm('Send edited report to local server at /save? Make sure you run scripts/serve_annotator.py')) return;
    fetch('/save', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(rows)})
      .then(r=>{ if(r.ok) alert('Saved on server'); else r.text().then(t=>alert('Server error: '+t)); })
      .catch(e=>alert('Failed to save to server: '+e.message));
  });

  listBackupsBtn.addEventListener('click', ()=>{
    fetch('/backups').then(r=>r.json()).then(j=>{
      backupsListContainer.innerHTML = '';
      if(!j.backups || !j.backups.length) { backupsListContainer.textContent = 'No backups'; return; }
      j.backups.forEach(name=>{
        const span = document.createElement('span');
        span.style.marginRight = '8px';
        const a = document.createElement('a'); a.href = `/download?name=${encodeURIComponent(name)}`; a.textContent = name; a.target='_blank';
        span.appendChild(a);
        backupsListContainer.appendChild(span);
      });
    }).catch(e=>{ backupsListContainer.textContent = 'Failed to list backups: '+e.message });
  });

  // init empty
  renderList();
})();
