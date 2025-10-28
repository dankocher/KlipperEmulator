const $files = document.getElementById("files");
const $uploadForm = document.getElementById("uploadForm");
const $estimateForm = document.getElementById("estimateForm");
const $fileId = document.getElementById("file_id");
const tpl = document.getElementById("fileRow");

async function loadFiles(){
  const r = await fetch("/api/files");
  const j = await r.json();
  $files.innerHTML = "";
  j.files.forEach(f=>{
    const el = tpl.content.cloneNode(true);
    const img = el.querySelector(".thumb");
    const name = el.querySelector(".name");
    const btnUse = el.querySelector(".use");
    const btnDel = el.querySelector(".del");

    name.textContent = `${f.name} — ${(f.meta?.size||0/1024).toFixed(0)} bytes`;
    if (f.thumb) img.src = `/thumb/${f.id}`; else img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAA..."; // placeholder opcional

    btnUse.onclick = ()=>{ $fileId.value = f.id; scrollToForm(); };
    btnDel.onclick = async ()=>{
      if(!confirm("Eliminar archivo?")) return;
      await fetch(`/api/files/${f.id}`, {method:"DELETE"});
      loadFiles();
    };
    $files.appendChild(el);
  });
}

function scrollToForm(){
  $estimateForm.scrollIntoView({behavior:"smooth", block:"center"});
}

$uploadForm.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const fd = new FormData($uploadForm);
  const r = await fetch("/api/upload", {method:"POST", body: fd});
  if(r.ok){ await loadFiles(); alert("Subido."); } else { alert("Error al subir."); }
});

$estimateForm.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const fd = new FormData($estimateForm);
  const r = await fetch("/api/estimate", {method:"POST", body: fd});
  const j = await r.json();
  const out = document.getElementById("result");
  if(!j.ok){ out.textContent = "Error: " + (j.error || "simulación"); return; }
  out.textContent = `Tiempo estimado: ${j.pretty}\n\nSalida del simulador:\n${j.raw}`;
});

// ==== Sliders sincronizados con inputs numéricos ====
document.querySelectorAll('.slider-wrap').forEach(wrap=>{
  const range = wrap.querySelector('input[type=range]');
  const num   = wrap.querySelector('input[type=number]');

  // sincr. en ambos sentidos
  range.addEventListener('input', ()=> num.value = range.value);
  num.addEventListener('input', ()=> range.value = num.value);
});


loadFiles();
