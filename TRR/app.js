const vertexInput = document.querySelector('#vertices');
const edgeInput = document.querySelector('#edges');
const analyzeButton = document.querySelector('#analyze');
const resetButton = document.querySelector('#reset');
const errorBox = document.querySelector('#input-error');
const resultBox = document.querySelector('#result');
const detailsBox = document.querySelector('#details');
const trailBox = document.querySelector('#trail');
const graphSvg = document.querySelector('#graph');
const canvasEmpty = document.querySelector('#canvas-empty');

function parseGraph() {
  const vertices = vertexInput.value.trim().split(/\s+/).filter(Boolean);
  const lines = edgeInput.value.trim() ? edgeInput.value.trim().split(/\n+/) : [];
  const vertexSet = new Set(vertices);
  if (!vertices.length) throw new Error('Bạn cần nhập ít nhất một đỉnh.');
  if (vertices.length !== vertexSet.size) throw new Error('Tên các đỉnh không được trùng nhau.');
  const edges = lines.map((line, index) => {
    const parts = line.trim().split(/\s+/);
    if (parts.length !== 2 || !vertexSet.has(parts[0]) || !vertexSet.has(parts[1])) {
      throw new Error(`Cạnh ở dòng ${index + 1} phải gồm 2 đỉnh đã khai báo.`);
    }
    return { start: parts[0], end: parts[1] };
  });
  return { vertices, edges };
}

function analyzeGraph(vertices, edges) {
  const adjacency = new Map(vertices.map(vertex => [vertex, []]));
  edges.forEach((edge, id) => {
    adjacency.get(edge.start).push({ vertex: edge.end, id });
    adjacency.get(edge.end).push({ vertex: edge.start, id });
  });
  const degrees = Object.fromEntries(vertices.map(vertex => [vertex, adjacency.get(vertex).length]));
  const odd = vertices.filter(vertex => degrees[vertex] % 2 === 1);
  const active = vertices.filter(vertex => degrees[vertex] > 0);
  const visited = new Set();
  if (active.length) {
    const queue = [active[0]];
    while (queue.length) {
      const current = queue.shift();
      if (visited.has(current)) continue;
      visited.add(current);
      adjacency.get(current).forEach(item => { if (!visited.has(item.vertex)) queue.push(item.vertex); });
    }
  }
  const connected = active.every(vertex => visited.has(vertex));
  let kind = 'none';
  let reason = 'Đồ thị phải có ít nhất một cạnh.';
  if (edges.length && connected && odd.length === 0) { kind = 'circuit'; reason = 'Có 0 đỉnh bậc lẻ và các đỉnh có cạnh liên thông.'; }
  else if (edges.length && connected && odd.length === 2) { kind = 'path'; reason = 'Có đúng 2 đỉnh bậc lẻ và các đỉnh có cạnh liên thông.'; }
  else if (edges.length && !connected) reason = 'Các đỉnh có cạnh không nằm trong cùng một thành phần liên thông.';
  else if (edges.length) reason = `Có ${odd.length} đỉnh bậc lẻ; cần 0 hoặc 2 đỉnh.`;

  let trail = null;
  if (kind !== 'none') {
    const used = new Set();
    const start = kind === 'path' ? odd[0] : active[0];
    const stack = [start];
    const reversed = [];
    while (stack.length) {
      const current = stack[stack.length - 1];
      const next = adjacency.get(current).find(item => !used.has(item.id));
      if (next) { used.add(next.id); stack.push(next.vertex); }
      else reversed.push(stack.pop());
    }
    trail = reversed.reverse();
  }
  return { degrees, odd, connected, kind, reason, trail };
}

function renderResult(graph, result) {
  const titles = { circuit: 'Đây là đồ thị Euler', path: 'Đây là đường đi Euler', none: 'Chưa đủ điều kiện Euler' };
  const descriptions = { circuit: 'Tồn tại một chu trình đi qua mỗi cạnh đúng một lần.', path: 'Tồn tại một đường đi đi qua mỗi cạnh đúng một lần.', none: 'Không tồn tại chu trình hoặc đường đi Euler.' };
  resultBox.className = `result-banner ${result.kind}`;
  resultBox.innerHTML = `<strong>${titles[result.kind]}</strong><span>${descriptions[result.kind]}</span>`;
  detailsBox.classList.remove('hidden');
  detailsBox.innerHTML = `<div class="detail-row"><span>Số đỉnh</span><strong>${graph.vertices.length}</strong></div><div class="detail-row"><span>Số cạnh</span><strong>${graph.edges.length}</strong></div><div class="detail-row"><span>Đỉnh bậc lẻ</span><strong>${result.odd.length ? result.odd.join(', ') : 'Không có'}</strong></div><div class="detail-row"><span>Liên thông</span><strong>${result.connected ? 'Có' : 'Không'}</strong></div>`;
  if (result.trail) { trailBox.classList.remove('hidden'); trailBox.textContent = `Lộ trình: ${result.trail.join(' → ')}`; }
  else { trailBox.classList.add('hidden'); }
  drawGraph(graph, result.trail);
}

function drawGraph(graph, trail) {
  graphSvg.innerHTML = '';
  canvasEmpty.classList.add('hidden');
  const width = 720, height = 460, centerX = width / 2, centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 65;
  const positions = new Map();
  graph.vertices.forEach((vertex, index) => {
    const angle = index * 2 * Math.PI / graph.vertices.length - Math.PI / 2;
    positions.set(vertex, { x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle) });
  });
  const highlighted = new Set();
  if (trail) for (let index = 0; index < trail.length - 1; index += 1) highlighted.add([trail[index], trail[index + 1]].sort().join('|'));
  const svg = (tag, attrs) => { const element = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value)); graphSvg.appendChild(element); return element; };
  graph.edges.forEach(edge => {
    const from = positions.get(edge.start), to = positions.get(edge.end), key = [edge.start, edge.end].sort().join('|');
    if (edge.start === edge.end) svg('circle', { cx: from.x, cy: from.y - 22, r: 28, fill: 'none', stroke: '#e76f51', 'stroke-width': 4 });
    else svg('line', { x1: from.x, y1: from.y, x2: to.x, y2: to.y, stroke: highlighted.has(key) ? '#e76f51' : '#829497', 'stroke-width': highlighted.has(key) ? 5 : 2.5, 'stroke-linecap': 'round' });
  });
  graph.vertices.forEach(vertex => { const point = positions.get(vertex); svg('circle', { cx: point.x, cy: point.y, r: 27, fill: '#d8f0eb', stroke: '#087f78', 'stroke-width': 2 }); const text = svg('text', { x: point.x, y: point.y + 6, 'text-anchor': 'middle', fill: '#18222d', 'font-size': 15, 'font-family': 'DM Mono, monospace', 'font-weight': '500' }); text.textContent = vertex; });
}

function runAnalysis() {
  try { const graph = parseGraph(); const result = analyzeGraph(graph.vertices, graph.edges); errorBox.textContent = ''; renderResult(graph, result); }
  catch (error) { errorBox.textContent = error.message; }
}

analyzeButton.addEventListener('click', runAnalysis);
resetButton.addEventListener('click', () => { vertexInput.value = 'A B C'; edgeInput.value = 'A B\nB C\nC A'; runAnalysis(); });
runAnalysis();