from pathlib import Path
import re

p = Path('index.html')
html = p.read_text(encoding='utf-8')

html = re.sub(
    r'<nav class="filters"[^>]*>.*?</nav>',
    '<nav class="filters" id="filters" aria-label="Filtra per tipologia"></nav>',
    html,
    count=1,
    flags=re.S,
)

html = re.sub(
    r'<label for="category">Tipologia</label><select id="category" required>.*?</select>',
    '<label>Tipologia</label><div class="category-picker" id="categoryPicker"><button type="button" class="category-toggle" id="categoryToggle" aria-expanded="false">Seleziona una o più tipologie <span>▾</span></button><div class="category-menu" id="categoryMenu"><div class="category-options" id="categoryOptions"></div><div class="new-category-row"><input id="newCategory" type="text" maxlength="32" placeholder="Nuova tipologia…"><button type="button" id="addCategory">＋ Aggiungi</button></div></div></div><div class="category-hint">Puoi associare più tipologie alla stessa ricetta.</div>',
    html,
    count=1,
    flags=re.S,
)

extra_css = '''
.category-picker{position:relative}.category-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;border:1px solid var(--line);border-radius:9px;padding:10px 12px;background:#fff;color:var(--ink);font:15px Georgia,serif;cursor:pointer;text-align:left}.category-toggle.open{border-color:#cba9a1;box-shadow:0 0 0 2px rgba(201,143,145,.10)}.category-menu{display:none;position:absolute;z-index:30;left:0;right:0;top:calc(100% + 6px);background:#fffdfb;border:1px solid var(--line);border-radius:12px;padding:10px;box-shadow:0 12px 32px rgba(70,50,45,.16)}.category-menu.open{display:block}.category-options{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;max-height:210px;overflow:auto;padding:2px}.category-option{display:flex;align-items:center;gap:8px;padding:8px 9px;border-radius:8px;background:#faf3f1;cursor:pointer;font-size:14px}.category-option:hover{background:var(--tag)}.category-option input{width:auto;margin:0;accent-color:var(--accent)}.new-category-row{display:flex;gap:7px;margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}.new-category-row input{min-width:0;flex:1}.new-category-row button{border:0;border-radius:8px;background:var(--accent-dark);color:#fff;padding:8px 11px;cursor:pointer;font:600 13px Georgia,serif;white-space:nowrap}.category-hint{font-size:12px;color:var(--muted);margin-top:6px}.card .category{margin:0}.filters .filter{white-space:nowrap}
'''
if '.category-picker{position:relative}' not in html:
    html = html.replace('</style>', extra_css + '</style>', 1)

script = r'''<script>
const KEY="ricettine-v1",CAT_KEY="ricettine-categories-v1";
const DEFAULT_CATEGORIES=["Riso","Verdurine","Asia","Salsine","Carne"];
const uid=()=>window.crypto&&crypto.randomUUID?crypto.randomUUID():Date.now()+"-"+Math.random().toString(16).slice(2);
const initial=[{id:uid(),title:"Riso alla cantonese",categories:["Riso"],ingredients:"Riso\nPiselli\nUova\nProsciutto cotto",steps:"Cuoci il riso e prepara gli ingredienti. Salta tutto in padella.",image:"",status:"published"},{id:uid(),title:"Salsina allo yogurt",categories:["Salsine"],ingredients:"Yogurt bianco\nLimone\nSale\nErbe aromatiche",steps:"Mescola tutti gli ingredienti e lascia riposare in frigorifero.",image:"",status:"published"}];
let recipes;try{recipes=JSON.parse(localStorage.getItem(KEY)||"null")||initial}catch(e){recipes=initial}
recipes=recipes.map(r=>({...r,categories:Array.isArray(r.categories)&&r.categories.length?r.categories:(r.category?[r.category]:["Riso"]),image:r.image||"",status:r.status||"published"}));
let categories;try{categories=JSON.parse(localStorage.getItem(CAT_KEY)||"null")||DEFAULT_CATEGORIES.slice()}catch(e){categories=DEFAULT_CATEGORIES.slice()}
for(const r of recipes)for(const c of r.categories||[])if(c&&!categories.some(x=>x.toLowerCase()===String(c).toLowerCase()))categories.push(c);
categories=[...new Map(categories.filter(Boolean).map(c=>[String(c).trim().toLowerCase(),String(c).trim()])).values()];
let currentFilter="Tutte",pendingImage="";
const grid=document.getElementById("grid"),count=document.getElementById("count"),search=document.getElementById("search"),modal=document.getElementById("modal"),form=document.getElementById("recipeForm"),filters=document.getElementById("filters"),imageInput=document.getElementById("imageInput"),imageUpload=document.getElementById("imageUpload"),imagePreview=document.getElementById("imagePreview"),imageTools=document.getElementById("imageTools"),categoryPicker=document.getElementById("categoryPicker"),categoryToggle=document.getElementById("categoryToggle"),categoryMenu=document.getElementById("categoryMenu"),categoryOptions=document.getElementById("categoryOptions"),newCategory=document.getElementById("newCategory");
function save(){localStorage.setItem(KEY,JSON.stringify(recipes))}function saveCategories(){localStorage.setItem(CAT_KEY,JSON.stringify(categories))}
function esc(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function setPreview(src){pendingImage=src||"";imagePreview.src=pendingImage;imageUpload.classList.toggle("has-image",!!pendingImage);imageTools.classList.toggle("has-image",!!pendingImage)}
function selectedTypes(){return [...categoryOptions.querySelectorAll('input[type="checkbox"]:checked')].map(x=>x.value)}
function updateCategoryToggle(){const s=selectedTypes();categoryToggle.firstChild.textContent=s.length?s.join(", ")+" ":"Seleziona una o più tipologie ";categoryToggle.setAttribute("title",s.join(", "))}
function renderCategoryOptions(selected=[]){const sel=new Set(selected);categoryOptions.innerHTML=categories.map(c=>`<label class="category-option"><input type="checkbox" value="${esc(c)}" ${sel.has(c)?"checked":""}><span>${esc(c)}</span></label>`).join("");updateCategoryToggle()}
function renderFilters(){if(currentFilter!=="Tutte"&&!categories.includes(currentFilter))currentFilter="Tutte";filters.innerHTML=`<button class="filter ${currentFilter==="Tutte"?"active":""}" data-filter="Tutte">Tutte</button>`+categories.map(c=>`<button class="filter ${currentFilter===c?"active":""}" data-filter="${esc(c)}">${esc(c)}</button>`).join("")}
function addNewCategory(){const raw=newCategory.value.trim().replace(/\s+/g," ");if(!raw)return;const existing=categories.find(c=>c.toLowerCase()===raw.toLowerCase());const name=existing||raw;if(!existing){categories.push(name);saveCategories();renderFilters()}const selected=selectedTypes();if(!selected.includes(name))selected.push(name);renderCategoryOptions(selected);newCategory.value="";newCategory.focus()}
function render(){const q=search.value.trim().toLowerCase();const visible=recipes.filter(r=>(currentFilter==="Tutte"||(r.categories||[]).includes(currentFilter))&&(!q||(String(r.title||"")+" "+(r.categories||[]).join(" ")+" "+String(r.ingredients||"")+" "+String(r.steps||"")).toLowerCase().includes(q)));count.textContent=visible.length+" "+(visible.length===1?"ricetta":"ricette");grid.innerHTML=visible.length?visible.map(r=>`<article class="card">${r.image?`<img class="card-image" src="${r.image}" alt="${esc(r.title||"Immagine del piatto")}">`:""}<div class="badges">${(r.categories||[]).map(c=>`<span class="category">${esc(c)}</span>`).join("")}${r.status==="draft"?'<span class="draft-badge">Bozza</span>':""}</div><h3>${esc(r.title||"Bozza senza titolo")}</h3><p><strong>Ingredienti</strong><br>${esc(r.ingredients||"—")}</p>${r.steps?`<p style="margin-top:12px"><strong>Procedimento</strong><br>${esc(r.steps)}</p>`:""}<div class="card-actions"><button class="small-btn" data-edit="${r.id}">Modifica</button>${r.status==="draft"?`<button class="small-btn publish" data-post="${r.id}">Pubblica</button>`:""}<button class="small-btn delete" data-delete="${r.id}">Elimina</button></div></article>`).join(""):`<div class="empty">Non ci sono ancora ricette in questa categoria.<br><br>Il cincillà chef aspetta nuove idee! 🥣</div>`}
function openNew(){form.reset();document.getElementById("recipeId").value="";document.getElementById("modalTitle").textContent="Nuova ricetta";setPreview("");renderCategoryOptions(categories.length?[categories[0]]:[]);categoryMenu.classList.remove("open");categoryToggle.classList.remove("open");modal.classList.add("open");document.getElementById("title").focus()}
function editRecipe(id){const r=recipes.find(x=>x.id===id);if(!r)return;document.getElementById("recipeId").value=r.id;document.getElementById("title").value=r.title||"";document.getElementById("ingredients").value=r.ingredients||"";document.getElementById("steps").value=r.steps||"";document.getElementById("modalTitle").textContent=r.status==="draft"?"Modifica bozza":"Modifica ricetta";setPreview(r.image||"");renderCategoryOptions(r.categories||[]);categoryMenu.classList.remove("open");categoryToggle.classList.remove("open");modal.classList.add("open")}
function deleteRecipe(id){const r=recipes.find(x=>x.id===id);if(r&&confirm(`Eliminare "${r.title||"questa bozza"}"?`)){recipes=recipes.filter(x=>x.id!==id);save();render()}}
function formData(status){const id=document.getElementById("recipeId").value;return{id:id||uid(),title:document.getElementById("title").value.trim(),categories:selectedTypes(),ingredients:document.getElementById("ingredients").value.trim(),steps:document.getElementById("steps").value.trim(),image:pendingImage,status}}
function storeRecipe(data){const exists=recipes.some(r=>r.id===data.id);recipes=exists?recipes.map(r=>r.id===data.id?data:r):[data,...recipes];save();modal.classList.remove("open");render()}
function postRecipe(id){const r=recipes.find(x=>x.id===id);if(!r)return;if(!String(r.title||"").trim()||!String(r.ingredients||"").trim()||!(r.categories||[]).length){editRecipe(id);alert("Per pubblicare la ricetta completa nome, almeno una tipologia e ingredienti.");return}r.status="published";save();render()}
document.getElementById("openAdd").onclick=openNew;document.getElementById("closeModal").onclick=()=>modal.classList.remove("open");modal.addEventListener("click",e=>{if(e.target===modal)modal.classList.remove("open")});search.addEventListener("input",render);
filters.addEventListener("click",e=>{const b=e.target.closest("button[data-filter]");if(!b)return;currentFilter=b.dataset.filter;renderFilters();render()});
categoryToggle.addEventListener("click",()=>{const open=!categoryMenu.classList.contains("open");categoryMenu.classList.toggle("open",open);categoryToggle.classList.toggle("open",open);categoryToggle.setAttribute("aria-expanded",String(open))});
categoryOptions.addEventListener("change",updateCategoryToggle);document.getElementById("addCategory").onclick=addNewCategory;newCategory.addEventListener("keydown",e=>{if(e.key==="Enter"){e.preventDefault();addNewCategory()}});document.addEventListener("click",e=>{if(!categoryPicker.contains(e.target)){categoryMenu.classList.remove("open");categoryToggle.classList.remove("open");categoryToggle.setAttribute("aria-expanded","false")}});
grid.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;if(b.dataset.edit)editRecipe(b.dataset.edit);if(b.dataset.post)postRecipe(b.dataset.post);if(b.dataset.delete)deleteRecipe(b.dataset.delete)});
imageUpload.addEventListener("click",()=>imageInput.click());imageUpload.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();imageInput.click()}});imageInput.addEventListener("change",()=>{const f=imageInput.files&&imageInput.files[0];if(f)readImage(f)});function readImage(file){if(!file.type.startsWith("image/")){alert("Seleziona un file immagine.");return}const reader=new FileReader();reader.onload=()=>setPreview(reader.result);reader.readAsDataURL(file)}imageUpload.addEventListener("dragover",e=>{e.preventDefault();imageUpload.classList.add("drag")});imageUpload.addEventListener("dragleave",()=>imageUpload.classList.remove("drag"));imageUpload.addEventListener("drop",e=>{e.preventDefault();imageUpload.classList.remove("drag");const f=e.dataTransfer.files&&e.dataTransfer.files[0];if(f)readImage(f)});document.getElementById("removeImage").onclick=()=>{imageInput.value="";setPreview("")};
form.addEventListener("submit",e=>{e.preventDefault();const data=formData("published");if(!data.categories.length){alert("Seleziona almeno una tipologia.");categoryMenu.classList.add("open");return}storeRecipe(data)});document.getElementById("saveDraft").onclick=()=>storeRecipe(formData("draft"));
renderFilters();renderCategoryOptions([]);render();
</script>'''

html = re.sub(r'<script>.*?</script>', script, html, count=1, flags=re.S)
p.write_text(html, encoding='utf-8')
print('index.html updated')
