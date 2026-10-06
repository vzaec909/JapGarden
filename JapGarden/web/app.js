// ============================================================
// СОСТОЯНИЕ
// ============================================================
const state = {
    presets: [],
    selectedPreset: null,
};

const API = "";  // тот же origin: http://localhost:8000

// ============================================================
// УТИЛИТЫ
// ============================================================
function $(id) {
    return document.getElementById(id);
}

function showError(msg) {
    const el = $("error");
    el.textContent = "❌ " + msg;
    el.classList.remove("hidden");
}

function hideError() {
    $("error").classList.add("hidden");
}

// ============================================================
// ПРЕСЕТЫ
// ============================================================
async function loadPresets() {
    try {
        const res = await fetch(`${API}/api/presets`);
        if (!res.ok) throw new Error("не удалось загрузить пресеты");
        state.presets = await res.json();
        renderPresets();
    } catch (e) {
        $("presets").innerHTML =
            `<div class="loading">⚠️ Не удалось загрузить пресеты: ${e.message}</div>`;
    }
}

function renderPresets() {
    const container = $("presets");
    container.innerHTML = "";

    state.presets.forEach(preset => {
        const card = document.createElement("div");
        card.className = "preset-card";
        card.innerHTML = `
            <div class="emoji">${preset.emoji || "🌸"}</div>
            <div class="name">${preset.name}</div>
            <div class="desc">${preset.description}</div>
            <div class="groups">${preset.groups.join(" · ")}</div>
        `;
        card.onclick = () => applyPreset(preset);
        container.appendChild(card);
    });
}

function applyPreset(preset) {
    $("groups").value = preset.groups.join(" ");
    document.querySelectorAll(".preset-card").forEach(c => {
        c.classList.toggle("selected",
            c.querySelector(".name").textContent === preset.name);
    });
}

// ============================================================
// АНАЛИЗ
// ============================================================
async function analyzeGroups(groups) {
    const res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ groups })
    });
    return await res.json();
}

function renderAnalysis(data) {
    const panel = $("analysis");
    const content = $("analysis-content");
    panel.classList.remove("hidden");

    content.className = `status-${data.status}`;
    content.innerHTML = `
        <strong>Распределение:</strong> ${JSON.stringify(data.groups)}<br>
        <strong>Всего камней:</strong> ${data.total}<br><br>
        ${data.message}
    `;

    if (data.suggestions && data.suggestions.length) {
        const ul = document.createElement("ul");
        ul.className = "suggestions";
        data.suggestions.forEach(s => {
            const li = document.createElement("li");
            li.textContent = s;
            ul.appendChild(li);
        });
        content.appendChild(ul);
    }
}

// ============================================================
// ВАРИАНТЫ (когда введено одно число)
// ============================================================
async function loadVariants(total) {
    const res = await fetch(`${API}/api/variants`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ total })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "ошибка загрузки вариантов");
    }
    return await res.json();
}

function renderVariants(data) {
    const panel = $("variants-panel");
    const content = $("variants-content");
    panel.classList.remove("hidden");
    content.innerHTML = "";

    data.variants.forEach(v => {
        const item = document.createElement("div");
        item.className = "variant-item";
        item.innerHTML = `
            <span class="name">${v.name}</span>
            <span class="groups">${v.groups.join(" · ")}</span>
        `;
        item.onclick = () => {
            $("groups").value = v.groups.join(" ");
            panel.classList.add("hidden");
            generateGarden();
        };
        content.appendChild(item);
    });
}

// ============================================================
// ГЕНЕРАЦИЯ
// ============================================================
async function generateGarden() {
    hideError();

    const raw = $("groups").value.trim();
    if (!raw) {
        showError("Введите распределение камней.");
        return;
    }

    // Парсим
    const nums = raw.replace(/,/g, " ").replace(/;/g, " ")
                    .split(/\s+/).filter(Boolean)
                    .map(x => parseInt(x, 10));

    if (nums.some(isNaN) || nums.some(n => n < 0)) {
        showError("Введите целые неотрицательные числа через пробел.");
        return;
    }

    // Случай 1: одно число — запросить варианты
    if (nums.length === 1) {
        try {
            const variants = await loadVariants(nums[0]);
            renderVariants(variants);
            return;
        } catch (e) {
            showError(e.message);
            return;
        }
    }

    // Случай 2: несколько чисел — анализ и генерация
    try {
        const analysis = await analyzeGroups(nums);
        renderAnalysis(analysis);

        if (analysis.status === "error") {
            showError("Генерация невозможна. Исправьте распределение.");
            return;
        }

        // Генерация PNG
        const res = await fetch(`${API}/api/render`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                groups: nums,
                show_golden_grid: $("golden-grid").checked,
                seed: 42
            })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "ошибка генерации");
        }

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        $("garden-img").src = url;
        $("btn-download").href = url;
        $("result").classList.remove("hidden");

    } catch (e) {
        showError(e.message);
    }
}

// ============================================================
// СЛУЧАЙНЫЙ САД
// ============================================================
function randomGarden() {
    const nGroups = [3, 5, 7][Math.floor(Math.random() * 3)];
    const groups = [];
    let remaining = 3 + Math.floor(Math.random() * 20);

    for (let i = 0; i < nGroups - 1; i++) {
        const max = Math.min(7, remaining - (nGroups - i - 1));
        const take = 1 + Math.floor(Math.random() * max);
        groups.push(take);
        remaining -= take;
    }
    groups.push(Math.max(1, Math.min(7, remaining)));

    $("groups").value = groups.join(" ");
    generateGarden();
}

// ============================================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    loadPresets();
    $("btn-generate").onclick = generateGarden;
    $("btn-random").onclick = randomGarden;

    // Enter в поле ввода = генерация
    $("groups").addEventListener("keydown", (e) => {
        if (e.key === "Enter") generateGarden();
    });
});