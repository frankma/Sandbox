(function () {
    const SIZE = Number(document.getElementById('grid').dataset.size);
    const gridEl = document.getElementById('grid');
    const statusEl = document.getElementById('status');
    const newBtn = document.getElementById('new-btn');
    const solveBtn = document.getElementById('solve-btn');
    const hintBtn = document.getElementById('hint-btn');
    const resetBtn = document.getElementById('reset-btn');
    const difficultySel = document.getElementById('difficulty');
    const speedSlider = document.getElementById('speed');

    let givenGrid = emptyGrid();
    let currentGrid = emptyGrid();
    let inputs = [];
    let busy = false;

    function emptyGrid() {
        return Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
    }

    const tooltip = document.createElement('div');
    tooltip.className = 'candidate-tooltip';
    for (let d = 1; d <= SIZE; d++) {
        const span = document.createElement('span');
        span.className = 'digit';
        span.textContent = String(d);
        span.dataset.digit = String(d);
        tooltip.appendChild(span);
    }
    document.body.appendChild(tooltip);

    function computeCandidates(grid, r, c) {
        if (grid[r][c]) return [];
        const used = new Set();
        for (let i = 0; i < SIZE; i++) {
            if (grid[r][i]) used.add(grid[r][i]);
            if (grid[i][c]) used.add(grid[i][c]);
        }
        const br = Math.floor(r / 3) * 3, bc = Math.floor(c / 3) * 3;
        for (let dr = 0; dr < 3; dr++) {
            for (let dc = 0; dc < 3; dc++) {
                const v = grid[br + dr][bc + dc];
                if (v) used.add(v);
            }
        }
        const candidates = [];
        for (let v = 1; v <= SIZE; v++) if (!used.has(v)) candidates.push(v);
        return candidates;
    }

    function showCandidates(r, c, cellEl) {
        if (busy || givenGrid[r][c] || currentGrid[r][c]) {
            hideCandidates();
            return;
        }
        const candidates = computeCandidates(currentGrid, r, c);
        tooltip.querySelectorAll('.digit').forEach(span => {
            const d = Number(span.dataset.digit);
            span.className = 'digit ' + (candidates.includes(d) ? 'active' : 'inactive');
        });
        const rect = cellEl.getBoundingClientRect();
        const spaceRight = window.innerWidth - rect.right;
        tooltip.classList.add('visible');
        const tw = tooltip.offsetWidth || 84;
        if (spaceRight > tw + 12) {
            tooltip.style.left = `${rect.right + 6}px`;
        } else {
            tooltip.style.left = `${rect.left - tw - 6}px`;
        }
        tooltip.style.top = `${Math.max(4, rect.top - 6)}px`;
    }

    function hideCandidates() {
        tooltip.classList.remove('visible');
    }

    function buildGrid() {
        gridEl.innerHTML = '';
        inputs = [];
        for (let r = 0; r < SIZE; r++) {
            const row = [];
            for (let c = 0; c < SIZE; c++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                if ((c + 1) % 3 === 0 && c !== SIZE - 1) cell.classList.add('block-right');
                if ((r + 1) % 3 === 0 && r !== SIZE - 1) cell.classList.add('block-bottom');

                const input = document.createElement('input');
                input.type = 'text';
                input.inputMode = 'numeric';
                input.maxLength = 1;
                input.dataset.row = r;
                input.dataset.col = c;
                input.addEventListener('input', onCellInput);
                input.addEventListener('keydown', onCellKeydown);

                cell.addEventListener('mouseenter', () => showCandidates(r, c, cell));
                cell.addEventListener('mouseleave', hideCandidates);

                cell.appendChild(input);
                gridEl.appendChild(cell);
                row.push({ cell, input });
            }
            inputs.push(row);
        }
    }

    function onCellKeydown(e) {
        const r = Number(e.target.dataset.row);
        const c = Number(e.target.dataset.col);
        const move = (dr, dc) => {
            const nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE) inputs[nr][nc].input.focus();
        };
        if (e.key === 'ArrowUp') move(-1, 0);
        else if (e.key === 'ArrowDown') move(1, 0);
        else if (e.key === 'ArrowLeft') move(0, -1);
        else if (e.key === 'ArrowRight') move(0, 1);
        else if (e.key === 'Backspace' || e.key === 'Delete') {
            currentGrid[r][c] = 0;
            e.target.value = '';
            refreshConflicts();
        }
    }

    function onCellInput(e) {
        const r = Number(e.target.dataset.row);
        const c = Number(e.target.dataset.col);
        const digit = e.target.value.replace(/[^1-9]/g, '').slice(-1);
        e.target.value = digit;
        currentGrid[r][c] = digit ? Number(digit) : 0;
        refreshConflicts();
    }

    function render() {
        for (let r = 0; r < SIZE; r++) {
            for (let c = 0; c < SIZE; c++) {
                const { cell, input } = inputs[r][c];
                const isGiven = givenGrid[r][c] !== 0;
                const value = currentGrid[r][c];
                input.value = value ? String(value) : '';
                input.readOnly = isGiven;
                input.tabIndex = isGiven ? -1 : 0;
                cell.classList.toggle('given', isGiven);
                cell.classList.remove('fill-single', 'fill-trial', 'fill-hint');
            }
        }
        refreshConflicts();
    }

    function refreshConflicts() {
        const conflicted = new Set();
        const groups = [];
        for (let r = 0; r < SIZE; r++) groups.push(cellsInRow(r));
        for (let c = 0; c < SIZE; c++) groups.push(cellsInCol(c));
        for (let br = 0; br < 3; br++) {
            for (let bc = 0; bc < 3; bc++) groups.push(cellsInBlock(br, bc));
        }
        for (const group of groups) {
            const seen = new Map();
            for (const [r, c] of group) {
                const v = currentGrid[r][c];
                if (!v) continue;
                if (seen.has(v)) {
                    conflicted.add(seen.get(v));
                    conflicted.add(`${r},${c}`);
                } else {
                    seen.set(v, `${r},${c}`);
                }
            }
        }
        for (let r = 0; r < SIZE; r++) {
            for (let c = 0; c < SIZE; c++) {
                inputs[r][c].cell.classList.toggle('conflict', conflicted.has(`${r},${c}`));
            }
        }
        return conflicted.size > 0;
    }

    function cellsInRow(r) { return Array.from({ length: SIZE }, (_, c) => [r, c]); }
    function cellsInCol(c) { return Array.from({ length: SIZE }, (_, r) => [r, c]); }
    function cellsInBlock(br, bc) {
        const out = [];
        for (let r = br * 3; r < br * 3 + 3; r++) {
            for (let c = bc * 3; c < bc * 3 + 3; c++) out.push([r, c]);
        }
        return out;
    }

    function setStatus(text) { statusEl.textContent = text; }

    function setBusy(value) {
        busy = value;
        [newBtn, solveBtn, hintBtn, resetBtn, difficultySel].forEach(el => { el.disabled = value; });
        if (value) hideCandidates();
    }

    async function postJSON(url, body) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'request failed');
        return data;
    }

    async function newPuzzle() {
        if (busy) return;
        setBusy(true);
        setStatus('Generating…');
        try {
            const data = await postJSON('/api/new', { difficulty: difficultySel.value });
            givenGrid = data.grid.map(row => row.slice());
            currentGrid = data.grid.map(row => row.slice());
            render();
            setStatus('New puzzle ready.');
        } catch (err) {
            setStatus(err.message);
        } finally {
            setBusy(false);
        }
    }

    async function solveStepByStep() {
        if (busy) return;
        if (refreshConflicts()) {
            setStatus('Fix the highlighted conflicts before solving.');
            return;
        }
        setBusy(true);
        setStatus('Thinking…');
        try {
            const data = await postJSON('/api/solve_steps', { grid: currentGrid });
            if (!data.solved) {
                setStatus('No solution found from the current entries.');
                setBusy(false);
                return;
            }
            await animateSteps(data.steps);
            setStatus('Solved!');
        } catch (err) {
            setStatus(err.message);
        } finally {
            setBusy(false);
        }
    }

    function animateSteps(steps) {
        const delay = Number(speedSlider.value);
        return new Promise(resolve => {
            let i = 0;
            function step() {
                if (i >= steps.length) { resolve(); return; }
                const { row, col, value, technique } = steps[i];
                currentGrid[row][col] = value;
                const { cell, input } = inputs[row][col];
                input.value = String(value);
                cell.classList.remove('fill-single', 'fill-trial', 'conflict');
                cell.classList.add(technique === 'trial' ? 'fill-trial' : 'fill-single');
                i += 1;
                setTimeout(step, delay);
            }
            step();
        });
    }

    async function hint() {
        if (busy) return;
        if (refreshConflicts()) {
            setStatus('Fix the highlighted conflicts before asking for a hint.');
            return;
        }
        setBusy(true);
        setStatus('Looking for a hint…');
        try {
            const data = await postJSON('/api/hint', { grid: currentGrid });
            if (!data.hint) {
                setStatus('No hint available — puzzle is solved or unsolvable.');
                return;
            }
            const { row, col, value, technique } = data.hint;
            currentGrid[row][col] = value;
            const { cell, input } = inputs[row][col];
            input.value = String(value);
            cell.classList.add('fill-hint');
            setStatus(technique === 'single'
                ? 'Hint: that cell only has one possible value left.'
                : 'Hint: took some deeper reasoning to find this one.');
        } catch (err) {
            setStatus(err.message);
        } finally {
            setBusy(false);
        }
    }

    function reset() {
        if (busy) return;
        currentGrid = givenGrid.map(row => row.slice());
        render();
        setStatus('Reset to the original givens.');
    }

    newBtn.addEventListener('click', newPuzzle);
    solveBtn.addEventListener('click', solveStepByStep);
    hintBtn.addEventListener('click', hint);
    resetBtn.addEventListener('click', reset);

    buildGrid();
    render();
    newPuzzle();
})();
