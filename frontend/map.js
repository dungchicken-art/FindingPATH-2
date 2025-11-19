const COLORS = {
  default: '#4b5563',
  start: '#2563eb',
  goal: '#dc2626',
  current: '#fcd34d',
  visited: '#f97316',
  frontier: '#38bdf8',
  path: '#34d399',
};

const EDGE_COLORS = {
  normal: '#9ca3af',
  flooded: '#3b82f6',
  blocked: '#ef4444',
};

const FALLBACK_GRAPH = {
  nodes: [
    { id: '1', x: 105.8126, y: 20.9925 },
    { id: '2', x: 105.8135, y: 20.9935 },
    { id: '3', x: 105.8145, y: 20.9944 },
    { id: '4', x: 105.8155, y: 20.995 },
    { id: '5', x: 105.8163, y: 20.9957 },
    { id: '6', x: 105.817, y: 20.9965 },
    { id: '7', x: 105.815, y: 20.9968 },
    { id: '8', x: 105.8138, y: 20.996 },
    { id: '9', x: 105.8129, y: 20.995 },
    { id: '10', x: 105.814, y: 20.994 },
  ],
  edges: [
    { u: '1', v: '2', flooded: false, blocked: false },
    { u: '2', v: '3', flooded: false, blocked: false },
    { u: '3', v: '4', flooded: false, blocked: false },
    { u: '4', v: '5', flooded: false, blocked: false },
    { u: '5', v: '6', flooded: true, blocked: false },
    { u: '4', v: '7', flooded: false, blocked: false },
    { u: '3', v: '8', flooded: false, blocked: false },
    { u: '8', v: '7', flooded: false, blocked: false },
    { u: '8', v: '9', flooded: false, blocked: true },
    { u: '9', v: '1', flooded: false, blocked: false },
    { u: '2', v: '10', flooded: false, blocked: false },
    { u: '10', v: '3', flooded: false, blocked: false },
    { u: '10', v: '9', flooded: false, blocked: false },
    { u: '2', v: '5', flooded: false, blocked: false },
    { u: '6', v: '7', flooded: false, blocked: false },
  ],
};

const state = {
  graph: null,
  nodesLayer: {},
  pathLine: null,
  animationTimer: null,
  startNode: null,
  goalNode: null,
  finalPathNodes: [],
};

const map = L.map('map').setView([20.996, 105.817], 16);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors',
}).addTo(map);

const statusMessage = document.getElementById('status-message');
const startLabel = document.getElementById('start-node');
const goalLabel = document.getElementById('goal-node');
const speedInput = document.getElementById('speed');
const speedValue = document.getElementById('speed-value');

speedInput.addEventListener('input', () => {
  speedValue.textContent = speedInput.value;
});

document.getElementById('clear-selection').addEventListener('click', () => {
  resetSelection();
  setStatus('Đã reset lựa chọn. Chọn lại Start và Goal.');
});

fetch('/graph')
  .then((res) => res.json())
  .then((data) => {
    state.graph = data;
    renderGraph();
    setStatus('Click lên node bất kỳ để đặt Start, click node khác để đặt Goal.');
  })
  .catch((err) => {
    console.error(err);
    state.graph = FALLBACK_GRAPH;
    renderGraph();
    setStatus('Không thể tải dữ liệu đồ thị từ backend. Đang dùng dữ liệu mẫu offline.');
  });

function renderGraph() {
  if (!state.graph) return;
  const nodesById = Object.fromEntries(state.graph.nodes.map((node) => [node.id, node]));

  state.graph.edges.forEach((edge) => {
    const source = nodesById[edge.u];
    const target = nodesById[edge.v];
    const coords = [
      [source.y, source.x],
      [target.y, target.x],
    ];
    const color = edge.blocked
      ? EDGE_COLORS.blocked
      : edge.flooded
      ? EDGE_COLORS.flooded
      : EDGE_COLORS.normal;
    L.polyline(coords, {
      color,
      weight: 5,
      opacity: 0.8,
    }).addTo(map);
  });

  state.graph.nodes.forEach((node) => {
    const marker = L.circleMarker([node.y, node.x], {
      radius: 8,
      weight: 2,
      color: '#0f172a',
      fillColor: COLORS.default,
      fillOpacity: 1,
    }).addTo(map);
    marker.bindTooltip(`Node ${node.id}`, { permanent: false });
    marker.on('click', () => handleNodeClick(node.id));
    state.nodesLayer[node.id] = marker;
  });
}

function handleNodeClick(nodeId) {
  if (!state.startNode) {
    state.startNode = nodeId;
  } else if (!state.goalNode && nodeId !== state.startNode) {
    state.goalNode = nodeId;
  } else if (state.startNode === nodeId) {
    state.startNode = null;
  } else if (state.goalNode === nodeId) {
    state.goalNode = null;
  } else {
    state.startNode = nodeId;
    state.goalNode = null;
  }
  updateSelectionLabels();
  refreshNodeStyles();
}

function updateSelectionLabels() {
  startLabel.textContent = state.startNode ?? 'chưa chọn';
  goalLabel.textContent = state.goalNode ?? 'chưa chọn';
}

function setStatus(message) {
  statusMessage.textContent = message;
}

function resetSelection() {
  state.startNode = null;
  state.goalNode = null;
  clearAnimation();
  state.finalPathNodes = [];
  updateSelectionLabels();
  refreshNodeStyles();
  removePathLine();
}

function refreshNodeStyles(step = null) {
  Object.entries(state.nodesLayer).forEach(([id, marker]) => {
    let fill = COLORS.default;
    if (state.finalPathNodes.includes(id)) {
      fill = COLORS.path;
    }
    if (step && step.visited.includes(id)) {
      fill = COLORS.visited;
    }
    if (step && step.frontier.includes(id)) {
      fill = COLORS.frontier;
    }
    if (step && step.current === id) {
      fill = COLORS.current;
    }
    if (id === state.startNode) {
      fill = COLORS.start;
    }
    if (id === state.goalNode) {
      fill = COLORS.goal;
    }
    marker.setStyle({ fillColor: fill });
  });
}

function clearAnimation() {
  if (state.animationTimer) {
    clearTimeout(state.animationTimer);
    state.animationTimer = null;
  }
}

function removePathLine() {
  if (state.pathLine) {
    map.removeLayer(state.pathLine);
    state.pathLine = null;
  }
}

function drawPath(path) {
  removePathLine();
  if (!path || path.length < 2 || !state.graph) {
    state.finalPathNodes = [];
    refreshNodeStyles();
    return;
  }
  const nodesById = Object.fromEntries(state.graph.nodes.map((node) => [node.id, node]));
  const coords = path.map((nodeId) => [nodesById[nodeId].y, nodesById[nodeId].x]);
  state.pathLine = L.polyline(coords, {
    color: COLORS.path,
    weight: 6,
  }).addTo(map);
  state.finalPathNodes = [...path];
  refreshNodeStyles();
}

function runAlgorithm(algo) {
  if (!state.startNode || !state.goalNode) {
    setStatus('Hãy chọn Start và Goal trước khi chạy thuật toán.');
    return;
  }
  clearAnimation();
  setStatus(`Đang chạy ${algo.toUpperCase()}...`);
  fetch(`/path/${algo}?start=${state.startNode}&goal=${state.goalNode}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        setStatus(data.error);
        return;
      }
      animateSteps(data.steps, data.path);
    })
    .catch(() => setStatus('Không thể gọi API. Đảm bảo backend đang chạy.'));
}

function animateSteps(steps, path) {
  if (!Array.isArray(steps) || steps.length === 0) {
    drawPath(path);
    if (!path || path.length === 0) {
      setStatus('Không tìm được đường đi.');
    } else {
      setStatus(`Đường đi hoàn tất: ${path.join(' → ')}`);
    }
    return;
  }
  let index = 0;
  const speed = Number(speedInput.value);

  const tick = () => {
    const step = steps[index];
    refreshNodeStyles(step);
    index += 1;
    if (index < steps.length) {
      state.animationTimer = setTimeout(tick, speed);
    } else {
      state.animationTimer = setTimeout(() => {
        drawPath(path);
        if (!path || path.length === 0) {
          setStatus('Không tìm được đường đi.');
        } else {
          setStatus(`Đường đi hoàn tất: ${path.join(' → ')}`);
        }
      }, speed);
    }
  };

  tick();
}

Array.from(document.querySelectorAll('button[data-algo]')).forEach((button) => {
  button.addEventListener('click', () => runAlgorithm(button.dataset.algo));
});
