// SkillsBuilder Lite - Main JS
// Digital Art Director & Architect Edition

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    checkAIStatus();
    loadRecentEmails();
    
    // 定期更新
    setInterval(loadDashboardStats, 30000);
    setInterval(checkAIStatus, 15000);
});

// Global State
let searchState = {
    keyword: '',
    year: null,
    page: 1,
    totalPages: 1
};

function setSearchValue(val) {
    const input = document.getElementById('searchKeyword');
    if (input) {
        input.value = val;
        searchState.year = null; // Clear year filter when manually typing or clicking new keyword
        searchEmails(1);
    }
}

function setYearFilter(year) {
    searchState.year = year;
    searchEmails(1);
}

function togglePassword(id) {
    const el = document.getElementById(id);
    if (el) {
        el.type = el.type === 'password' ? 'text' : 'password';
    }
}

function clearSearch() {
    const input = document.getElementById('searchKeyword');
    const results = document.getElementById('searchResultsCard');
    const dashboard = document.getElementById('dashboardInitial');
    const wiki = document.getElementById('wikiAnswer');
    
    if (input) input.value = '';
    if (results) results.classList.add('hidden');
    if (dashboard) dashboard.classList.remove('hidden');
    if (wiki) wiki.classList.add('hidden');
    
    // Reset state
    searchState.keyword = '';
    searchState.page = 1;
}

// UI Logic
function showLoading(msg = '處理中...') {
    const overlay = document.getElementById('loadingOverlay');
    const message = document.getElementById('loadingMessage');
    const logContainer = document.getElementById('log-container');
    
    if (overlay) overlay.classList.remove('hidden');
    if (message) message.textContent = msg;
    if (logContainer) logContainer.classList.add('hidden');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('hidden');
}

function showInlineLoading(msg = '處理中...') {
    const el = document.getElementById('inlineLoading');
    const msgEl = document.getElementById('inlineLoadingMessage');
    if (el) el.classList.remove('hidden');
    if (msgEl) msgEl.textContent = msg;
    
    // Hide results while loading for better focus
    document.getElementById('searchResultsCard').classList.add('hidden');
    document.getElementById('wikiAnswer').classList.add('hidden');
}

function hideInlineLoading() {
    const el = document.getElementById('inlineLoading');
    if (el) el.classList.add('hidden');
}

function showView(viewId) {
    if (viewId === 'wiki') {
        document.getElementById('view-wiki').classList.remove('hidden');
        loadWikiIndex();
    }
}

function loadDashboardStats() {
    fetch('/api/dashboard_stats')
        .then(r => r.json())
        .then(data => {
            document.getElementById('dashEntityCount').textContent = data.entity_count || 0;
            document.getElementById('dashConceptCount').textContent = data.concept_count || 0;
            document.getElementById('dashSenderCount').textContent = data.unique_senders || 0;
            document.getElementById('dashTotalMails').textContent = data.total_emails || 0;
        })
        .catch(err => console.error('Dashboard Stats Error:', err));
}

function loadRecentEmails() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById('recentEmails');
            if (data.recent_emails && data.recent_emails.length > 0) {
                container.innerHTML = data.recent_emails.map(email => `
                    <div class="flex justify-between items-center p-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 rounded-xl transition-all cursor-default">
                        <div class="truncate mr-4">
                            <div class="font-bold text-slate-700 dark:text-slate-200">${email.subject}</div>
                            <div class="text-[10px] text-slate-400">${email.sender_name}</div>
                        </div>
                        <div class="text-[10px] text-slate-400 whitespace-nowrap">${email.received_time.split(' ')[0]}</div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<div class="p-4 text-center text-slate-400">尚無提取紀錄</div>';
            }
        });
}

function searchEmails(page = 1) {
    const keyword = document.getElementById('searchKeyword').value;
    if (!keyword) return;
    
    // Reset state if it's a new keyword
    if (keyword !== searchState.keyword) {
        searchState.keyword = keyword;
        searchState.page = 1;
    } else {
        searchState.page = page;
    }
    
    showInlineLoading(searchState.page === 1 ? '搜尋中...' : `正在載入第 ${searchState.page} 頁...`);
    
    fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            keyword: searchState.keyword,
            year: searchState.year,
            page: searchState.page,
            limit: 20
        })
    })
    .then(r => r.json())
    .then(data => {
        const container = document.getElementById('searchResults');
        const card = document.getElementById('searchResultsCard');
        const dashboard = document.getElementById('dashboardInitial');
        const wikiAnswer = document.getElementById('wikiAnswer');
        const pagination = document.getElementById('pagination');
        
        if (dashboard) dashboard.classList.add('hidden');
        if (wikiAnswer) wikiAnswer.classList.add('hidden');
        if (card) card.classList.remove('hidden');
        
        const countEl = document.getElementById('searchCount');
        if (countEl) countEl.textContent = `共找到 ${data.total_count} 筆結果`;

        // Render Year Distribution Chips
        const suggestionBox = document.querySelector('.search-suggestions');
        if (suggestionBox && data.year_distribution) {
            let yearHtml = '<span style="color: #64748b; font-size: 11px; margin-right: 10px;">年份分佈:</span>';
            // Add a "Clear" chip if a year is selected
            if (searchState.year) {
                yearHtml += `<span class="suggestion-chip" style="background: #ef4444; color: white;" onclick="setYearFilter(null)">清除過濾 (${searchState.year})</span>`;
            }
            for (const [year, count] of Object.entries(data.year_distribution)) {
                const isActive = searchState.year === year;
                const activeStyle = isActive ? 'background: #3b82f6; color: white;' : '';
                yearHtml += `<span class="suggestion-chip" style="${activeStyle}" onclick="setYearFilter('${year}')">${year} (${count})</span>`;
            }
            suggestionBox.innerHTML = yearHtml;
        }
        
        searchState.totalPages = data.total_pages;
        
        if (data.results && data.results.length > 0) {
            container.innerHTML = data.results.map(res => `
                <div class="p-4 border-b border-slate-100 dark:border-slate-700 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-all rounded-2xl">
                    <div class="flex justify-between mb-1">
                        <span class="font-bold text-blue-500">${res.sender_name}</span>
                        <span class="text-xs text-slate-400">${res.received_time}</span>
                    </div>
                    <div class="font-bold mb-2 text-slate-800 dark:text-slate-100">${res.subject}</div>
                    <div class="text-sm text-slate-500 dark:text-slate-400 line-clamp-3">${res.body}</div>
                </div>
            `).join('');
            
            // Update Pagination UI
            if (pagination && searchState.totalPages > 1) {
                pagination.classList.remove('hidden');
                document.getElementById('pageInfo').textContent = `第 ${data.page} / ${data.total_pages} 頁`;
                document.getElementById('prevPage').disabled = data.page <= 1;
                document.getElementById('nextPage').disabled = data.page >= data.total_pages;
                
                // Add visual feedback for disabled buttons
                document.getElementById('prevPage').style.opacity = data.page <= 1 ? '0.5' : '1';
                document.getElementById('nextPage').style.opacity = data.page >= data.total_pages ? '0.5' : '1';
            } else if (pagination) {
                pagination.classList.add('hidden');
            }
            
            // Scroll to top of results if on a new page
            if (page > 1 && card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } else {
            container.innerHTML = '<div class="p-8 text-center text-slate-400">未找到相關郵件</div>';
            if (pagination) pagination.classList.add('hidden');
        }
    })
    .finally(hideInlineLoading);
}

function changePage(delta) {
    const newPage = searchState.page + delta;
    if (newPage >= 1 && newPage <= searchState.totalPages) {
        searchEmails(newPage);
    }
}

function askWiki() {
    const query = document.getElementById('searchKeyword').value;
    if (!query) return;
    
    showInlineLoading('AI 思考中...');
    fetch('/api/ask_wiki', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
    })
    .then(r => r.json())
    .then(data => {
        const wikiAnswer = document.getElementById('wikiAnswer');
        const dashboard = document.getElementById('dashboardInitial');
        const searchCard = document.getElementById('searchResultsCard');
        
        dashboard.classList.add('hidden');
        searchCard.classList.add('hidden');
        wikiAnswer.classList.remove('hidden');
        
        if (data.error) {
            wikiAnswer.innerHTML = `<div class="text-rose-500 font-bold"><i class="fas fa-exclamation-triangle mr-2"></i>API 錯誤: ${data.error}</div>`;
        } else {
            // Using marked if available
            const formattedAnswer = typeof marked !== 'undefined' ? marked.parse(data.answer) : data.answer.replace(/\n/g, '<br>');
            wikiAnswer.innerHTML = `
                <div class="flex items-center gap-2 mb-6 text-indigo-500 font-bold border-b border-indigo-100 dark:border-indigo-900/30 pb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 12L2.1 12.1"/><path d="M12 12l9.9-0.1"/><path d="M12 12V22"/><path d="M12 12l-7-7"/><path d="M12 12l7 7"/></svg>
                    AI 深度分析結果
                </div>
                <div class="text-slate-700 dark:text-slate-200 leading-relaxed">${formattedAnswer}</div>
            `;
        }
    })
    .catch(err => {
        const wikiAnswer = document.getElementById('wikiAnswer');
        wikiAnswer.classList.remove('hidden');
        wikiAnswer.innerHTML = `<div class="text-rose-500 font-bold">API 錯誤: ${err.message}</div>`;
    })
    .finally(hideInlineLoading);
}

function loadWikiIndex() {
    const wikiIndex = document.getElementById('wikiIndex');
    const wikiContent = document.getElementById('wikiContent');
    
    wikiIndex.innerHTML = '<div class="p-4 text-center"><i class="fas fa-spinner fa-spin"></i></div>';
    
    fetch('/api/wiki/index')
        .then(r => r.json())
        .then(data => {
            const lines = data.content.split('\n');
            let html = '<div class="space-y-1">';
            
            if (data.content.includes('尚未建構')) {
                wikiContent.innerHTML = `
                    <div class="h-full flex flex-col items-center justify-center text-center p-12">
                        <div class="w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6">
                            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                        </div>
                        <h3 class="text-2xl font-bold mb-2">知識圖譜尚未建構</h3>
                        <p class="text-slate-500 mb-8 max-w-md">我們需要透過 AI 分析您的郵件，提取出專案、人物與核心概念，才能建立連結。</p>
                        <button onclick="buildWikiFromModal()" class="btn btn-primary btn-lg px-10 py-4 shadow-xl shadow-blue-500/20">
                            <i class="fas fa-magic mr-2"></i> 立即啟動 AI 建構
                        </button>
                    </div>
                `;
                wikiIndex.innerHTML = '';
                return;
            }

            lines.forEach(line => {
                const match = line.match(/\[(.*?)\]\((.*?)\)/);
                if (match) {
                    const name = match[1];
                    const path = match[2];
                    html += `
                        <button onclick="loadWikiPage('${path}')" class="w-full text-left p-3 rounded-xl hover:bg-white dark:hover:bg-slate-800 transition-all text-sm flex items-center gap-3 group">
                            <span class="w-2 h-2 rounded-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-all"></span>
                            <span class="truncate">${name}</span>
                        </button>`;
                }
            });
            html += '</div>';
            wikiIndex.innerHTML = html;
        });
}

function loadWikiPage(path) {
    const contentEl = document.getElementById('wikiContent');
    contentEl.innerHTML = '<div class="p-12 text-center"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
    
    fetch(`/api/wiki/page/${path}`)
        .then(r => r.json())
        .then(data => {
            const formatted = typeof marked !== 'undefined' ? marked.parse(data.content) : data.content;
            contentEl.innerHTML = `
                <div class="prose dark:prose-invert max-w-none">
                    ${formatted}
                </div>
                <button onclick="loadWikiIndex()" class="btn btn-secondary mt-8"><i class="fas fa-arrow-left mr-2"></i>返回索引</button>
            `;
        });
}

function buildWikiFromModal() {
    // 隱藏 Wiki 視窗並啟動流式進度條，避免超時
    document.getElementById('view-wiki').classList.add('hidden');
    runPipelineWithStream();
}

function checkAIStatus() {
    fetch('/api/ai_status')
        .then(response => response.json())
        .then(data => {
            const statusEl = document.getElementById('aiStatus');
            if (statusEl) {
                const dot = statusEl.querySelector('span');
                if (data.available) {
                    statusEl.childNodes[statusEl.childNodes.length - 1].textContent = ` AI 在線 (${data.model})`;
                    if (dot) {
                        dot.className = 'w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]';
                    }
                } else {
                    statusEl.childNodes[statusEl.childNodes.length - 1].textContent = ' AI 離線 (點擊重連)';
                    if (dot) {
                        dot.className = 'w-2 h-2 rounded-full bg-rose-500 animate-pulse';
                    }
                }
            }
        });
}


function reconnectAI() {
    showLoading('正在重新連線 AI 服務...');
    fetch('/api/ai_reconnect', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.available) {
                alert('✅ AI 已重新連線: ' + data.model);
                checkAIStatus();
            } else {
                const msg = data.provider === 'google' 
                    ? '❌ 重連失敗，請檢查 Gemini API Key 是否有效' 
                    : '❌ 重連失敗，請檢查 Ollama 是否運行';
                alert(msg);
            }
        })
        .catch(err => alert('❌ 連線異常: ' + err.message))
        .finally(hideLoading);
}


async function runPipelineWithStream() {
    const overlay = document.getElementById('loadingOverlay');
    const message = document.getElementById('loadingMessage');
    const logContainer = document.getElementById('log-container');
    
    if (overlay) overlay.classList.remove('hidden');
    if (logContainer) {
        logContainer.classList.remove('hidden');
        logContainer.innerHTML = '';
    }
    
    try {
        const response = await fetch('/api/pipeline/stream');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            lines.forEach(line => {
                if (line.startsWith('data: ')) {
                    const content = line.replace('data: ', '').trim();
                    if (content) {
                        const logLine = document.createElement('div');
                        logLine.className = 'py-0.5 border-b border-slate-700/30 last:border-0';
                        if (content.includes('🚀') || content.includes('🧠')) logLine.className += ' text-blue-400 font-bold mt-2';
                        if (content.includes('✅') || content.includes('✨')) logLine.className += ' text-emerald-400';
                        logLine.textContent = content;
                        logContainer.appendChild(logLine);
                        logContainer.scrollTop = logContainer.scrollHeight;
                        
                        if (content.includes('🚀')) message.textContent = '正在提取郵件...';
                        if (content.includes('🧠')) message.textContent = '正在建構知識圖譜...';
                    }
                }
            });
        }
        
        if (logContainer.innerText.includes('✅')) {
            alert('✅ 全流程執行成功！');
            location.reload();
        } else {
            setTimeout(() => { if (overlay) overlay.classList.add('hidden'); }, 3000);
        }
    } catch (err) {
        alert('系統錯誤: ' + err.message);
        if (overlay) overlay.classList.add('hidden');
    }
}

function runFullPipeline() {
    runPipelineWithStream();
}

function runImportantFoldersIngest() {
    const count = prompt('請輸入每個資料夾同步的郵件數量：', '100');
    if (!count) return;
    showLoading('同步中...');
    fetch('/api/important_folders_ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_per_folder: parseInt(count) })
    })
    .then(r => r.json())
    .then(data => {
        alert('✅ 重要資料夾同步完成');
        location.reload();
    })
    .catch(err => alert('同步失敗: ' + err.message))
    .finally(hideLoading);
}



// Settings Logic
function openSettings() {
    console.log("⚙️ Launching AI Control Center");
    const modal = document.getElementById('aiControlCenter');
    const bg = document.getElementById('modalOverlayBg');
    
    if (modal) {
        modal.classList.remove('hidden');
        if (bg) bg.classList.remove('hidden');
    }

    fetch('/api/ai_config')
        .then(r => r.json())
        .then(config => {
            document.getElementById('settingProvider').value = config.provider || 'ollama';
            if (config.google) {
                document.getElementById('settingGeminiKey').value = config.google.api_key || '';
                document.getElementById('settingGeminiModel').value = config.google.model || 'gemini-1.5-pro';
            }
            toggleSettingFields();
        });
}

function closeSettings() {
    const modal = document.getElementById('aiControlCenter');
    const bg = document.getElementById('modalOverlayBg');
    if (modal) modal.classList.add('hidden');
    if (bg) bg.classList.add('hidden');
}
window.openAISettings = openSettings;


function fetchOllamaModels(selectedModel) {
    const modelEl = document.getElementById('settingOllamaModel');
    modelEl.innerHTML = '<option value="">正在載入...</option>';
    
    fetch('/api/ollama_models')
        .then(r => r.json())
        .then(data => {
            if (data.models && data.models.length > 0) {
                modelEl.innerHTML = data.models.map(m => 
                    `<option value="${m.name}" ${m.name === selectedModel ? 'selected' : ''}>${m.name}</option>`
                ).join('');
            } else {
                const errorMsg = data.error || '無可用模型 (請確認 Ollama 已啟動)';
                modelEl.innerHTML = `<option value="">${errorMsg}</option>`;
            }
        })
        .catch(err => {
            modelEl.innerHTML = `<option value="">連線錯誤: ${err.message}</option>`;
        });
}

function toggleSettingFields() {
    const provider = document.getElementById('settingProvider').value;
    document.getElementById('ollamaFields').classList.toggle('hidden', provider !== 'ollama');
    document.getElementById('geminiFields').classList.toggle('hidden', provider !== 'google');
}

function saveSettings() {
    const provider = document.getElementById('settingProvider').value;
    const config = {
        provider: provider,
        ollama: {
            url: document.getElementById('settingOllamaUrl').value,
            model: document.getElementById('settingOllamaModel').value,
            timeout: 120
        },
        google: {
            api_key: document.getElementById('settingGeminiKey').value,
            model: document.getElementById('settingGeminiModel').value
        }
    };
    
    showLoading('儲存設定中...');
    fetch('/api/ai_config_update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) alert('儲存失敗: ' + data.error);
        else {
            alert('✅ 設定已套用');
            closeSettings();
            location.reload();
        }
    })
    .finally(hideLoading);
}

// Footer helper or other utils can go here
