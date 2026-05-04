/**
 * SkillsBuilder Main Application Logic
 * Project: Outlook Database Tool
 * Architecture: State-Driven Workflow
 */

// Global State
let currentSearchType = 'keyword';
let currentSearchResults = [];
let currentSearchQuery = '';

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('SkillsBuilder Lite Activated');
    
    // Check if database exists (passed from Flask)
    const dbExists = window.DB_EXISTS || false;
    
    loadStats(); // Always try to load stats
    
    // Check AI status
    checkAIStatus();
    
    // Initialize Search Listeners
    const searchKeywordElement = document.getElementById('searchKeyword');
    if (searchKeywordElement) {
        searchKeywordElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const val = searchKeywordElement.value.trim();
                if (val.includes('?') || val.length > 10) {
                    askWiki();
                } else {
                    searchEmails();
                }
            }
        });
    }

    // Initialize Mobile Toggle (if still relevant, though mostly removed)
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const sidebar = document.querySelector('.sidebar');
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
}

// Workflow Logic
function updateWorkflowIndicators(step) {
    const indicators = {
        1: document.getElementById('step1-indicator'),
        2: document.getElementById('step2-indicator'),
        3: document.getElementById('step3-indicator')
    };

    Object.keys(indicators).forEach(s => {
        const el = indicators[s];
        if (!el) return;
        
        if (s < step) {
            el.className = 'flex items-center space-x-2 text-brand-success';
            el.querySelector('.w-8').innerHTML = '<i class="fas fa-check text-xs"></i>';
        } else if (s == step) {
            el.className = 'flex items-center space-x-2 text-brand-accent';
        } else {
            el.className = 'flex items-center space-x-2 text-gray-400';
        }
    });
}

function setEmptyState() {
    const elements = ['topSenders', 'recentEmails'];
    elements.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '<p class="text-gray-500 text-center py-8">請先提取郵件資料</p>';
    });
}

// UI Helpers
function showLoading(message = '處理中...') {
    const loadingMessage = document.getElementById('loadingMessage');
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingMessage) loadingMessage.textContent = message;
    if (loadingOverlay) loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) loadingOverlay.classList.add('hidden');
}

function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-TW') + ' ' + date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateString;
    }
}

// Navigation
function showView(viewId, event) {
    if (viewId === 'wiki') {
        const wikiModal = document.getElementById('view-wiki');
        if (wikiModal) {
            wikiModal.classList.remove('hidden');
            loadWikiIndex();
        }
        return;
    }

    document.querySelectorAll('.view-content').forEach(view => {
        view.classList.add('hidden');
    });
    
    const targetView = document.getElementById(`view-${viewId}`);
    if (targetView) targetView.classList.remove('hidden');
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Find the link that was clicked
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    } else if (window.event && window.event.currentTarget) {
        window.event.currentTarget.classList.add('active');
    }
}

// API Integration - Stats
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);

        const totalEmailsElement = document.getElementById('totalEmails');
        if (totalEmailsElement) totalEmailsElement.textContent = data.total_emails.toLocaleString();

        const recentEmailsElement = document.getElementById('recentEmails');
        if (recentEmailsElement && data.recent_emails) {
            if (data.recent_emails.length === 0) {
                recentEmailsElement.innerHTML = '<p class="text-gray-400 text-center py-4">尚無郵件</p>';
            } else {
                recentEmailsElement.innerHTML = data.recent_emails.map(email => `
                    <div class="p-2 hover:bg-gray-50 dark:hover:bg-slate-800 rounded transition-colors border-b border-gray-50 dark:border-slate-800 last:border-0">
                        <p class="font-bold truncate">${email.subject || '(無主旨)'}</p>
                        <div class="flex justify-between text-xs text-gray-400">
                            <span>${email.sender_name}</span>
                            <span>${formatDate(email.received_time).split(' ')[0]}</span>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Stats Error:', error);
    }
}

// API Integration - Search
function setSearchType(type) {
    currentSearchType = type;
    const buttons = ['keyword', 'semantic', 'summary', 'category'];
    
    buttons.forEach(btnId => {
        const btn = document.getElementById(`${btnId}SearchBtn`);
        if (btn) btn.classList.toggle('active', btnId === type);
    });
    
    const descriptions = {
        'keyword': '使用關鍵字搜尋郵件主旨和內容',
        'semantic': '使用 AI 理解搜尋意圖，找到語意相關的郵件',
        'summary': '搜尋包含特定主題或內容摘要的郵件',
        'category': '按郵件類型搜尋（工作、客戶、財務等）'
    };
    
    const placeholders = {
        'keyword': '輸入關鍵字搜尋...',
        'semantic': '描述您要找的內容，例如：關於合約的郵件',
        'summary': '輸入主題或摘要內容...',
        'category': '輸入類型，例如：財務'
    };
    
    document.getElementById('searchDescriptionText').textContent = descriptions[type];
    document.getElementById('searchKeyword').placeholder = placeholders[type];
}

async function searchEmails() {
    const keyword = document.getElementById('searchKeyword').value.trim();
    if (!keyword) return;

    let searchUrl = '/api/search';
    let requestBody = { keyword, limit: 20 };
    
    if (currentSearchType === 'semantic') {
        searchUrl = '/api/semantic_search';
        requestBody = { query: keyword, limit: 20 };
        showLoading('AI 正在進行語意檢索...');
    } else {
        showLoading('搜尋中...');
    }
    
    try {
        const response = await fetch(searchUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentSearchResults = data.results;
        currentSearchQuery = keyword;

        const countEl = document.getElementById('searchCount');
        if (countEl) countEl.textContent = data.count;

        const resultsEl = document.getElementById('searchResults');
        if (resultsEl) {
            if (data.results.length === 0) {
                resultsEl.innerHTML = `<p class="text-gray-500 text-center py-8">找不到 "${keyword}" 的相關郵件</p>`;
            } else {
                resultsEl.innerHTML = data.results.map(email => {
                    const relevance = email.relevance_score ? 
                        `<span class="ml-2 bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs">相關性: ${email.relevance_score}</span>` : '';
                    
                    return `
                        <div class="border border-gray-100 dark:border-slate-700 rounded-xl p-4 hover:shadow-lg transition-all bg-white dark:bg-slate-800 mb-2">
                            <div class="flex justify-between items-start mb-2">
                                <h4 class="font-bold text-gray-800 dark:text-slate-100 flex-1">${email.subject || '(無主旨)'}${relevance}</h4>
                                <span class="text-xs text-gray-400 ml-2">${formatDate(email.received_time)}</span>
                            </div>
                            <p class="text-sm text-blue-600 dark:text-blue-400 mb-2"><i class="fas fa-user-circle mr-1"></i>${email.sender_name}</p>
                            <p class="text-sm text-gray-500 line-clamp-2">${email.body || ''}</p>
                        </div>
                    `;
                }).join('');
            }
        }
    } catch (error) {
        console.error('Search Error:', error);
        alert('搜尋失敗: ' + error.message);
    } finally {
        hideLoading();
    }
}

// AI Functions
function checkAIStatus() {
    fetch('/api/ai_status')
        .then(response => response.json())
        .then(data => {
            const statusEl = document.getElementById('aiStatus');
            if (statusEl) {
                if (data.available) {
                    statusEl.textContent = `AI 在線 (${data.model})`;
                    statusEl.className = 'stat-value text-emerald-500';
                } else {
                    statusEl.textContent = 'AI 離線';
                    statusEl.className = 'stat-value text-rose-500';
                }
            }
        });
}

function analyzeRecentEmails() {
    showLoading('AI 正在分析最近郵件趨勢...');
    fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword: '', limit: 10 })
    })
    .then(r => r.json())
    .then(data => {
        const emailIds = data.results.map(e => e.id);
        return fetch('/api/ai_analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email_ids: emailIds })
        });
    })
    .then(r => r.json())
    .then(showAIResults)
    .catch(err => alert('分析失敗: ' + err))
    .finally(hideLoading);
}

function showAIResults(data) {
    if (data.error) return alert(data.error);
    const resultsDiv = document.getElementById('aiResults');
    const reportDiv = document.getElementById('aiReport');
    resultsDiv.classList.remove('hidden');
    reportDiv.innerHTML = data.report;
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function closeAIResults() {
    document.getElementById('aiResults').classList.add('hidden');
}

// AI Tools Extension
function analyzeSearchResults() {
    if (currentSearchResults.length === 0) return alert('請先進行搜尋');
    showLoading('AI 正在分析搜尋結果...');
    
    const emailIds = currentSearchResults.slice(0, 10).map(e => e.id || e.entry_id);
    fetch('/api/ai_analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_ids: emailIds })
    })
    .then(r => r.json())
    .then(showAIResults)
    .catch(err => alert('分析失敗: ' + err))
    .finally(hideLoading);
}

function generateEmailSummary() {
    if (currentSearchResults.length === 0) return alert('請先搜尋並選擇一封郵件');
    const email = currentSearchResults[0];
    showLoading('AI 正在生成摘要...');
    
    fetch('/api/generate_summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: email.subject, body: email.body })
    })
    .then(r => r.json())
    .then(data => {
        showAIResults({ report: `### 郵件摘要: ${data.subject}\n\n${data.summary}` });
    })
    .catch(err => alert('生成失敗: ' + err))
    .finally(hideLoading);
}

function extractKeyInfo() {
    if (currentSearchResults.length === 0) return alert('請先搜尋並選擇一封郵件');
    const email = currentSearchResults[0];
    showLoading('AI 正在提取重點...');
    
    fetch('/api/extract_key_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: email.subject, body: email.body })
    })
    .then(r => r.json())
    .then(data => {
        let report = `### 重點提取: ${email.subject}\n\n`;
        report += `**關鍵字:** ${data.keywords.join(', ')}\n\n`;
        report += `**重點摘要:**\n${data.key_points}`;
        showAIResults({ report });
    })
    .catch(err => alert('提取失敗: ' + err))
    .finally(hideLoading);
}

function generateReplySuggestions() {
    if (currentSearchResults.length === 0) return alert('請先搜尋並選擇一封郵件');
    const email = currentSearchResults[0];
    showLoading('AI 正在生成回覆建議...');
    
    fetch('/api/generate_reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: email.subject, body: email.body })
    })
    .then(r => r.json())
    .then(data => {
        showAIResults({ report: `### 回覆建議\n\n${data.reply_suggestions}` });
    })
    .catch(err => alert('生成失敗: ' + err))
    .finally(hideLoading);
}

function translateEmail() {
    if (currentSearchResults.length === 0) return alert('請先搜尋並選擇一封郵件');
    const email = currentSearchResults[0];
    const targetLang = prompt('請輸入目標語言 (例如：英文, 日文):', '英文');
    if (!targetLang) return;
    
    showLoading('AI 正在翻譯...');
    fetch('/api/translate_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: email.subject, body: email.body, target_language: targetLang })
    })
    .then(r => r.json())
    .then(data => {
        showAIResults({ report: `### 翻譯結果 (${data.target_language})\n\n**主旨:** ${data.translated_subject}\n\n**內容:**\n${data.translated_body}` });
    })
    .catch(err => alert('翻譯失敗: ' + err))
    .finally(hideLoading);
}

function analyzeEmailInsights() {
    showLoading('AI 正在生成全量洞察...');
    fetch('/api/email_insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(r => r.json())
    .then(data => {
        showAIResults({ report: `### 郵件資料庫洞察報告\n\n${data.insights}` });
    })
    .catch(err => alert('分析失敗: ' + err))
    .finally(hideLoading);
}

// Wiki Logic
function loadWikiIndex() {
    const wikiIndex = document.getElementById('wikiIndex');
    wikiIndex.innerHTML = '<div class="p-4 text-center"><i class="fas fa-spinner fa-spin"></i></div>';
    
    fetch('/api/wiki/index')
        .then(r => r.json())
        .then(data => {
            const lines = data.content.split('\n');
            let html = '<div class="space-y-1">';
            lines.forEach(line => {
                const match = line.match(/\[(.*?)\]\((.*?)\)/);
                if (match) {
                    html += `
                        <button onclick="loadWikiPage('${match[2]}')" class="w-full text-left p-3 rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 text-sm transition-colors flex items-center gap-2">
                            <i class="fas fa-file-alt text-blue-400"></i>
                            <span>${match[1]}</span>
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
            contentEl.innerHTML = `
                <div class="prose dark:prose-invert max-w-none">
                    ${marked.parse(data.content)}
                </div>
                <button onclick="loadWikiIndex()" class="btn btn-secondary mt-8">
                    <i class="fas fa-arrow-left mr-2"></i>返回索引
                </button>
            `;
        });
}

async function askWiki() {
    const query = document.getElementById('wikiQuery').value;
    if (!query) return;
    
    const answerDiv = document.getElementById('wikiAnswer');
    answerDiv.classList.remove('hidden');
    answerDiv.innerHTML = '<div class="p-8 text-center"><div class="loading-spinner mx-auto mb-4"></div><p>AI 正在分析知識庫，請稍候...</p></div>';
    
    try {
        const response = await fetch('/api/ask_wiki', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        const data = await response.json();
        answerDiv.innerHTML = marked.parse(data.answer || data.error);
    } catch (err) {
        answerDiv.innerHTML = `<p class="text-rose-500">檢索失敗: ${err.message}</p>`;
    }
}

// Maintenance
function buildDatabase() {
    const activePlan = document.querySelector('.plan-option.active');
    const planId = activePlan ? activePlan.dataset.plan : '2';
    
    showLoading('正在啟動提取任務...');
    fetch('/api/build_database_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        alert(`✅ ${data.plan_name} 執行成功！已提取 ${data.extracted_count} 封郵件。`);
        location.reload();
    })
    .catch(err => alert('提取失敗: ' + err.message))
    .finally(hideLoading);
}

function exportData() {
    window.location.href = '/api/export';
}

function setupAI() {
    alert('AI 設定模組開發中...\n目前預設連接本機 Ollama 服務。');
}

function toggleCustomPlan() {
    const section = document.getElementById('customPlanSection');
    if (section) section.classList.toggle('hidden');
}

function buildCustomPlan() {
    const count = document.getElementById('customEmailCount').value;
    const limit = document.getElementById('customBodyLimit').value;
    
    showLoading('執行自訂提取方案...');
    fetch('/api/build_database_custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_count: parseInt(count), body_limit: parseInt(limit) })
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) throw new Error(data.error);
        alert(`✅ 自訂方案執行成功！已提取 ${data.extracted_count} 封郵件。`);
        location.reload();
    })
    .catch(err => alert('執行失敗: ' + err.message))
    .finally(hideLoading);
}

function runFullPipeline() {
    if (!confirm('將啟動「一鍵自動化」流程：\n1. 提取 Outlook 郵件與附件\n2. AI 分析並建構知識圖譜\n\n這可能需要幾分鐘時間，確定繼續？')) return;
    
    showLoading('一鍵同步與知識建構中，請勿關閉視窗...');
    fetch('/api/full_pipeline', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                alert('流程中斷: ' + data.error + '\n' + (data.details || ''));
            } else {
                alert('✅ 全流程執行成功！知識庫已更新。');
                location.reload();
            }
        })
        .catch(err => alert('系統錯誤: ' + err))
        .finally(hideLoading);
}

function fullIngest() {
    if (!confirm('執行完整提取將會重置本地附件庫，確定繼續？')) return;
    showLoading('全量同步中...');
    fetch('/api/ingest', { method: 'POST' })
        .then(r => r.json())
        .then(() => location.reload())
        .catch(err => alert(err))
        .finally(hideLoading);
}

function buildWiki() {
    showLoading('正在建構知識圖譜...');
    fetch('/api/build_wiki', { method: 'POST' })
        .then(r => r.json())
        .then(() => alert('Wiki 建構完成！'))
        .finally(hideLoading);
}

async function clearAndRebuild() {
    if (!confirm('⚠️ 警告：這將刪除所有已提取的資料。')) return;
    showLoading('清理中...');
    await fetch('/api/clear_database', { method: 'POST' });
    location.reload();
}
