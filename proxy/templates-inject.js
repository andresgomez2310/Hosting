(function(){
  function findTemplateNameFromElement(el){
    // 1) buscar atributos data-template / data-folder / data-name en el elemento o en ancestros
    var node = el;
    while(node && node !== document.body){
      if(node.dataset){
        if(node.dataset.template) return node.dataset.template;
        if(node.dataset.folder) return node.dataset.folder;
        if(node.dataset.name) return node.dataset.name;
      }
      node = node.parentElement;
    }
    // 2) buscar en el card un elemento con clase común (ajustar si tu markup usa otra clase)
    node = el.closest('.card, .template-card, .item') || el.parentElement;
    if(node){
      var candidate = node.querySelector('[data-template],[data-folder],[data-name],.template-name,h3,h2');
      if(candidate){
        if(candidate.dataset){
          if(candidate.dataset.template) return candidate.dataset.template;
          if(candidate.dataset.folder) return candidate.dataset.folder;
          if(candidate.dataset.name) return candidate.dataset.name;
        }
        return candidate.textContent.trim().split(/\s+/)[0];
      }
    }
    // 3) fallback (ajusta al slug por defecto de tus templates)
    return 'react-template';
  }

  // crea botón clonando tipo y clases del botón de descarga (si existe)
  function createMountButton(dbtn, templateName){
    var isAnchor = (dbtn.tagName && dbtn.tagName.toLowerCase() === 'a');
    var btn;
    // apuntar al path que usa la SPA/modal: /templates/<folder>/
    var targetUrl = '/templates/' + encodeURIComponent(templateName) + '/';
    if(isAnchor) {
      btn = document.createElement('a');
      btn.href = targetUrl;
      btn.target = '_blank';
      btn.rel = 'noopener noreferrer';
    } else {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.onclick = function(){ window.open(targetUrl, '_blank'); };
    }

    // Copiar clases del botón de descarga para mantener estilo
    try {
      if(dbtn.classList && dbtn.classList.length){
        dbtn.classList.forEach(function(c){ btn.classList.add(c); });
      } else if(dbtn.getAttribute && dbtn.getAttribute('class')){
        btn.setAttribute('class', dbtn.getAttribute('class'));
      }
    } catch(e){ /* ignore */ }

    // Forzar display block so buttons stack
    btn.style.display = 'block';
    btn.style.marginTop = '8px';

    btn.classList.add('mount-btn');
    btn.innerHTML = 'Montar';
    return btn;
  }

  // helper para detectar botones existentes que ya hacen 'montar'
  function hasExistingMount(parent){
    if(!parent) return false;
    // ya existe elemento con class mount-btn
    if(parent.querySelector('.mount-btn')) return true;
    // buscar elementos con aria-label/title que contengan 'Montar' (case-insensitive)
    var candidates = parent.querySelectorAll('*');
    for(var i=0;i<candidates.length;i++){
      var el = candidates[i];
      var al = el.getAttribute && (el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent || '');
      if(al && /montar/i.test(al)) return true;
    }
    return false;
  }

  function enhance(){
    var downloadButtons = Array.from(document.querySelectorAll('button, a')).filter(function(el){
      return /descargar\s*zip/i.test(el.textContent || el.innerText || '');
    });

    downloadButtons.forEach(function(dbtn){
      // si en el contenedor ya hay un mount, saltar
      if(hasExistingMount(dbtn.parentElement)) return;

      var templateName = findTemplateNameFromElement(dbtn);
      var mountBtn = createMountButton(dbtn, templateName);
      dbtn.parentElement.insertBefore(mountBtn, dbtn.nextSibling);
    });
  }

  enhance();
  var observer = new MutationObserver(function(){ enhance(); });
  observer.observe(document.body, { childList: true, subtree: true });
})();
