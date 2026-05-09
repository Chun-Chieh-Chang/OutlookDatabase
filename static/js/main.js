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
    lastSyncNodeCount: 0
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
    
    setInterval(() => {
        if (AppState.currentView === '3d') sync3DGraph();
        loadDashboardStats();
        checkAIStatus();
    }, 8000);
});

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

        graphInstance.d3Force('link').distance(60);
        graphInstance.controls().autoRotate = true;
    } catch (err) { UI.log('3D 引擎崩潰: ' + err.message, 'error'); }
}

async function sync3DGraph() {
    if (!graphInstance) return;
    UI.log('執行增量同步檢查...');
    try {
        const resp = await fetch('/api/graph_data?t=' + Date.now());
        const data = await resp.json();
        if (data.nodes.length !== AppState.lastSyncNodeCount) {
            UI.log(`⚡ 偵測到知識爆炸！節點激增: ${data.nodes.length}`, 'info');
            graphInstance.graphData(data);
            AppState.lastSyncNodeCount = data.nodes.length;
        }
    } catch (err) { UI.log('實時同步失效', 'error'); }
}

function showView(v) {
    AppState.currentView = v;
    UI.log(`切換導航: ${v.toUpperCase()}`);
    
    // Hide all views including the new sync and manual views
    ['view-dashboard', 'view-wiki', 'view-3d', 'view-sync', 'view-manual', 'view-devlog'].forEach(id => UI.hide(id));
    
    if (v === 'dashboard') { UI.show('view-dashboard'); }
    else if (v === 'wiki') { UI.show('view-wiki'); loadWikiIndex(); }
    else if (v === '3d') { UI.show('view-3d'); init3DGraph(); }
    else if (v === 'sync') { UI.show('view-sync'); }
    else if (v === 'manual') { UI.show('view-manual'); loadManual(); }
    else if (v === 'devlog') { UI.show('view-devlog'); loadDevLog(); }
}

async function loadDevLog() {
    UI.log('正在讀取系統進化與故障確效紀錄...');
    try {
        const resp = await fetch('/api/dev_log?t=' + Date.now());
        const data = await resp.json();
        if (data.error) throw new Error(data.error);
        const container = UI.get('devLogContent');
        if (container) {
            container.innerHTML = marked.parse(data.content || '目前尚無日誌');
            UI.renderMath('devLogContent');
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
            container.innerHTML = marked.parse(data.content || '目前尚無手冊內容');
            UI.renderMath('manualContent');
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

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const next = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    UI.get('themeIcon').className = next === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    UI.log(`切換主題至: ${next.toUpperCase()}`);
}

async function saveSettings() {
    const config = {
        provider: UI.get('settingProvider').value
    };
    try {
        await fetch('/api/ai_config_update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        UI.log('配置已儲存，正在重新初始化...');
        closeSettings();
        location.reload();
    } catch (err) { UI.log('配置儲存失敗', 'error'); }
}

function openSettings() { UI.show('settingsModal'); }
function closeSettings() { UI.hide('settingsModal'); }

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
