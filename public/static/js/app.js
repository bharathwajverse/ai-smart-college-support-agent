/**
 * CampusResolve AI - Frontend Controller
 * Connects UI with FastAPI Agent Backend.
 */

const API_BASE = "";

// Global State
let currentTab = "chat";
let allTickets = [];
let selectedTicket = null;
let categoryChart = null;
let priorityChart = null;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initChat();
    initComplaintForm();
    initEmergencyFeatures();
    initFilters();
    loadTickets();
    loadMetrics();
    loadFaiDiagnostics();
});

// --- Tab Management ---
function initTabs() {
    const tabButtons = document.querySelectorAll(".nav-tab-btn");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    currentTab = tabId;
    // Update button states
    document.querySelectorAll(".nav-tab-btn").forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("bg-indigo-600", "text-white");
            btn.classList.remove("text-slate-400", "hover:bg-slate-800");
        } else {
            btn.classList.remove("bg-indigo-600", "text-white");
            btn.classList.add("text-slate-400", "hover:bg-slate-800");
        }
    });

    // Update section views
    document.querySelectorAll(".tab-content-section").forEach(sec => {
        sec.classList.add("hidden");
    });
    const activeSection = document.getElementById(`section-${tabId}`);
    if (activeSection) {
        activeSection.classList.remove("hidden");
    }

    // Refresh data if relevant
    if (tabId === "track" || tabId === "admin") {
        loadTickets();
    } else if (tabId === "analytics") {
        loadMetrics();
    } else if (tabId === "inspector") {
        loadFaiDiagnostics();
    }
}

// --- Chat Assistant (Module VI Knowledge QA) ---
function initChat() {
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    const quickPrompts = document.querySelectorAll(".quick-chat-prompt");

    sendBtn.addEventListener("click", () => sendChatMessage());
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    quickPrompts.forEach(btn => {
        btn.addEventListener("click", () => {
            chatInput.value = btn.innerText.replace(/["]/g, '').trim();
            sendChatMessage();
        });
    });
}

async function sendChatMessage() {
    const chatInput = document.getElementById("chat-input");
    const query = chatInput.value.trim();
    if (!query) return;

    chatInput.value = "";
    appendChatMessage("student", query);

    // AI typing indicator
    const typingId = appendTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        removeTypingIndicator(typingId);

        let formattedMsg = data.answer;
        if (data.escalation_required) {
            formattedMsg += `\n\n🚨 **URGENT**: ${data.suggested_action}`;
        }
        appendChatMessage("agent", formattedMsg, data.category, data.confidence);
    } catch (err) {
        removeTypingIndicator(typingId);
        appendChatMessage("agent", "Error connecting to AI Assistant. Please check if the backend is running.");
    }
}

function appendChatMessage(sender, text, category = null, confidence = null) {
    const container = document.getElementById("chat-messages-container");
    const msgDiv = document.createElement("div");
    msgDiv.className = `flex ${sender === "student" ? "justify-end" : "justify-start"} mb-4`;

    const isStudent = sender === "student";
    const bgClass = isStudent ? "bg-indigo-600 text-white rounded-tr-none" : "bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none";

    let badgeHtml = "";
    if (category) {
        badgeHtml = `
            <div class="flex items-center gap-2 mt-2 pt-2 border-t border-slate-700 text-xs text-indigo-400">
                <span>🏷️ Inferred Category: <strong>${category}</strong></span>
                ${confidence ? `<span>(Confidence: ${(confidence * 100).toFixed(0)}%)</span>` : ""}
            </div>
        `;
    }

    msgDiv.innerHTML = `
        <div class="max-w-[80%] rounded-2xl px-5 py-3.5 ${bgClass} shadow-md">
            <div class="text-xs font-semibold uppercase tracking-wider mb-1 ${isStudent ? 'text-indigo-200' : 'text-slate-400'}">
                ${isStudent ? "You" : "🤖 CampusResolve Support Agent"}
            </div>
            <div class="text-sm leading-relaxed whitespace-pre-wrap">${formatMarkdown(text)}</div>
            ${badgeHtml}
        </div>
    `;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
    const container = document.getElementById("chat-messages-container");
    const id = "typing-" + Date.now();
    const div = document.createElement("div");
    div.id = id;
    div.className = "flex justify-start mb-4";
    div.innerHTML = `
        <div class="bg-slate-800 text-slate-400 border border-slate-700 rounded-2xl rounded-tl-none px-4 py-3 flex items-center space-x-2">
            <span class="animate-pulse">🤖 Agent reasoning...</span>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function formatMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>');
}


// --- Complaint Submission & Live Agent Pipeline ---
function initComplaintForm() {
    const form = document.getElementById("complaint-form");
    const anonToggle = document.getElementById("form-is-anonymous");
    const studentInfoFields = document.getElementById("student-info-fields");

    anonToggle.addEventListener("change", (e) => {
        if (e.target.checked) {
            studentInfoFields.classList.add("opacity-40", "pointer-events-none");
        } else {
            studentInfoFields.classList.remove("opacity-40", "pointer-events-none");
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await submitGrievance();
    });

    // Demo Pre-fill presets
    document.querySelectorAll(".demo-preset-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const preset = btn.getAttribute("data-preset");
            applyDemoPreset(preset);
        });
    });
}

function applyDemoPreset(preset) {
    const subject = document.getElementById("form-subject");
    const desc = document.getElementById("form-description");
    const loc = document.getElementById("form-location");
    const cat = document.getElementById("form-category");
    const anon = document.getElementById("form-is-anonymous");

    if (preset === "ragging") {
        subject.value = "Urgent: Ragging and harassment in Nilgiri Hostel 2nd floor";
        desc.value = "First year juniors are being forced to stay awake past 2 AM, harassed verbally, and threatened by seniors. Requesting immediate confidential intervention.";
        loc.value = "Nilgiri Hostel, Room 214";
        cat.value = "Anti-Ragging & Safety";
        anon.checked = true;
    } else if (preset === "wifi") {
        subject.value = "Campus WiFi completely dead in Shivalik Hostel Block C";
        desc.value = "The WiFi router on the 3rd floor corridor has no internet connection for 24 hours. Multiple students have online project submissions due today.";
        loc.value = "Shivalik Hostel Block C, 3rd Floor";
        cat.value = "IT & Infrastructure";
        anon.checked = false;
    } else if (preset === "mess") {
        subject.value = "Stale food and contaminated water in Central Mess";
        desc.value = "Tonight at dinner, the rice smelled foul and several students complained of severe stomach pain. The water purifier in the mess hall is also leaking.";
        loc.value = "Central Mess Hall 1";
        cat.value = "Mess & Canteen";
        anon.checked = false;
    } else if (preset === "fees") {
        subject.value = "Duplicate fee deduction for semester examination";
        desc.value = "Exam fee of Rs. 2500 was deducted twice from my bank account (Ref UTR982347101). College portal still says pending receipt. Please refund.";
        loc.value = "Accounts Portal";
        cat.value = "Accounts & Fees";
        anon.checked = false;
    }
}

async function submitGrievance() {
    const submitBtn = document.getElementById("form-submit-btn");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>⚙️ AI Agent Executing Pipeline (NLP ➔ Rules ➔ Bayes ➔ A* Plan)...</span>`;

    const payload = {
        student_name: document.getElementById("form-name").value || "Anonymous",
        student_id: document.getElementById("form-id").value || "N/A",
        email: document.getElementById("form-email").value || "",
        phone: document.getElementById("form-phone").value || "",
        is_anonymous: document.getElementById("form-is-anonymous").checked,
        subject: document.getElementById("form-subject").value,
        description: document.getElementById("form-description").value,
        location: document.getElementById("form-location").value,
        category: document.getElementById("form-category").value || null
    };

    try {
        const response = await fetch(`${API_BASE}/api/complaints`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Failed to submit grievance");
        }

        const ticket = await response.json();
        renderSubmissionSuccess(ticket);
        loadTickets();
        loadMetrics();
    } catch (err) {
        alert("Error submitting complaint: " + err.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>🚀 Submit to AI Agent Pipeline</span>`;
    }
}

function renderSubmissionSuccess(ticket) {
    const modal = document.getElementById("submission-success-modal");
    modal.classList.remove("hidden");

    document.getElementById("modal-ticket-code").innerText = ticket.ticket_code;
    document.getElementById("modal-category").innerText = ticket.category;
    document.getElementById("modal-priority").innerText = ticket.priority;
    document.getElementById("modal-priority").className = `px-3 py-1 rounded-full text-xs font-bold badge-${ticket.priority.toLowerCase()}`;
    document.getElementById("modal-sla").innerText = `${ticket.sla_hours} Hours`;
    document.getElementById("modal-bayesian-risk").innerText = `${(ticket.escalation_risk * 100).toFixed(1)}%`;
    document.getElementById("modal-department").innerText = ticket.assigned_department;

    // Cluster notice
    const clusterBox = document.getElementById("modal-cluster-box");
    if (ticket.cluster_id) {
        clusterBox.classList.remove("hidden");
        document.getElementById("modal-cluster-id").innerText = ticket.cluster_id;
    } else {
        clusterBox.classList.add("hidden");
    }

    // Rules fired
    const rulesContainer = document.getElementById("modal-rules-list");
    rulesContainer.innerHTML = "";
    if (ticket.rules_triggered && ticket.rules_triggered.length > 0) {
        ticket.rules_triggered.forEach(r => {
            const li = document.createElement("li");
            li.className = "text-xs text-amber-300 bg-amber-950/40 p-2 rounded border border-amber-800/40 mb-1";
            li.innerHTML = `<strong>${r.rule_id}</strong> (${r.module}): ${r.consequent.action_required || 'Enforced policy constraint.'}`;
            rulesContainer.appendChild(li);
        });
    } else {
        rulesContainer.innerHTML = `<li class="text-xs text-slate-400 italic">Standard institutional workflow applied.</li>`;
    }

    // A* Plan
    const planContainer = document.getElementById("modal-plan-steps");
    planContainer.innerHTML = "";
    if (ticket.resolution_plan && ticket.resolution_plan.length > 0) {
        ticket.resolution_plan.forEach(step => {
            const div = document.createElement("div");
            div.className = "plan-timeline-step mb-3 text-xs";
            div.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px]">${step.step_number}</span>
                    <span class="font-semibold text-slate-200">${step.action}</span>
                    <span class="text-slate-400">(${step.actor})</span>
                    <span class="ml-auto text-indigo-400 font-mono">${step.cumulative_hours}h</span>
                </div>
                <div class="text-slate-400 ml-7 mt-0.5">${step.description}</div>
            `;
            planContainer.appendChild(div);
        });
    }

    document.getElementById("modal-ai-response").innerText = ticket.ai_generated_response;
}

function closeSuccessModal() {
    document.getElementById("submission-success-modal").classList.add("hidden");
    document.getElementById("complaint-form").reset();
    switchTab("track");
}


// --- Ticket Tracker & Management ---
function initFilters() {
    const searchInput = document.getElementById("tickets-search");
    const statusFilter = document.getElementById("filter-status");
    const categoryFilter = document.getElementById("filter-category");

    if (searchInput) {
        searchInput.addEventListener("input", () => renderTicketsTable());
    }
    if (statusFilter) {
        statusFilter.addEventListener("change", () => renderTicketsTable());
    }
    if (categoryFilter) {
        categoryFilter.addEventListener("change", () => renderTicketsTable());
    }
}

async function loadTickets() {
    try {
        const response = await fetch(`${API_BASE}/api/complaints`);
        allTickets = await response.json();
        renderTicketsTable();
        renderTrackCards();
        updateEmergencyBanner();
    } catch (err) {
        console.error("Failed to load tickets:", err);
    }
}

function renderTicketsTable() {
    const tbody = document.getElementById("admin-tickets-tbody");
    if (!tbody) return;

    const searchTerm = (document.getElementById("tickets-search")?.value || "").toLowerCase();
    const statusVal = document.getElementById("filter-status")?.value || "";
    const categoryVal = document.getElementById("filter-category")?.value || "";

    const filtered = allTickets.filter(t => {
        const matchSearch = !searchTerm ||
            t.ticket_code.toLowerCase().includes(searchTerm) ||
            t.subject.toLowerCase().includes(searchTerm) ||
            t.student_name.toLowerCase().includes(searchTerm);
        const matchStatus = !statusVal || t.status === statusVal;
        const matchCat = !categoryVal || t.category === categoryVal;
        return matchSearch && matchStatus && matchCat;
    });

    tbody.innerHTML = "";

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400">No tickets match the selected filters.</td></tr>`;
        return;
    }

    filtered.forEach(ticket => {
        const tr = document.createElement("tr");
        tr.className = "border-b border-slate-800 hover:bg-slate-800/40 transition-colors";

        const priClass = `badge-${ticket.priority.toLowerCase()}`;
        const clusterBadge = ticket.cluster_id ? `<span class="ml-1 text-[10px] px-1.5 py-0.5 rounded bg-purple-900/60 text-purple-300 border border-purple-700/50">🔗 ${ticket.cluster_id}</span>` : "";

        tr.innerHTML = `
            <td class="px-4 py-3 font-mono text-xs text-indigo-400 font-semibold">${ticket.ticket_code}</td>
            <td class="px-4 py-3">
                <div class="text-sm font-medium text-slate-200">${ticket.subject}</div>
                <div class="text-xs text-slate-400">${ticket.location || 'Campus Wide'}</div>
            </td>
            <td class="px-4 py-3 text-xs text-slate-300">
                ${ticket.category} ${clusterBadge}
            </td>
            <td class="px-4 py-3">
                <span class="px-2.5 py-1 rounded-full text-xs font-bold ${priClass}">${ticket.priority}</span>
            </td>
            <td class="px-4 py-3 text-xs">
                <div class="font-semibold text-slate-300">${(ticket.escalation_risk * 100).toFixed(0)}%</div>
                <div class="w-16 bg-slate-700 h-1.5 rounded-full overflow-hidden mt-1">
                    <div class="h-full ${ticket.escalation_risk > 0.7 ? 'bg-red-500' : (ticket.escalation_risk > 0.4 ? 'bg-amber-400' : 'bg-emerald-400')}" style="width: ${ticket.escalation_risk * 100}%"></div>
                </div>
            </td>
            <td class="px-4 py-3">
                <span class="text-xs px-2.5 py-1 rounded-full font-medium ${getStatusBadgeClass(ticket.status)}">${ticket.status}</span>
            </td>
            <td class="px-4 py-3 text-right">
                <button onclick="openTicketDetailModal('${ticket.ticket_code}')" class="px-3 py-1 bg-slate-700 hover:bg-indigo-600 text-xs rounded text-white transition-colors">
                    Inspect & Act
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function getStatusBadgeClass(status) {
    switch (status) {
        case "Submitted": return "bg-slate-700 text-slate-300";
        case "Triaged": return "bg-blue-900/60 text-blue-300 border border-blue-700/50";
        case "In Progress": return "bg-amber-900/60 text-amber-300 border border-amber-700/50";
        case "Escalated": return "bg-red-900/60 text-red-300 border border-red-700/50";
        case "Resolved": return "bg-emerald-900/60 text-emerald-300 border border-emerald-700/50";
        case "Closed": return "bg-slate-800 text-slate-400";
        default: return "bg-slate-700 text-slate-300";
    }
}

function renderTrackCards() {
    const container = document.getElementById("student-tickets-container");
    if (!container) return;

    container.innerHTML = "";
    if (allTickets.length === 0) {
        container.innerHTML = `<div class="col-span-3 text-center py-12 text-slate-400">No active tickets registered yet. Submit your first complaint above!</div>`;
        return;
    }

    allTickets.forEach(ticket => {
        const card = document.createElement("div");
        card.className = "glass-card rounded-xl p-5 border border-slate-700/60 flex flex-col justify-between";

        const planCount = ticket.resolution_plan ? ticket.resolution_plan.length : 0;

        card.innerHTML = `
            <div>
                <div class="flex items-center justify-between mb-3">
                    <span class="font-mono text-xs font-bold text-indigo-400">${ticket.ticket_code}</span>
                    <span class="px-2.5 py-0.5 rounded-full text-xs font-bold badge-${ticket.priority.toLowerCase()}">${ticket.priority}</span>
                </div>
                <h3 class="text-base font-semibold text-slate-100 mb-1 leading-snug">${ticket.subject}</h3>
                <p class="text-xs text-slate-400 line-clamp-2 mb-4">${ticket.description}</p>
                <div class="flex items-center justify-between text-xs text-slate-400 border-t border-slate-800/80 pt-3">
                    <span>🏷️ ${ticket.category}</span>
                    <span>⏱️ SLA: ${ticket.sla_hours}h</span>
                </div>
            </div>
            <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between">
                <span class="text-xs px-2.5 py-1 rounded-full font-medium ${getStatusBadgeClass(ticket.status)}">${ticket.status}</span>
                <button onclick="openTicketDetailModal('${ticket.ticket_code}')" class="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1">
                    View A* Workflow ➔
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}


// --- Ticket Detail & Action Modal ---
function openTicketDetailModal(ticketCode) {
    const ticket = allTickets.find(t => t.ticket_code === ticketCode);
    if (!ticket) return;

    selectedTicket = ticket;
    const modal = document.getElementById("ticket-detail-modal");
    modal.classList.remove("hidden");

    document.getElementById("detail-code").innerText = ticket.ticket_code;
    document.getElementById("detail-subject").innerText = ticket.subject;
    document.getElementById("detail-desc").innerText = ticket.description;
    document.getElementById("detail-student").innerText = ticket.student_name;
    document.getElementById("detail-category").innerText = ticket.category;
    document.getElementById("detail-priority").innerText = ticket.priority;
    document.getElementById("detail-priority").className = `px-3 py-1 rounded-full text-xs font-bold badge-${ticket.priority.toLowerCase()}`;
    const deptEl = document.getElementById("detail-department");
    if (deptEl) deptEl.innerText = ticket.assigned_department || "General Administration";
    document.getElementById("detail-location").innerText = ticket.location || "N/A";
    document.getElementById("detail-sla").innerText = `${ticket.sla_hours} Hours`;
    document.getElementById("detail-status-select").value = ticket.status;


    // AI Reasoning & Diagnostics
    document.getElementById("detail-bayes-risk").innerText = `${(ticket.escalation_risk * 100).toFixed(1)}%`;
    document.getElementById("detail-urgency-score").innerText = ticket.bayesian_urgency_score;
    
    // Cluster
    const clusterDiv = document.getElementById("detail-cluster-info");
    if (ticket.cluster_id) {
        clusterDiv.classList.remove("hidden");
        document.getElementById("detail-cluster-id").innerText = ticket.cluster_id;
    } else {
        clusterDiv.classList.add("hidden");
    }

    // Rules
    const rulesList = document.getElementById("detail-rules-list");
    rulesList.innerHTML = "";
    if (ticket.rules_triggered && ticket.rules_triggered.length > 0) {
        ticket.rules_triggered.forEach(r => {
            const li = document.createElement("li");
            li.className = "text-xs text-amber-300 mb-1";
            li.innerHTML = `• <strong>${r.rule_id}</strong>: ${r.consequent.action_required || 'Rule activated'}`;
            rulesList.appendChild(li);
        });
    } else {
        rulesList.innerHTML = `<li class="text-xs text-slate-400 italic">No emergency override rules triggered.</li>`;
    }

    // A* Plan
    const planSteps = document.getElementById("detail-plan-steps");
    planSteps.innerHTML = "";
    if (ticket.resolution_plan && ticket.resolution_plan.length > 0) {
        ticket.resolution_plan.forEach(step => {
            const stepDiv = document.createElement("div");
            stepDiv.className = "plan-timeline-step mb-3 text-xs";
            stepDiv.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px]">${step.step_number}</span>
                    <span class="font-semibold text-slate-200">${step.action}</span>
                    <span class="text-slate-400">(${step.actor})</span>
                    <span class="ml-auto text-indigo-400 font-mono">${step.cumulative_hours}h</span>
                </div>
                <div class="text-slate-400 ml-7 mt-0.5">${step.description}</div>
            `;
            planSteps.appendChild(stepDiv);
        });
    }

    // Feedback rating section
    const feedbackSection = document.getElementById("detail-feedback-section");
    if (ticket.status === "Resolved" || ticket.status === "Closed") {
        feedbackSection.classList.remove("hidden");
        document.getElementById("feedback-score-display").innerText = ticket.feedback_score ? `Rating: ${ticket.feedback_score} / 5 Stars` : "No rating given yet.";
    } else {
        feedbackSection.classList.add("hidden");
    }
}

function closeTicketDetailModal() {
    document.getElementById("ticket-detail-modal").classList.add("hidden");
    selectedTicket = null;
}

async function updateTicketStatus() {
    if (!selectedTicket) return;
    const newStatus = document.getElementById("detail-status-select").value;
    const notes = document.getElementById("detail-status-notes").value;
    const staff = document.getElementById("detail-staff-name").value || "Admin Supervisor";

    try {
        const response = await fetch(`${API_BASE}/api/complaints/${selectedTicket.ticket_code}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                status: newStatus,
                notes: notes,
                staff_name: staff
            })
        });

        if (!response.ok) throw new Error("Failed to update status");

        alert("Ticket status updated successfully!");
        closeTicketDetailModal();
        loadTickets();
        loadMetrics();
    } catch (err) {
        alert("Error updating status: " + err.message);
    }
}

async function submitRating(stars) {
    if (!selectedTicket) return;
    try {
        const response = await fetch(`${API_BASE}/api/complaints/${selectedTicket.ticket_code}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                satisfaction_score: stars,
                comments: "Submitted via student portal."
            })
        });
        const res = await response.json();
        alert(res.message);
        loadTickets();
        loadMetrics();
        closeTicketDetailModal();
    } catch (err) {
        alert("Error submitting feedback: " + err.message);
    }
}


// --- Analytics & Telemetry (Module X: Applications) ---
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/api/metrics`);
        const metrics = await response.json();

        document.getElementById("metric-total").innerText = metrics.total_tickets;
        document.getElementById("metric-open").innerText = metrics.open_tickets;
        document.getElementById("metric-resolved").innerText = metrics.resolved_tickets;
        document.getElementById("metric-escalated").innerText = metrics.escalated_tickets;
        document.getElementById("metric-sla").innerText = `${metrics.avg_resolution_sla_hours}h`;
        document.getElementById("metric-satisfaction").innerText = `${metrics.satisfaction_rating_avg} / 5.0`;
        document.getElementById("metric-clusters").innerText = metrics.incident_clusters_detected;

        renderCharts(metrics);
    } catch (err) {
        console.error("Failed to load metrics:", err);
    }
}

function renderCharts(metrics) {
    const catCanvas = document.getElementById("chart-categories");
    const priCanvas = document.getElementById("chart-priorities");
    if (!catCanvas || !priCanvas) return;

    if (categoryChart) categoryChart.destroy();
    if (priorityChart) priorityChart.destroy();

    // Category Doughnut Chart
    categoryChart = new Chart(catCanvas, {
        type: 'doughnut',
        data: {
            labels: Object.keys(metrics.categories_distribution),
            datasets: [{
                data: Object.values(metrics.categories_distribution),
                backgroundColor: [
                    '#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6',
                    '#8b5cf6', '#ef4444', '#14b8a6', '#f97316'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } }
            }
        }
    });

    // Priority Bar Chart
    priorityChart = new Chart(priCanvas, {
        type: 'bar',
        data: {
            labels: Object.keys(metrics.priorities_distribution),
            datasets: [{
                label: 'Tickets',
                data: Object.values(metrics.priorities_distribution),
                backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444'],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { ticks: { color: '#94a3b8', stepSize: 1 }, grid: { color: '#1e293b' } },
                x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}


// --- FAI Syllabus & Agent Inspector ---
async function loadFaiDiagnostics() {
    try {
        const response = await fetch(`${API_BASE}/api/fai-diagnostics`);
        const diag = await response.json();

        // Render PEAS
        const peas = diag.peas_model;
        const peasContainer = document.getElementById("inspector-peas-container");
        if (peasContainer) {
            peasContainer.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                        <div class="font-bold text-xs text-indigo-400 mb-1">🎯 Performance Measure</div>
                        <ul class="text-xs text-slate-300 space-y-1">
                            ${Object.entries(peas.performance_measures).map(([k, v]) => `<li>• <strong>${k}</strong>: ${v}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                        <div class="font-bold text-xs text-emerald-400 mb-1">🌍 Environment</div>
                        <p class="text-xs text-slate-300 mb-1 font-semibold">${peas.environment.type}</p>
                        <p class="text-xs text-slate-400">${peas.environment.entities.slice(0, 4).join(', ')}...</p>
                    </div>
                    <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                        <div class="font-bold text-xs text-amber-400 mb-1">🦾 Actuators</div>
                        <ul class="text-xs text-slate-300 space-y-1">
                            ${peas.actuators.map(a => `<li>• ${a}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                        <div class="font-bold text-xs text-cyan-400 mb-1">📡 Sensors</div>
                        <ul class="text-xs text-slate-300 space-y-1">
                            ${peas.sensors.map(s => `<li>• ${s}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        // Render Planning Operators
        const opsContainer = document.getElementById("inspector-operators-container");
        if (opsContainer) {
            opsContainer.innerHTML = diag.planning_operators.map(op => `
                <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-bold text-indigo-300">${op.name}</span>
                        <span class="text-slate-400 font-mono">Cost: ${op.cost_hours}h</span>
                    </div>
                    <div class="text-slate-400 mb-1">${op.description}</div>
                    <div class="text-[11px] text-slate-500">Actor: <span class="text-slate-300">${op.actor}</span></div>
                </div>
            `).join('');
        }

        // Render Rules
        const rulesContainer = document.getElementById("inspector-rules-container");
        if (rulesContainer) {
            rulesContainer.innerHTML = diag.inference_rule_base.map(r => `
                <div class="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs">
                    <div class="flex items-center justify-between mb-1">
                        <span class="font-bold text-amber-300">${r.rule_id}</span>
                        <span class="text-slate-500">${r.module}</span>
                    </div>
                    <div class="text-slate-300 mb-1"><strong>Action:</strong> ${r.consequent.action_required || 'Standard rule'}</div>
                    <div class="text-[11px] text-slate-400 italic">Ref: ${r.consequent.policy_reference || 'Campus Ordinance'}</div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Failed to load FAI diagnostics:", err);
    }
}


// --- Module IV: Constraint Satisfaction Problem (CSP) Trigger ---
async function triggerCspDispatch() {
    const btn = document.getElementById("run-csp-btn");
    if (btn) btn.disabled = true;

    const resEl = document.getElementById("inspector-csp-result");
    if (resEl) resEl.innerText = "Running Backtracking Search + MRV + Forward Checking...";

    try {
        const response = await fetch(`${API_BASE}/api/csp/dispatch`, { method: "POST" });
        const data = await response.json();

        const assignments = data.assignments || {};
        const tel = data.telemetry || {};

        let summaryText = `[CSP SOLVER - MODULE IV SUCCESS]\n`;
        summaryText += `Algorithm: ${tel.algorithm || 'Backtracking + MRV'}\n`;
        summaryText += `Total Constraints Evaluated: ${tel.constraint_checks || 0}\n`;
        summaryText += `Backtracks: ${tel.backtracks || 0}\n`;
        summaryText += `Allocations Assigned: ${Object.keys(assignments).length}\n\n`;

        for (const [code, alloc] of Object.entries(assignments)) {
            summaryText += `• ${code} (${alloc.category}, ${alloc.priority}) ➔ ${alloc.assigned_staff_name}\n`;
        }

        if (resEl) resEl.innerText = summaryText;

        alert(`CSP Dispatch Completed Successfully!\n${Object.keys(assignments).length} tickets assigned to qualified campus specialists without violating capacity constraints.`);

        loadTickets();
        loadMetrics();
    } catch (err) {
        if (resEl) resEl.innerText = "Error solving CSP: " + err.message;
        alert("Error executing CSP: " + err.message);
    } finally {
        if (btn) btn.disabled = false;
    }
}


// --- Module II vs Module III: Search Algorithm Benchmark ---
async function runSearchComparison() {
    const resEl = document.getElementById("inspector-search-compare-result");
    if (resEl) resEl.innerText = "Benchmarking A* (Informed) vs Uniform Cost Search (Uninformed)...";

    try {
        const response = await fetch(`${API_BASE}/api/planning/compare-search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                category: "Hostel",
                priority: "Emergency",
                requires_parts: true,
                requires_dean_alert: true
            })
        });
        const data = await response.json();

        const astar = data.astar_informed_search.telemetry;
        const ucs = data.uniform_cost_search_uninformed.telemetry;
        const comp = data.academic_comparison;

        let output = `[SEARCH COMPARISON BENCHMARK - MODULE II vs III]\n\n`;
        output += `1. A* SEARCH (Informed, f = g + h):\n`;
        output += `   • Nodes Expanded: ${astar.nodes_expanded}\n`;
        output += `   • Nodes Generated: ${astar.nodes_generated}\n`;
        output += `   • Optimal Path Duration: ${astar.path_cost_hours} hrs (${astar.total_steps} steps)\n\n`;

        output += `2. UNIFORM COST SEARCH (Uninformed, f = g, h = 0):\n`;
        output += `   • Nodes Expanded: ${ucs.nodes_expanded}\n`;
        output += `   • Nodes Generated: ${ucs.nodes_generated}\n`;
        output += `   • Optimal Path Duration: ${ucs.path_cost_hours} hrs (${ucs.total_steps} steps)\n\n`;

        output += `ACADEMIC CONCLUSION:\n`;
        output += `• ${comp.nodes_expanded_difference}\n`;
        output += `• ${comp.search_pruning_efficiency}\n`;
        output += `• Both algorithms guarantee optimal cost, but A* achieves it with significantly fewer node expansions due to admissible heuristic h(n).`;

        if (resEl) resEl.innerText = output;
    } catch (err) {
        if (resEl) resEl.innerText = "Error running search benchmark: " + err.message;
    }
}


// --- Emergency Reporting & Alert System ---
function initEmergencyFeatures() {
    const sosForm = document.getElementById("emergency-sos-form");
    if (sosForm) {
        sosForm.addEventListener("submit", submitEmergencySOS);
    }
}

function openEmergencyModal() {
    const modal = document.getElementById("modal-emergency");
    if (modal) {
        modal.classList.remove("hidden");
    }
}

function closeEmergencyModal() {
    const modal = document.getElementById("modal-emergency");
    if (modal) {
        modal.classList.add("hidden");
    }
}

function updateEmergencyBanner() {
    const banner = document.getElementById("global-emergency-banner");
    const bannerText = document.getElementById("emergency-banner-text");
    if (!banner || !bannerText) return;

    const activeEmergencies = allTickets.filter(
        t => (t.priority === "Emergency" || t.category === "Anti-Ragging & Safety") &&
             t.status !== "Resolved" && t.status !== "Closed"
    );

    if (activeEmergencies.length > 0) {
        banner.classList.remove("hidden");
        const latest = activeEmergencies[0];
        bannerText.innerHTML = `<span class="font-mono font-bold text-white">${latest.ticket_code}</span>: ${latest.subject} (${latest.location || 'Campus Wide'}) &bull; Escalated to Proctorial Board & Dean`;
        banner.setAttribute("data-emergency-ticket", latest.ticket_code);
    } else {
        banner.classList.add("hidden");
    }
}

function viewActiveEmergencyTicket() {
    const banner = document.getElementById("global-emergency-banner");
    const ticketCode = banner?.getAttribute("data-emergency-ticket");
    if (ticketCode) {
        openTicketDetail(ticketCode);
    } else {
        switchTab("admin");
    }
}

async function submitEmergencySOS(e) {
    e.preventDefault();
    const btn = document.getElementById("sos-submit-btn");
    btn.disabled = true;
    btn.innerHTML = `<span>🚨 Transmitting Emergency to Proctorial Board...</span>`;

    const category = document.getElementById("sos-category").value;
    const location = document.getElementById("sos-location").value;
    const subject = document.getElementById("sos-subject").value;
    const desc = document.getElementById("sos-description").value;
    const isAnon = document.getElementById("sos-anonymous").checked;

    const payload = {
        student_name: isAnon ? "Anonymous Student" : "Emergency Reporter",
        student_id: isAnon ? "N/A" : "EMERGENCY",
        email: "",
        phone: "",
        is_anonymous: isAnon,
        subject: `[EMERGENCY SOS] ${subject}`,
        description: `URGENT CAMPUS EMERGENCY DISPATCH: ${desc}`,
        location: location,
        category: category
    };

    try {
        const response = await fetch(`${API_BASE}/api/complaints`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error("Emergency dispatch failed");
        const ticket = await response.json();

        closeEmergencyModal();
        alert(`🚨 EMERGENCY REPORTED & TRANSMITTED!\n\nTicket Code: ${ticket.ticket_code}\nPriority: ${ticket.priority}\nAssigned: ${ticket.assigned_department}\nSLA: ${ticket.sla_hours} Hours\n\nDean of Student Welfare & Proctorial Board have been alerted via forward-chaining rules.`);

        await loadTickets();
        await loadMetrics();
        openTicketDetail(ticket.ticket_code);
    } catch (err) {
        alert("Failed to report emergency: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>⚡ TRANSMIT EMERGENCY DISPATCH</span>`;
    }
}


