const vertexInput = document.querySelector('#vertices');
const edgeInput = document.querySelector('#edges');
const analyzeButton = document.querySelector('#analyze');
const resetButton = document.querySelector('#reset');
const graphTypeInput = document.querySelector('#graph-type');
const resultEyebrow = document.querySelector('#result-eyebrow');
const legendText = document.querySelector('#legend-text');
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

function findEulerTrailHierholzer(adjacency, vertices, edges, kind, odd, active) {
  if (kind === 'none') return { trail: null, trailEdges: null };
  const used = new Set();
  const start = kind === 'path' ? odd[0] : active[0];
  const stack = [{ vertex: start, edgeId: null }];
  const reversed = [];
  const reversedEdges = [];
  while (stack.length) {
    const current = stack[stack.length - 1].vertex;
    const next = adjacency.get(current).find(item => !used.has(item.id));
    if (next) { used.add(next.id); stack.push({ vertex: next.vertex, edgeId: next.id }); }
    else {
      const item = stack.pop();
      reversed.push(item.vertex);
      if (item.edgeId !== null) reversedEdges.push(item.edgeId);
    }
  }
  const trail = reversed.reverse();
  const trailEdges = reversedEdges.reverse();
  if (used.size !== edges.length || trail.length !== edges.length + 1) return { trail: null, trailEdges: null };
  return { trail, trailEdges };
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

  const { trail, trailEdges } = findEulerTrailHierholzer(adjacency, vertices, edges, kind, odd, active);
  return { degrees, odd, connected, kind, reason, trail, trailEdges, algorithm: 'Hierholzer' };
}

function analyzeHamilton(vertices, edges) {
  const adjacency = new Map(vertices.map(vertex => [vertex, new Set()]));
  edges.forEach((edge, id) => {
    if (edge.start !== edge.end) {
      adjacency.get(edge.start).add(edge.end);
      adjacency.get(edge.end).add(edge.start);
    }
  });
  const path = [];
  const visited = new Set();
  let solution = null;
  const search = current => {
    if (solution) return;
    path.push(current);
    visited.add(current);
    if (path.length === vertices.length) {
      solution = [...path];
    } else {
      for (const next of adjacency.get(current)) {
        if (!visited.has(next)) search(next);
      }
    }
    visited.delete(current);
    path.pop();
  };
  vertices.some(vertex => { search(vertex); return Boolean(solution); });
  if (!solution) return { kind: 'none', path: null, connected: false, degrees: {}, odd: [], reason: 'Không tìm được đường đi qua tất cả các đỉnh đúng một lần.' };
  const isCircuit = solution.length > 2 && adjacency.get(solution[solution.length - 1]).has(solution[0]);
  const route = isCircuit ? [...solution, solution[0]] : solution;
  const degrees = Object.fromEntries(vertices.map(vertex => [vertex, adjacency.get(vertex).size]));
  return { kind: isCircuit ? 'circuit' : 'path', path: route, connected: true, degrees, odd: [], reason: isCircuit ? 'Đỉnh cuối nối với đỉnh đầu, tạo thành chu trình Hamilton.' : 'Đã tìm được đường đi qua mỗi đỉnh đúng một lần.' };
}

function routeEdgeIds(edges, route) {
  if (!route) return null;
  const used = new Set();
  return route.slice(0, -1).map((start, index) => {
    const end = route[index + 1];
    const edgeId = edges.findIndex((edge, id) => !used.has(id) && ((edge.start === start && edge.end === end) || (edge.start === end && edge.end === start)));
    if (edgeId === -1) return null;
    used.add(edgeId);
    return edgeId;
  }).filter(edgeId => edgeId !== null);
}

function renderAutomaticResult(graph, euler, hamilton) {
  resultEyebrow.textContent = 'TỰ ĐỘNG PHÂN LOẠI';
  legendText.innerHTML = '<span class="legend-line"></span> Lộ trình được tìm thấy';
  const eulerText = euler.kind === 'circuit' ? 'Chu trình Euler' : euler.kind === 'path' ? 'Đường đi Euler' : 'Không phải Euler';
  const hamiltonText = hamilton.kind === 'circuit' ? 'Chu trình Hamilton' : hamilton.kind === 'path' ? 'Đường đi Hamilton' : 'Không phải Hamilton';
  const hasResult = euler.kind !== 'none' || hamilton.kind !== 'none';
  resultBox.className = `result-banner ${hasResult ? 'circuit' : 'none'}`;
  resultBox.innerHTML = `<strong>${hasResult ? 'Đã phân loại đồ thị' : 'Không thuộc loại Euler hoặc Hamilton'}</strong><span>${eulerText} · ${hamiltonText}</span>`;
  const degreeText = graph.vertices.map(vertex => `${vertex} = ${euler.degrees[vertex] ?? hamilton.degrees[vertex] ?? 'không có'}`).join(', ');
  detailsBox.classList.remove('hidden');
  detailsBox.innerHTML = `<div class="detail-row"><span>Số đỉnh</span><strong>${graph.vertices.length}</strong></div><div class="detail-row"><span>Số cạnh</span><strong>${graph.edges.length}</strong></div><div class="detail-row"><span>Bậc từng đỉnh</span><strong>${degreeText}</strong></div><div class="detail-row"><span>Thuật toán Euler</span><strong>${euler.algorithm}</strong></div><div class="detail-row"><span>Kết luận Euler</span><strong>${eulerText}</strong></div><div class="detail-row"><span>Kết luận Hamilton</span><strong>${hamiltonText}</strong></div>`;
  const eulerRoute = euler.trail ? `Euler: ${euler.trail.join(' → ')}` : '';
  const hamiltonRoute = hamilton.path ? `Hamilton: ${hamilton.path.join(' → ')}` : '';
  const routes = [eulerRoute, hamiltonRoute].filter(Boolean);
  if (routes.length) { trailBox.classList.remove('hidden'); trailBox.textContent = `Lộ trình: ${routes.join(' | ')}`; }
  else { trailBox.classList.add('hidden'); trailBox.textContent = ''; }
  drawGraph(graph, euler.kind !== 'none' ? euler.trailEdges : routeEdgeIds(graph.edges, hamilton.path));
}

function renderResult(graph, result) {
  const isHamilton = graphTypeInput.value === 'hamilton';
  resultEyebrow.textContent = isHamilton ? 'ĐỊNH LÝ HAMILTON' : 'ĐỊNH LÝ EULER';
  legendText.innerHTML = `<span class="legend-line"></span> ${isHamilton ? 'Lộ trình Hamilton' : 'Lộ trình Euler'}`;
  const titles = isHamilton ? { circuit: 'Đây là đồ thị Hamilton', path: 'Đây là đường đi Hamilton', none: 'Không phải đồ thị Hamilton' } : { circuit: 'Đây là đồ thị Euler', path: 'Đây là đường đi Euler', none: 'Chưa đủ điều kiện Euler' };
  const descriptions = isHamilton ? { circuit: 'Có chu trình đi qua mỗi đỉnh đúng một lần.', path: 'Có đường đi đi qua mỗi đỉnh đúng một lần.', none: 'Không tồn tại đường đi Hamilton.' } : { circuit: 'Tồn tại một chu trình đi qua mỗi cạnh đúng một lần.', path: 'Tồn tại một đường đi đi qua mỗi cạnh đúng một lần.', none: 'Không tồn tại chu trình hoặc đường đi Euler.' };
  resultBox.className = `result-banner ${result.kind}`;
  resultBox.innerHTML = `<strong>${titles[result.kind]}</strong><span>${descriptions[result.kind]}</span>`;
  detailsBox.classList.remove('hidden');
  const degreeText = graph.vertices.map(vertex => `${vertex} = ${result.degrees[vertex] ?? 'không có'}`).join(', ');
  detailsBox.innerHTML = `<div class="detail-row"><span>Số đỉnh</span><strong>${graph.vertices.length}</strong></div><div class="detail-row"><span>Số cạnh</span><strong>${graph.edges.length}</strong></div><div class="detail-row"><span>Bậc từng đỉnh</span><strong>${degreeText}</strong></div><div class="detail-row"><span>Thuật toán</span><strong>${isHamilton ? 'Quay lui' : 'Hierholzer'}</strong></div><div class="detail-row"><span>Liên thông</span><strong>${result.connected ? 'Có' : 'Không xác định'}</strong></div><div class="detail-row"><span>Lý do</span><strong>${result.reason}</strong></div>`;
  const route = isHamilton ? result.path : result.trail;
  if (route) { trailBox.classList.remove('hidden'); trailBox.textContent = `Lộ trình ${isHamilton ? 'Hamilton' : 'Hierholzer'}: ${route.join(' → ')}`; }
  else { trailBox.classList.add('hidden'); }
  drawGraph(graph, isHamilton ? routeEdgeIds(graph.edges, route) : result.trailEdges);
}

function drawGraph(graph, trailEdges) {
  graphSvg.innerHTML = '';
  canvasEmpty.classList.add('hidden');
  const width = 720, height = 460, centerX = width / 2, centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 65;
  const positions = new Map();
  graph.vertices.forEach((vertex, index) => {
    const angle = index * 2 * Math.PI / graph.vertices.length - Math.PI / 2;
    positions.set(vertex, { x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle) });
  });
  const highlighted = new Set(trailEdges || []);
  const svg = (tag, attrs) => { const element = document.createElementNS('http://www.w3.org/2000/svg', tag); Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value)); graphSvg.appendChild(element); return element; };
  graph.edges.forEach((edge, edgeId) => {
    const from = positions.get(edge.start), to = positions.get(edge.end), isHighlighted = highlighted.has(edgeId);
    if (edge.start === edge.end) svg('circle', { cx: from.x, cy: from.y - 22, r: 28, fill: 'none', stroke: isHighlighted ? '#e76f51' : '#829497', 'stroke-width': isHighlighted ? 5 : 2.5 });
    else svg('line', { x1: from.x, y1: from.y, x2: to.x, y2: to.y, stroke: isHighlighted ? '#e76f51' : '#829497', 'stroke-width': isHighlighted ? 5 : 2.5, 'stroke-linecap': 'round' });
  });
  graph.vertices.forEach(vertex => { const point = positions.get(vertex); svg('circle', { cx: point.x, cy: point.y, r: 27, fill: '#d8f0eb', stroke: '#087f78', 'stroke-width': 2 }); const text = svg('text', { x: point.x, y: point.y + 6, 'text-anchor': 'middle', fill: '#18222d', 'font-size': 15, 'font-family': 'DM Mono, monospace', 'font-weight': '500' }); text.textContent = vertex; });
}

function runAnalysis() {
  try {
    const graph = parseGraph();
    if (graphTypeInput.value === 'auto') {
      renderAutomaticResult(graph, analyzeGraph(graph.vertices, graph.edges), analyzeHamilton(graph.vertices, graph.edges));
    } else {
      const result = graphTypeInput.value === 'hamilton' ? analyzeHamilton(graph.vertices, graph.edges) : analyzeGraph(graph.vertices, graph.edges);
      renderResult(graph, result);
    }
    errorBox.textContent = '';
  }
  catch (error) { errorBox.textContent = error.message; }
}

analyzeButton.addEventListener('click', runAnalysis);
graphTypeInput.addEventListener('change', runAnalysis);
resetButton.addEventListener('click', () => { vertexInput.value = 'A B C'; edgeInput.value = 'A B\nB C\nC A'; runAnalysis(); });
runAnalysis();