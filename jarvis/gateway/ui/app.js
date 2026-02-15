const log = document.getElementById('log');
const input = document.getElementById('msg');
const planOnly = document.getElementById('planOnly');
const send = document.getElementById('send');

const ws = new WebSocket('ws://127.0.0.1:8787/ws');

function append(text) {
  log.textContent += text + "\n\n";
  log.scrollTop = log.scrollHeight;
}

ws.onopen = () => append('Connected.');
ws.onmessage = (evt) => {
  const data = JSON.parse(evt.data);
  append(`[${data.status}] #${data.inbox_id} (${data.mode})\n${data.text || ''}${data.error ? '\nERROR: ' + data.error : ''}`);
};
ws.onerror = () => append('WebSocket error');

function sendMsg() {
  const text = input.value.trim();
  if (!text) return;
  const payload = {
    workspace: 'default',
    text,
    mode: planOnly.checked ? 'plan' : 'exec',
  };
  append('YOU: ' + text);
  ws.send(JSON.stringify(payload));
  input.value = '';
}

send.addEventListener('click', sendMsg);
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendMsg();
});
