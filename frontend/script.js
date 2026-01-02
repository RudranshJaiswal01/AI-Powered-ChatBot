// Minimalistic Chat UI logic for FastAPI backend
// Author: GitHub Copilot

const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const loading = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const docUrlInput = document.getElementById('doc-url');
const loadDocBtn = document.getElementById('load-doc');
const resetDbBtn = document.getElementById('reset-db');

let history = [];

// Utility: Scroll chat to bottom
function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Utility: Render a message
function renderMessage(message, from) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `flex mb-2 ${from === 'user' ? 'justify-end' : 'justify-start'}`;
  const bubble = document.createElement('div');
  bubble.className = `max-w-[75%] px-4 py-2 rounded-lg text-sm prose prose-invert break-words ${from === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-700 text-gray-100 rounded-bl-none'}`;
  // Render markdown to HTML using marked.js
  bubble.innerHTML = window.marked ? window.marked.parse(message) : message;
  msgDiv.appendChild(bubble);
  chatContainer.appendChild(msgDiv);
  scrollToBottom();
}

// Utility: Show/hide loading
function setLoading(isLoading) {
  loading.classList.toggle('hidden', !isLoading);
  sendBtn.disabled = isLoading;
  chatInput.disabled = isLoading;
  loadDocBtn.disabled = isLoading;
  resetDbBtn.disabled = isLoading;
  docUrlInput.disabled = isLoading;
}

// Utility: Show error
function showError(msg) {
  errorDiv.textContent = msg;
  errorDiv.classList.remove('hidden');
}
function clearError() {
  errorDiv.textContent = '';
  errorDiv.classList.add('hidden');
}

// Handle chat form submit
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  const message = chatInput.value.trim();
  if (!message) return;
  renderMessage(message, 'user');
  chatInput.value = '';
  setLoading(true);
  try {
    // Keep last 5 user-bot turns
    if (history.length > 9) history = history.slice(-9);
    history.push(message);
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history })
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();
    if (!data.answer) throw new Error('No answer from bot');
    renderMessage(data.answer, 'bot');
    history.push(data.answer);
  } catch (err) {
    showError(err.message || 'Network error');
  } finally {
    setLoading(false);
  }
});

// Handle Load Document
loadDocBtn.addEventListener('click', async () => {
  clearError();
  const url = docUrlInput.value.trim();
  if (!url) {
    showError('Please enter a Google Doc URL.');
    return;
  }
  setLoading(true);
  try {
    const res = await fetch('/ingest-and-store?doc_url=' + encodeURIComponent(url), {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || 'Failed to load document');
    }
    renderMessage('Document loaded successfully.', 'bot');
  } catch (err) {
    showError(err.message || 'Network error');
  } finally {
    setLoading(false);
  }
});

// Handle Reset DB
resetDbBtn.addEventListener('click', async () => {
  clearError();
  setLoading(true);
  try {
    const res = await fetch('/reset-db', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset database');
    renderMessage('Database reset. You can load a new document.', 'bot');
    history = [];
    chatContainer.innerHTML = '';
  } catch (err) {
    showError(err.message || 'Network error');
  } finally {
    setLoading(false);
  }
});

// Optional: Enter key on doc input triggers load
docUrlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') loadDocBtn.click();
});

// Initial focus
chatInput.focus();
