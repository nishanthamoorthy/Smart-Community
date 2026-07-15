// ============================================================
// Smart Community Resource & Volunteer Allocation System
// Shared JavaScript Utilities - main.js
// ============================================================

const API = {
  BASE: '',  // Same origin; Flask serves both API and pages

  // Generic fetch wrapper with error handling
  async request(endpoint, method = 'GET', body = null) {
    try {
      const opts = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };
      if (body) opts.body = JSON.stringify(body);
      const res = await fetch(API.BASE + endpoint, opts);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Request failed');
      return { data, ok: true };
    } catch (err) {
      return { error: err.message, ok: false };
    }
  },

  getIssues: (filters = {}) => {
    const params = new URLSearchParams(filters).toString();
    return API.request(`/api/get_issues${params ? '?' + params : ''}`);
  },
  addIssue: (data) => API.request('/api/add_issue', 'POST', data),
  getStats: () => API.request('/api/stats'),
  getVolunteers: () => API.request('/api/get_volunteers'),
  registerVolunteer: (data) => API.request('/api/register_volunteer', 'POST', data),
  loginVolunteer: (data) => API.request('/api/login_volunteer', 'POST', data),
  logout: () => API.request('/api/logout', 'POST'),
  assignVolunteer: (data) => API.request('/api/assign_volunteer', 'POST', data),
  matchVolunteers: (issueId) => API.request(`/api/match_volunteers/${issueId}`),
  myTasks: (volunteerId) => API.request(`/api/my_tasks?volunteer_id=${volunteerId}`),
  updateIssue: (id, data) => API.request(`/api/update_issue/${id}`, 'PATCH', data),
};


// ============================================================
// Toast Notifications
// ============================================================
let toastTimer = null;

function showToast(message, type = 'success') {
  // Remove existing toast
  const existing = document.getElementById('toast');
  if (existing) existing.remove();
  if (toastTimer) clearTimeout(toastTimer);

  const icons = { success: '✓', error: '✕', warn: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.id = 'toast';
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9000;
    display: flex; align-items: center; gap: 10px;
    background: var(--bg-2); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 18px;
    font-family: var(--font-body); font-size: 0.875rem; color: var(--text);
    box-shadow: var(--shadow-lg); min-width: 260px; max-width: 380px;
    animation: slideIn 0.3s ease forwards;
    border-left: 3px solid ${
      type === 'success' ? 'var(--success)' :
      type === 'error' ? 'var(--danger)' :
      type === 'warn' ? 'var(--warn)' : 'var(--accent-2)'
    };
  `;
  toast.innerHTML = `
    <span style="font-size:1.1rem">${icons[type] || '•'}</span>
    <span>${message}</span>
  `;

  const style = document.createElement('style');
  style.textContent = `@keyframes slideIn { from { transform: translateX(120%); opacity:0; } to { transform:translateX(0); opacity:1; } }`;
  document.head.appendChild(style);

  document.body.appendChild(toast);
  toastTimer = setTimeout(() => {
    toast.style.animation = 'slideIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}


// ============================================================
// Format Helpers
// ============================================================
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function severityBadge(severity) {
  const map = { high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
  return `<span class="badge ${map[severity] || 'badge-low'}">${severity}</span>`;
}

function priorityBadge(priority) {
  if (priority === 'high') return `<span class="badge badge-urgent">🚨 HIGH</span>`;
  return `<span class="badge badge-normal">Normal</span>`;
}

function statusBadge(status) {
  const map = {
    open: { cls: 'badge-high', label: 'Open' },
    in_progress: { cls: 'badge-medium', label: 'In Progress' },
    resolved: { cls: 'badge-normal', label: 'Resolved' }
  };
  const s = map[status] || map.open;
  return `<span class="badge ${s.cls}">${s.label}</span>`;
}

function categoryIcon(cat) {
  const icons = {
    medical: '🏥', disaster: '', education: '',
    water: '💧', infrastructure: '🏗️', general: ''
  };
  return icons[cat] || '';
}

function skillIcon(skill) {
  const icons = {
    doctor: '👨‍⚕️', driver: '🚗', teacher: '👩‍🏫',
    engineer: '🔧', nurse: '💉', counselor: '🧠', general: '🙋'
  };
  return icons[skill] || '🙋';
}


// ============================================================
// Active nav link highlighting
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (path === '/' && href === '/') || (path !== '/' && href !== '/' && path.includes(href))) {
      link.classList.add('active');
    }
  });
});
