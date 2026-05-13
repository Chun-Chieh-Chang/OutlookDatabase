/**
 * SkillsBuilder AI - Main Frontend Controller
 * v3.1: Visual Hardening & Live Pulse Monitoring
 */

const AppState = {
    keyword: '',
    page: 1,
    limit: 12,
    wikiData: [],
    currentView: 'dashboard',
    lastSyncNodeCount: 0,
    selectedEmails: new Set(),
    prunePage: 1,
    syncActive: true
};

const UI = {
    get: (id) => document.getElementById(id),
    text: (id, text) => { const el = document.getElementById(id); if(el) el.textContent = text; },
    show: (id) => { const el = document.getElementById(id); if(el) el.classList.remove('hidden'); },
    hide: (id) => { const el = document.getElementById(id); if(el) el.classList.add('hidden'); },
    // 強化版狀態看板
    log: (msg, type = 'info') => {
        console.log(`%c[SkillsBuilder] %c${msg}`, "color: #3b82f6; font-weight: bold", "color: inherit");
        const ticker = document.getElementById('ticker-content');
        if (ticker) {
            const entry = document.createElement('div');
            entry.className = `text-[10px] py-1 border-b border-white/5 last:border-0 ${type === 'error' ? 'text-rose-400' : 'text-emerald-400/90'} animate-fade-in`;
            entry.innerHTML = `<span class="opacity-30 mr-2 font-mono">${new Date().toLocaleTimeString([], {hour12:false})}</span> ${msg}`;
            ticker.prepend(entry);
            if (ticker.childNodes.length > 5) ticker.removeChild(ticker.lastChild);
        }
    },
    // KaTeX 渲染驅動
    renderMath: (id) => {
        const el = document.getElementById(id);
        if (el && window.renderMathInElement) {
            // 使用 requestAnimationFrame 確保 DOM 已渲染
            requestAnimationFrame(() => {
                window.renderMathInElement(el, {
                    delimiters: [
                        {left: "$$", right: "$$", display: true},
                        {left: "$", right: "$", display: false},
                        {left: "\\(", right: "\\)", display: false},
                        {left: "\\[", right: "\\]", display: true}
                    ],
                    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
                    throwOnError : false
                });
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    UI.log('SkillsBuilder Engine 核心初始化...');
    loadDashboardStats();
    loadRecentEmails();
    checkAIStatus();
    pollSystemLogs(); 
    
    setInterval(() => {
        if (AppState.currentView === '3d' && AppState.syncActive) sync3DGraph();
        loadDashboardStats();
        checkAIStatus();
        pollSystemLogs();
        updateSynthesisProgress();
    }, 4000); 

    startIncrementalSync();

    // Wiki 搜尋連動邏輯
    const searchInput = document.getElementById('wikiSearchInput') || document.querySelector('input[placeholder*="搜尋"]');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            if (AppState.currentView === 'wiki') {
                filterWikiList(val);
            }
        });

        // [New] Wiki 優先直達邏輯
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = searchInput.value.toLowerCase();
                // 優先在 Wiki 列表搜尋
                const matches = document.querySelectorAll('#wikiSidebar .wiki-item, #wikiGrid .glass-panel');
                let foundMatch = null;
                for (let item of matches) {
                    if (item.innerText.toLowerCase().includes(val)) {
                        foundMatch = item;
                        break;
                    }
                }

                if (foundMatch) {
                    UI.log(`⚡ 偵測到實體直接匹配：啟動 Wiki 直達程式...`);
                    showView('wiki');
                    const fileName = foundMatch.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
                    if (fileName) {
                        loadWikiPage(fileName);
                    } else {
                        foundMatch.click(); // 退而求其次，觸發點擊
                    }
                } else {
                    // 找不到才去詢問 AI
                    askWiki();
                }
            }
        });
    }

    // 全域導入按鈕監聽
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('#importBundleBtn');
        if (btn) {
            UI.log('📡 偵測到物理點擊：啟動導入程序');
            importBundle();
        }
    });
});

let lastLogLines = [];
async function pollSystemLogs() {
    try {
        const resp = await fetch('/api/system_logs?t=' + Date.now());
        const lines = await resp.json();
        
        // 更新標題呼吸燈
        const pulseDot = UI.get('pulse-dot');
        if (pulseDot) {
            pulseDot.classList.add('animate-pulse');
            pulseDot.style.color = lines.length > 0 ? '#10b981' : '#64748b';
        }

        // 更新進度條與計時器
        try {
            const progResp = await fetch('/api/system_progress?t=' + Date.now());
            const prog = await progResp.json();
            const bar = UI.get('system-progress-bar');
            const timer = UI.get('system-timer');
            
            if (bar) bar.style.width = (prog.percentage || 0) + '%';
            
            // [V3.1] 更新百分比與狀態文字
            const pText = UI.get('system-progress-text');
            const sText = UI.get('system-status-text');
            if (pText) pText.innerText = Math.round(prog.percentage || 0) + '%';
            if (sText && prog.status) sText.innerText = prog.status;

            if (timer && prog.elapsed_seconds !== undefined) {
                const mins = Math.floor(prog.elapsed_seconds / 60);
                const secs = prog.elapsed_seconds % 60;
                timer.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
        } catch (e) {}

        lines.forEach(line => {
            const cleanLine = line.trim();
            // 如果這行還沒出現在日誌視窗中
            if (cleanLine && !lastLogLines.includes(cleanLine)) {
                // 放寬過濾條件，包含所有進度訊號
                const isProgress = /正在分析|✅|🚀|\[Fallback\]|已加載|Starting|Analysis|Waiting|Processing|Gemini|PROGRESS/.test(cleanLine);
                if (isProgress) {
                    UI.log(cleanLine, cleanLine.includes('Fallback') ? 'error' : 'info');
                }
                lastLogLines.push(cleanLine);
                if (lastLogLines.length > 100) lastLogLines.shift();
            }
        });
    } catch (err) {}
}

async function checkAIStatus() {
    try {
        const resp = await fetch('/api/ai_status?t=' + Date.now());
        const data = await resp.json();
        const pill = UI.get('aiStatusPill');
        const dot = UI.get('aiStatusDot');
        const text = UI.get('aiStatusText');
        if(!pill) return;
        
        if (data.available) {
            pill.className = 'ai-status-pill px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-bold flex items-center gap-2 transition-colors';
            dot.className = 'w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse';
            text.textContent = 'OLLAMA ONLINE';
        } else {
            pill.className = 'ai-status-pill px-3 py-1 bg-slate-100 text-slate-500 rounded-full text-[10px] font-bold flex items-center gap-2 transition-colors';
            dot.className = 'w-1.5 h-1.5 bg-slate-400 rounded-full';
            text.textContent = 'OLLAMA OFFLINE';
        }
    } catch (err) {}
}

async function loadDashboardStats() {
    try {
        const resp = await fetch('/api/dashboard_stats?t=' + Date.now());
        const data = await resp.json();
        UI.text('dashTotalMails', data.total_emails || 0);
        UI.get('dashEntityCount').textContent = data.entity_count || 0;
        
        // Fetch Evolution Metrics
        try {
            const evo = await fetch('/api/evolution').then(r => r.json());
            UI.get('dashEvolutionScore').textContent = evo.score;
            UI.get('dashEvolutionStatus').textContent = evo.status.toUpperCase();
        } catch (e) { console.error('Evo metrics failed', e); }

        UI.text('dashConceptCount', data.concept_count || 0);
        UI.text('dashSenderCount', data.unique_senders || 0);
    } catch (err) { UI.log('看板數據抓取異常', 'error'); }
}

// --- 3D 圖譜視覺強化版 ---
let graphInstance = null;

async function init3DGraph() {
    if (graphInstance) return;
    UI.log('開啟 3D 空間，正在部署文字渲染陣列...');
    const elem = UI.get('3d-graph');
    if (!elem) return;

    try {
        const resp = await fetch('/api/graph_data?t=' + Date.now());
        const data = await resp.json();
        UI.log(`數據部署成功: ${data.nodes.length} 實體已就位`);
        AppState.lastSyncNodeCount = data.nodes.length;

        graphInstance = ForceGraph3D()(elem)
            .graphData(data)
            .nodeColor(node => node.color || '#3b82f6')
            .nodeRelSize(5)
            .nodeThreeObject(node => {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                const label = node.id;
                const fontSize = 48;
                context.font = `bold ${fontSize}px Inter, Arial`;
                const width = context.measureText(label).width;
                canvas.width = width + 40;
                canvas.height = fontSize + 40;
                
                // [視覺美化] 移除方塊背景，改用發光描邊文字
                context.shadowColor = 'rgba(0, 0, 0, 1)';
                context.shadowBlur = 10;
                context.lineWidth = 6;
                context.strokeStyle = 'rgba(0, 0, 0, 0.8)';
                context.strokeText(label, canvas.width / 2, canvas.height / 2);

                context.fillStyle = '#ffffff';
                context.textAlign = 'center';
                context.textBaseline = 'middle';
                context.fillText(label, canvas.width / 2, canvas.height / 2);

                const texture = new THREE.CanvasTexture(canvas);
                texture.needsUpdate = true;
                const material = new THREE.SpriteMaterial({ 
                    map: texture,
                    transparent: true,
                    depthTest: false
                });
                const sprite = new THREE.Sprite(material);
                sprite.scale.set(width / 10, (fontSize + 40) / 10, 1);
                return sprite;
            })
            .nodeThreeObjectExtend(true)
            .backgroundColor('#000000')
            .onNodeClick(node => {
                UI.log(`深度檢閱實體: ${node.id}`);
                closeView('3d'); showView('wiki'); loadWikiPage(node.id + '.md');
            });

        graphInstance.d3Force('link').distance(800).strength(0.005);
        graphInstance.d3Force('charge').strength(-10000);
        graphInstance.linkOpacity(0.1); // 大幅淡化連線，防止疊加發光
        graphInstance.controls().autoRotate = true;

        // [Premium UX] 實作游標基準縮放 (Zoom to Cursor)
        elem.addEventListener('wheel', (e) => {
            if (!graphInstance) return;
            
            // 1. 一旦開始縮放，停止自動旋轉，讓使用者接管視角
            const controls = graphInstance.controls();
            if (controls.autoRotate) {
                controls.autoRotate = false;
                UI.log('使用者接管：已終止自動旋轉');
            }
            
            const rect = elem.getBoundingClientRect();
            const mouse = new THREE.Vector2(
                ((e.clientX - rect.left) / rect.width) * 2 - 1,
                -((e.clientY - rect.top) / rect.height) * 2 + 1
            );

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, graphInstance.camera());
            
            // 優先尋找節點
            const intersects = raycaster.intersectObjects(graphInstance.scene().children, true);
            
            if (intersects.length > 0) {
                const targetPoint = intersects[0].point;
                // 提高權重，讓移動更有感
                controls.target.lerp(targetPoint, 0.2);
            } else {
                // 如果指在空白處，投影到通過原點且平行於相機平面的虛擬平面上
                const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
                const targetPoint = new THREE.Vector3();
                if (raycaster.ray.intersectPlane(plane, targetPoint)) {
                    controls.target.lerp(targetPoint, 0.1);
                }
            }
        }, { passive: true });

    } catch (err) { UI.log('3D 引擎崩潰: ' + err.message, 'error'); }
}

function filterWikiList(query) {
    const items = document.querySelectorAll('#wikiSidebar .wiki-item, #wikiGrid .glass-panel');
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        item.style.display = text.includes(query) ? '' : 'none';
    });
}

async function sync3DGraph() {
    if (!graphInstance || !AppState.syncActive) return;
    try {
        const resp = await fetch('/api/graph_data?t=' + Date.now());
        const data = await resp.json();
        if (data.nodes.length !== AppState.lastSyncNodeCount) {
            UI.log(`⚡ 偵測到知識爆炸！節點激增: ${data.nodes.length}`, 'info');
            graphInstance.graphData(data);
            AppState.lastSyncNodeCount = data.nodes.length;
        }
    } catch (err) { }
}

let syncFailCount = 0;
async function startIncrementalSync() {
    const interval = setInterval(async () => {
        if (!AppState.syncActive) {
            clearInterval(interval);
            return;
        }

        try {
            const resp = await fetch('/api/sync/incremental');
            const data = await resp.json();
            
            if (data.status === 'no_outlook') {
                syncFailCount++;
                if (syncFailCount >= 3) {
                    AppState.syncActive = false;
                    UI.log('[系統休眠] 未偵測到 Outlook 環境，已切換至離線模式。', 'warning');
                    clearInterval(interval);
                }
            } else {
                syncFailCount = 0;
                // 只有在特定視圖下才顯示心跳日誌，避免干擾
                if (AppState.currentView === 'sync') {
                    UI.log(data.message || '執行增量同步檢查...');
                }
            }
        } catch (e) {
            syncFailCount++;
        }
    }, 5000);
}

function showView(v) {
    AppState.currentView = v;
    UI.log(`切換導航: ${v.toUpperCase()}`);
    
    // Hide all views
    ['view-dashboard', 'view-wiki', 'view-3d', 'view-sync', 'view-manual', 'view-devlog', 'view-prune'].forEach(id => UI.hide(id));
    
    if (v === 'dashboard') { UI.show('view-dashboard'); }
    else if (v === 'wiki') { UI.show('view-wiki'); loadWikiIndex(); }
    else if (v === '3d') { UI.show('view-3d'); init3DGraph(); }
    else if (v === 'sync') { UI.show('view-sync'); }
    else if (v === 'prune') { UI.show('view-prune'); loadPruneList(); }
    else if (v === 'manual') { UI.show('view-manual'); loadManual(); }
    else if (v === 'devlog') { UI.show('view-devlog'); loadDevLog(); }
}

async function loadPruneList(page = 1) {
    AppState.prunePage = page;
    UI.log(`載入待清理數據 (第 ${page} 頁)...`);
    try {
        const resp = await fetch(`/api/emails/recent_list?page=${page}&limit=50`);
        const data = await resp.json();
        
        const tbody = document.getElementById('pruneListBody');
        const pagination = document.getElementById('prunePagination');
        
        if (!tbody) return;

        tbody.innerHTML = data.emails.map(e => `
            <tr class="hover:bg-slate-50/80 transition-colors group">
                <td class="p-4 text-center">
                    <input type="checkbox" data-id="${e.entry_id}" onchange="toggleEmailSelection(this)" ${AppState.selectedEmails.has(e.entry_id) ? 'checked' : ''} class="email-checkbox w-4 h-4 rounded border-slate-300">
                </td>
                <td class="p-4">
                    <div class="font-bold text-slate-700 text-xs">${e.sender_name}</div>
                    <div class="text-[10px] text-slate-400 mt-1">${e.received_time}</div>
                </td>
                <td class="p-4">
                    <div class="font-bold text-slate-800 text-sm mb-1">${e.subject}</div>
                    <div class="text-xs text-slate-500 line-clamp-1">${e.snippet}...</div>
                </td>
                <td class="p-4 text-center">
                    <button onclick="deleteSingleEmail('${e.entry_id}')" class="text-slate-300 hover:text-rose-500 transition-colors">
                        <i class="fas fa-trash-can"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Render Pagination
        pagination.innerHTML = `
            <div class="text-xs text-slate-400">顯示第 ${page} 頁，共 ${data.total} 封</div>
            <div class="flex gap-2">
                <button onclick="loadPruneList(${page - 1})" ${page === 1 ? 'disabled' : ''} class="px-3 py-1 bg-white border border-slate-200 rounded-lg text-xs disabled:opacity-30">上一頁</button>
                <button onclick="loadPruneList(${page + 1})" ${page === data.pages || data.pages === 0 ? 'disabled' : ''} class="px-3 py-1 bg-white border border-slate-200 rounded-lg text-xs disabled:opacity-30">下一頁</button>
            </div>
        `;
        
        updateSelectedUI();
    } catch (err) { UI.log('清理清單讀取失敗', 'error'); }
}

function toggleEmailSelection(el) {
    const id = el.dataset.id;
    if (AppState.selectedEmails.has(id)) AppState.selectedEmails.delete(id);
    else AppState.selectedEmails.add(id);
    updateSelectedUI();
}

function toggleSelectAll(cb) {
    const boxes = document.querySelectorAll('.email-checkbox');
    boxes.forEach(box => {
        const id = box.dataset.id;
        box.checked = cb.checked;
        if (cb.checked) AppState.selectedEmails.add(id);
        else AppState.selectedEmails.delete(id);
    });
    updateSelectedUI();
}

function updateSelectedUI() {
    const btn = document.getElementById('btnDeleteSelected');
    const count = document.getElementById('selectedCount');
    if (btn) btn.disabled = AppState.selectedEmails.size === 0;
    if (count) count.textContent = AppState.selectedEmails.size;
}

function openDeleteModal() {
    UI.show('deleteModal');
    const count = document.getElementById('modalDeleteCount');
    if (count) count.textContent = AppState.selectedEmails.size;
}

function closeDeleteModal() {
    UI.hide('deleteModal');
}

function deleteSelectedEmails() {
    if (AppState.selectedEmails.size === 0) return;
    openDeleteModal();
}

async function confirmDelete() {
    const ids = Array.from(AppState.selectedEmails);
    closeDeleteModal();
    
    UI.log(`正在刪除 ${ids.length} 封郵件...`, 'warning');
    try {
        const resp = await fetch('/api/emails/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids })
        });
        const data = await resp.json();
        UI.log(data.message, 'success');
        AppState.selectedEmails.clear();
        loadPruneList(AppState.prunePage);
        loadDashboardStats();
    } catch (err) { UI.log('刪除失敗', 'error'); }
}

async function deleteSingleEmail(id) {
    AppState.selectedEmails.clear();
    AppState.selectedEmails.add(id);
    openDeleteModal();
}

function reset3DView() {
    if (!graphInstance) return;
    UI.log('重置 3D 空間視野，正在還原全貌...');
    
    // 1. 還原相機焦點到原點
    const controls = graphInstance.controls();
    controls.target.set(0, 0, 0);
    
    // 2. 使用內建函數平滑地縮放到容納所有節點
    graphInstance.zoomToFit(1000, 50);
}

async function loadDevLog() {
    UI.log('正在讀取系統進化與故障確效紀錄...');
    try {
        const resp = await fetch('/api/dev_log?t=' + Date.now());
        const data = await resp.json();
        if (data.error) throw new Error(data.error);
        
        const container = UI.get('devLogContent');
        if (container) {
            // 1. Markdown 渲染
            container.innerHTML = marked.parse(data.content || '目前尚無日誌');
            
            // 2. 強化版數學公式渲染 (KaTeX)
            let html = container.innerHTML;
            html = html.replace(/\$\$(.*?)\$\$/gs, (m, p1) => {
                try { return `<div class="katex-display">${katex.renderToString(p1, { displayMode: true })}</div>`; } catch (e) { return m; }
            });
            html = html.replace(/\$(.*?)\$/g, (m, p1) => {
                try { return `<span class="katex-inline">${katex.renderToString(p1, { displayMode: false })}</span>`; } catch (e) { return m; }
            });
            container.innerHTML = html;
            
            UI.log('日誌渲染完成：已套用顆粒化排版', 'info');
        }
    } catch (err) {
        UI.log('日誌讀取失敗: ' + err.message, 'error');
    }
}

async function loadManual() {
    UI.log('正在讀取系統操作手冊...');
    try {
        const resp = await fetch('/api/manual?t=' + Date.now());
        const data = await resp.json();
        if (data.error) throw new Error(data.error);
        
        const container = UI.get('manualContent');
        if (container) {
            // 1. Markdown 渲染
            container.innerHTML = marked.parse(data.content || '目前尚無手冊內容');
            
            // 2. 強化版數學公式渲染 (KaTeX)
            let html = container.innerHTML;
            
            // 處理獨立區塊公式 $$ ... $$
            html = html.replace(/\$\$(.*?)\$\$/gs, (match, p1) => {
                try {
                    return `<div class="katex-display">${katex.renderToString(p1, { displayMode: true })}</div>`;
                } catch (e) { return match; }
            });
            
            // 處理行內公式 $ ... $
            html = html.replace(/\$(.*?)\$/g, (match, p1) => {
                try {
                    return `<span class="katex-inline">${katex.renderToString(p1, { displayMode: false })}</span>`;
                } catch (e) { return match; }
            });
            
            container.innerHTML = html;
            UI.log('手冊渲染完成：已套用全量數學公式解析 (Display & Inline)', 'info');
        }
    } catch (err) {
        UI.log('手冊讀取失敗: ' + err.message, 'error');
    }
}

function closeView(v) { showView('dashboard'); }

async function loadRecentEmails() {
    const resp = await fetch('/api/stats');
    const data = await resp.json();
    const container = UI.get('recentEmails');
    if (!container || !data.recent_emails) return;
    container.innerHTML = data.recent_emails.slice(0, 8).map(e => `
        <div class="p-4 glass-panel hover:bg-white transition-all cursor-pointer">
            <div class="text-xs font-bold truncate">${e.subject}</div>
            <div class="text-[10px] text-slate-400 mt-2">${e.sender || '系統實體'}</div>
        </div>
    `).join('');
}

async function askWiki() {
    const q = UI.get('searchKeyword').value;
    if (!q) return;
    UI.log(`正在詢問 AI: ${q}...`);
    UI.hide('dashboardInitial');
    UI.show('inlineLoading');
    UI.hide('wikiAnswer');
    
    try {
        const resp = await fetch('/api/ask_wiki', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: q })
        });
        const data = await resp.json();
        UI.hide('inlineLoading');
        UI.show('wikiAnswer');
        UI.get('wikiAnswerContent').innerHTML = marked.parse(data.answer || 'AI 未能生成有效回覆');
        UI.renderMath('wikiAnswerContent');
        UI.log('AI 回覆已生成');
    } catch (err) {
        UI.log('AI 詢問失敗: ' + err.message, 'error');
        resetDashboard();
    }
}

function resetDashboard() {
    UI.show('dashboardInitial');
    UI.hide('wikiAnswer');
    UI.hide('inlineLoading');
}

async function loadWikiPage(path) {
    UI.log(`讀取知識頁面: ${path}`);
    UI.hide('wikiGrid');
    UI.show('wikiPageContainer');
    UI.get('wikiActualContent').innerHTML = '<div class="animate-pulse text-slate-400">正在載入實體內容...</div>';
    
    try {
        const resp = await fetch(`/api/wiki/page/${path}`);
        const data = await resp.json();
        
        let htmlContent = marked.parse(data.content || '空文檔');
        
        // Dynamic On-Demand Synthesis Trigger
        if (data.content && data.content.includes('即時總結')) {
            const entityName = path.split('/').pop().replace('.md', '');
            htmlContent += `
                <div class="mt-12 p-8 bg-blue-50 border border-blue-100 rounded-3xl flex flex-col items-center justify-center gap-4 text-center shadow-inner">
                    <i class="fas fa-microchip text-4xl text-blue-400 mb-2 drop-shadow-md"></i>
                    <h4 class="text-blue-900 font-bold text-lg">啟動 AI 深度總結</h4>
                    <p class="text-sm text-blue-600/80 max-w-md">目前僅顯示靜態萃取的骨架。點擊按鈕，呼叫 Local LLM 從數萬封原始郵件中即時還原此實體的技術脈絡與因果關係。</p>
                    <button id="btnSynthesize" onclick="synthesizeEntity('${entityName}', '${path}')" class="btn-primary mt-2">
                        <i class="fas fa-wand-magic-sparkles"></i> 立即合成
                    </button>
                </div>
            `;
        }
        
        UI.get('wikiActualContent').innerHTML = htmlContent;
        UI.renderMath('wikiActualContent');
    } catch (err) { UI.log('頁面讀取失敗: ' + err.message, 'error'); }
}

async function synthesizeEntity(entityName, path) {
    const btn = document.getElementById('btnSynthesize');
    const container = btn.parentElement;
    
    // Create Progress UI
    container.innerHTML = `
        <div class="w-full max-w-md space-y-4 animate-fade-in">
            <div class="flex items-center justify-between text-blue-900 font-bold text-sm">
                <span id="syncStatusText"><i class="fas fa-cog fa-spin mr-2"></i>正在深度還原中...</span>
                <span id="syncTimer">00:00</span>
            </div>
            <div class="w-full bg-blue-100 h-3 rounded-full overflow-hidden shadow-inner">
                <div id="syncProgressBar" class="bg-blue-600 h-full transition-all duration-500 ease-out" style="width: 0%"></div>
            </div>
            <div class="flex justify-between items-center text-[10px] text-blue-400 font-bold tracking-widest uppercase">
                <span>Phase: Semantic Mapping</span>
                <span id="syncPercent">0%</span>
            </div>
        </div>
    `;

    let seconds = 0;
    let progress = 0;
    const startTime = Date.now();
    
    const timerInterval = setInterval(() => {
        seconds++;
        const mins = String(Math.floor(seconds / 60)).padStart(2, '0');
        const secs = String(seconds % 60).padStart(2, '0');
        const timerEl = document.getElementById('syncTimer');
        if (timerEl) timerEl.textContent = `${mins}:${secs}`;
        
        // Simulated progress logic: slow down as it gets closer to 95%
        if (progress < 60) progress += Math.random() * 2;
        else if (progress < 85) progress += Math.random() * 0.5;
        else if (progress < 98) progress += Math.random() * 0.1;
        
        const bar = document.getElementById('syncProgressBar');
        const perc = document.getElementById('syncPercent');
        if (bar) bar.style.width = `${progress}%`;
        if (perc) perc.textContent = `${Math.floor(progress)}%`;
    }, 1000);
    
    try {
        UI.log(`啟動 AI 深度合成任務: ${entityName}`);
        const resp = await fetch('/api/wiki/synthesize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ entity_name: entityName, file_path: path })
        });
        
        const data = await resp.json();
        clearInterval(timerInterval);
        
        if (data.error) throw new Error(data.error);
        
        // Finalize progress
        const bar = document.getElementById('syncProgressBar');
        const perc = document.getElementById('syncPercent');
        if (bar) bar.style.width = '100%';
        if (perc) perc.textContent = '100%';
        
        UI.log(`合成任務完成，耗時 ${seconds} 秒`, 'success');
        
        setTimeout(() => {
            loadWikiPage(path);
        }, 800);
        
    } catch (err) {
        clearInterval(timerInterval);
        UI.log('合成失敗: ' + err.message, 'error');
        container.innerHTML = `
            <div class="text-rose-500 font-bold flex flex-col items-center gap-2">
                <i class="fas fa-exclamation-triangle text-2xl"></i>
                <span>合成中斷: ${err.message}</span>
                <button onclick="loadWikiPage('${path}')" class="btn-primary mt-4 bg-slate-800">重試</button>
            </div>
        `;
    }
}

function backToGrid() {
    UI.show('wikiGrid');
    UI.hide('wikiPageContainer');
}


async function saveSettings() {
    const config = {
        provider: UI.get('settingProvider').value,
        ollama: {
            model: UI.get('settingOllamaModel').value,
            timeout: parseInt(UI.get('settingTimeout').value)
        },
        google: {
            api_key: UI.get('settingGoogleKey').value,
            model: UI.get('settingGoogleModel').value,
            timeout: parseInt(UI.get('settingTimeout').value)
        }
    };
    
    UI.log('正在更新核心配置並重啟 AI 引擎...');
    try {
        const resp = await fetch('/api/ai_config_update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const data = await resp.json();
        UI.log('配置已儲存：' + (data.available ? 'AI 在線' : 'AI 離線'), data.available ? 'success' : 'error');
        closeSettings();
        // 觸發後端重啟分析器
        await fetch('/api/ai_reconnect', { method: 'POST' });
        location.reload();
    } catch (err) { UI.log('配置儲存失敗', 'error'); }
}


async function runKnowledgeMapping() {
    const status = UI.get('pipelineStatus');
    if (!status) return;
    status.textContent = '🚀 啟動獨立知識圖譜重構 (正在處理過濾後的數據)...\n';
    
    const eventSource = new EventSource('/api/pipeline/build_wiki_stream');
    eventSource.onmessage = (event) => {
        if (event.data === 'heartbeat') return;
        status.textContent += event.data;
        status.scrollTop = status.scrollHeight;
        if (event.data.includes('✅ 知識圖譜重構完成')) {
            eventSource.close();
            UI.log('知識圖譜重構完成', 'success');
            loadDashboardStats();
            loadWikiIndex();
        }
    };
    eventSource.onerror = (err) => {
        status.textContent += '\n❌ 任務中斷。\n';
        eventSource.close();
        UI.log('任務執行失敗', 'error');
    };
}

async function runPipeline() {
    const status = UI.get('pipelineStatus');
    if (!status) return;
    status.textContent = '🚀 正在初始化全自動同步程序...\n';
    
    const eventSource = new EventSource('/api/pipeline/stream');
    eventSource.onmessage = (event) => {
        if (event.data === 'heartbeat') return;
        status.textContent += event.data;
        status.scrollTop = status.scrollHeight;
        if (event.data.includes('✅ 全流程執行成功')) {
            eventSource.close();
            UI.log('全自動同步完成', 'success');
            loadDashboardStats();
        }
    };
    eventSource.onerror = (err) => {
        status.textContent += '\n❌ 管道中斷，可能是因為本機未設置 Outlook 帳戶或網路問題。\n';
        eventSource.close();
        UI.log('管道執行失敗', 'error');
    };
}

async function stopPipeline() {
    UI.log('正在嘗試終止後端進程...');
    try {
        const resp = await fetch('/api/pipeline/stop', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            UI.log('進程已強制終止', 'warning');
            UI.get('pipelineStatus').textContent += '\n\n🛑 任務已被使用者手動終止。\n';
        } else {
            UI.log('目前無正在執行的進程', 'info');
        }
    } catch (err) {
        UI.log('停止指令發送失敗: ' + err.message, 'error');
    }
}

async function runBatchSynthesis() {
    const status = UI.get('pipelineStatus');
    if (!status) return;
    status.textContent = '🚀 啟動 AI 批次合成任務...\n';
    
    const eventSource = new EventSource('/api/wiki/batch_synthesize');
    eventSource.onmessage = (event) => {
        status.textContent += event.data;
        status.scrollTop = status.scrollHeight;
        if (event.data.includes('🏁 批次合成任務結束')) {
            eventSource.close();
            UI.log('批次合成任務結束', 'success');
        }
    };
    eventSource.onerror = (err) => {
        status.textContent += '\n❌ 合成任務中斷。\n';
        eventSource.close();
    };
}

async function loadWikiIndex() {
    UI.log('讀取技術百科分組索引...');
    try {
        const groupedData = await fetch('/api/entities').then(r => r.json());
        const grid = UI.get('wikiGrid');
        const sidebar = UI.get('wikiSidebar');
        if (!grid || !sidebar) return;

        grid.innerHTML = '';
        sidebar.innerHTML = '';

        Object.keys(groupedData).sort().forEach(dimension => {
            const entities = groupedData[dimension];
            
            const sidebarSection = document.createElement('div');
            sidebarSection.className = 'py-2';
            sidebarSection.innerHTML = `
                <div class="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-3 px-3">${dimension}</div>
                <div class="space-y-1 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                    ${entities.slice(0, 50).map(e => `
                        <div class="px-3 py-2 text-xs font-medium text-slate-600 hover:bg-white hover:text-blue-600 rounded-lg cursor-pointer transition-all truncate"
                             onclick="loadWikiPage('${e.path}')">
                            ${e.name}
                        </div>
                    `).join('')}
                </div>
            `;
            sidebar.appendChild(sidebarSection);

            entities.forEach(e => {
                const card = document.createElement('div');
                card.className = 'p-6 glass-panel hover:border-blue-500 transition-all cursor-pointer group';
                card.onclick = () => loadWikiPage(e.path);
                card.innerHTML = `
                    <div class="text-[10px] text-blue-500 font-bold mb-2 flex items-center gap-2">
                        <span class="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                        ${dimension} ENTITY
                    </div>
                    <div class="font-bold text-slate-800 mb-2">${e.name}</div>
                    <div class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">${e.description}</div>
                `;
                grid.appendChild(card);
            });
        });
        
        UI.log(`成功載入 ${Object.keys(groupedData).length} 個知識維度`);
    } catch (err) {
        UI.log('索引讀取失敗: ' + err.message, 'error');
    }
}

async function importBundle() {
    const btn = document.getElementById('importBundleBtn');
    if (!btn) return;
    const originalText = btn.innerHTML;
    
    // 移除 confirm 以避開瀏覽器攔截
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner animate-spin mr-2"></i> 正在導入...';
    UI.log('正在啟動數據包導入管道...', 'warning');
    
    try {
        const response = await fetch('/api/pipeline/import_bundle', { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            UI.log('✅ ' + data.message, 'success');
            alert(data.message);
            location.reload(); 
        } else {
            UI.log('❌ ' + data.error, 'error');
            alert("導入失敗: " + data.error);
        }
    } catch (err) {
        UI.log('❌ 網路連接異常', 'error');
        alert("網路連接異常");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

window.importBundle = importBundle;

async function uploadBundle(input) {
    if (!input.files || !input.files[0]) return;
    const file = input.files[0];
    UI.log('正在上傳數據包: ' + file.name, 'warning');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/pipeline/upload_bundle', { method: 'POST', body: formData });
        const data = await response.json();
        
        if (response.ok) {
            UI.log('✅ ' + data.message, 'success');
            // 自動觸發導入程序
            location.reload(); 
        } else {
            UI.log('❌ 上傳失敗: ' + data.error, 'error');
        }
    } catch (err) {
        UI.log('❌ 網路異常: ' + err.message, 'error');
    }
}

window.uploadBundle = uploadBundle;

async function updateSynthesisProgress() {
    try {
        const resp = await fetch('/api/system_progress?t=' + Date.now());
        const data = await resp.json();
        
        const pBar = document.getElementById('physical-progress-bar');
        const pLabel = document.getElementById('physical-percentage-label');
        const qBar = document.getElementById('quality-progress-bar');
        const qLabel = document.getElementById('quality-percentage-label');
        const timer = document.getElementById('system-timer');
        
        if (data.physical_percentage !== undefined) {
            if (pBar) pBar.style.width = data.physical_percentage + '%';
            if (pLabel) pLabel.innerText = Math.round(data.physical_percentage) + '%';
        }
        
        if (data.quality_percentage !== undefined) {
            if (qBar) qBar.style.width = data.quality_percentage + '%';
            if (qLabel) qLabel.innerText = Math.round(data.quality_percentage) + '%';
        }

        if (timer && data.elapsed_seconds !== undefined) {
            const mins = Math.floor(data.elapsed_seconds / 60);
            const secs = data.elapsed_seconds % 60;
            timer.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        
        // 相容性處理：同時更新百科視窗內的進度條
        const oldBar = document.getElementById('synthProgressBar');
        const oldText = document.getElementById('synthProgressText');
        if (oldBar) oldBar.style.width = data.physical_percentage + '%';
        if (oldText) oldText.innerText = data.physical_status;

    } catch (e) {
        console.error('Progress Update Error:', e);
    }
}
window.updateSynthesisProgress = updateSynthesisProgress;

function initDraggableTicker() {
    const ticker = document.getElementById('status-ticker');
    if (!ticker) return;

    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    ticker.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
        
        ticker.style.transition = 'none'; // Disable transition during drag
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        ticker.style.top = (ticker.offsetTop - pos2) + "px";
        ticker.style.left = (ticker.offsetLeft - pos1) + "px";
        ticker.style.bottom = 'auto'; // Remove fixed constraints
        ticker.style.right = 'auto';
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
        ticker.style.transition = 'all 0.3s ease'; // Re-enable if needed, though usually not for drag
    }
}

// Global Initialization
document.addEventListener('DOMContentLoaded', () => {
    initDraggableTicker();
});
