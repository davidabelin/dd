const frontendConfig = JSON.parse(document.querySelector("#dd-frontend-config").textContent);
const apiBase = frontendConfig.apiBase;

const digitChoices = Array.from({ length: 10 }, (_, index) => index);
const variantChoices = Array.from({ length: 12 }, (_, index) => index);
const operatorChoices = [
  { value: "add", label: "Add (+)" },
  { value: "subtract", label: "Subtract (-)" },
  { value: "multiply", label: "Multiply (×)" },
  { value: "divide", label: "Divide (÷)" },
];

async function getJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      detail = payload.error || payload.message || JSON.stringify(payload);
    } catch {
      const text = await response.text();
      if (text) {
        detail = text;
      }
    }
    throw new Error(detail);
  }
  return response.json();
}

function buildOptions(select, values, formatter = (value) => value) {
  select.innerHTML = "";
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = formatter(value);
    select.appendChild(option);
  });
}

function buildOperatorOptions(select) {
  select.innerHTML = "";
  operatorChoices.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.value;
    option.textContent = item.label;
    select.appendChild(option);
  });
}

function setStatus(card, state, text) {
  const status = card.querySelector(".lab-status");
  status.classList.remove("is-idle", "is-loading", "is-ok", "is-error");
  status.classList.add(`is-${state}`);
  status.textContent = text;
}

function humanizeKey(key) {
  return String(key)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}

function renderKeyValueList(container, payload) {
  container.innerHTML = "";
  const entries = Object.entries(payload || {});
  if (!entries.length) {
    return;
  }
  entries.forEach(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = humanizeKey(key);
    const dd = document.createElement("dd");
    dd.textContent = Array.isArray(value) ? value.join(", ") : String(value);
    container.appendChild(dt);
    container.appendChild(dd);
  });
}

function renderInference(card, payload) {
  card.querySelector(".example-image").src = payload.example.image_uri;
  card.querySelector(".prediction").textContent = `Prediction: ${JSON.stringify(payload.prediction)}`;
  card.querySelector(".confidence").textContent = `Confidence: ${payload.confidence}`;
  card.querySelector(".preset-label").textContent = `Preset: ${payload.preset}`;
  card.querySelector(".explanation").textContent = payload.explanation;
  renderKeyValueList(card.querySelector(".example-meta"), payload.example.metadata);
  const resultImage = card.querySelector(".result-image");
  if (resultImage) {
    resultImage.src = payload.result_image_uri || "";
    resultImage.style.display = payload.result_image_uri ? "block" : "none";
  }
}

function renderVisualGroup(container, payload) {
  container.innerHTML = "";
  (payload.items || []).forEach((item) => {
    const card = document.createElement("article");
    card.className = "visual-card";

    const title = document.createElement("h4");
    title.textContent = item.segment || item.label || payload.kind;
    card.appendChild(title);

    if (item.maps) {
      item.maps.forEach((map) => {
        const label = document.createElement("p");
        label.textContent = map.name;
        const img = document.createElement("img");
        img.className = "visual-thumb";
        img.src = map.image_uri;
        img.alt = map.name;
        card.appendChild(label);
        card.appendChild(img);
      });
    } else {
      const imageKeys = ["image_uri", "coefficient_uri"];
      imageKeys.forEach((key) => {
        if (!item[key]) {
          return;
        }
        const img = document.createElement("img");
        img.className = "visual-thumb";
        img.src = item[key];
        img.alt = item.label || payload.kind;
        card.appendChild(img);
      });
    }
    container.appendChild(card);
  });
}

function buildPayload(card, useExample) {
  const level = card.dataset.level;
  const payload = { level };
  const preset = card.querySelector(".preset-select")?.value;
  if (preset) {
    payload.preset = preset;
  }
  if (useExample) {
    payload.example_id = card.querySelector(".example-select").value;
    return payload;
  }
  if (level === "single") {
    payload.digit = Number(card.querySelector(".digit-select").value);
    payload.variant = Number(card.querySelector(".variant-select").value);
    return payload;
  }
  payload.left = Number(card.querySelector(".left-select").value);
  payload.right = Number(card.querySelector(".right-select").value);
  if (level === "arithmetic") {
    payload.operator = card.querySelector(".operator-select").value;
  }
  return payload;
}

function applySelectedPresetMeta(card, presetsPayload) {
  const presetSelect = card.querySelector(".preset-select");
  const selected = presetsPayload.presets.find((item) => item.name === presetSelect.value) || presetsPayload.presets[0];
  if (!selected) {
    card.querySelector(".preset-meta").innerHTML = "";
    return;
  }
  presetSelect.value = selected.name;
  renderKeyValueList(card.querySelector(".preset-meta"), {
    source_notebook: selected.source_notebook,
    description: selected.description,
    default: selected.default ? "yes" : "no",
    artifact_ready: selected.artifact_ready ? "yes" : "no",
    train_size: selected.train_size,
    test_size: selected.test_size,
    epochs: selected.epochs,
    batch_size: selected.batch_size,
  });
}

async function loadPresets(card) {
  if (card.dataset.presetsLoaded === "1") {
    return;
  }
  const presetsPayload = await getJson(`${apiBase}/presets?level=${encodeURIComponent(card.dataset.level)}`);
  const presetSelect = card.querySelector(".preset-select");
  presetSelect.innerHTML = "";
  presetsPayload.presets.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.name;
    option.textContent = item.default ? `${item.name} (default)` : item.name;
    presetSelect.appendChild(option);
  });
  presetSelect.value = presetsPayload.default_preset;
  presetSelect.addEventListener("change", () => applySelectedPresetMeta(card, presetsPayload));
  applySelectedPresetMeta(card, presetsPayload);
  card.dataset.presetsLoaded = "1";
}

async function refreshCard(card, useExample) {
  const payload = buildPayload(card, useExample);
  setStatus(card, "loading", "Running the notebook-derived model and refreshing all views...");
  try {
    const inference = await getJson(`${apiBase}/infer`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderInference(card, inference);

    const params = new URLSearchParams();
    Object.entries(payload).forEach(([key, value]) => params.set(key, value));
    const [featureMaps, prototype, comparison] = await Promise.all([
      getJson(`${apiBase}/visualizations/feature_maps?${params.toString()}`),
      getJson(`${apiBase}/visualizations/prototype?${params.toString()}`),
      getJson(`${apiBase}/visualizations/comparison?${params.toString()}`),
    ]);
    renderVisualGroup(card.querySelector(".feature-maps"), featureMaps);
    renderVisualGroup(card.querySelector(".prototype"), prototype);
    renderVisualGroup(card.querySelector(".comparison"), comparison);
    setStatus(card, "ok", `Notebook run complete with preset ${inference.preset}.`);
  } catch (error) {
    setStatus(card, "error", `Notebook run failed: ${error.message}`);
    card.querySelector(".explanation").textContent = error.message;
  }
}

async function initializeCard(card) {
  const level = card.dataset.level;
  const examplesPayload = await getJson(`${apiBase}/examples?level=${encodeURIComponent(level)}`);
  const exampleSelect = card.querySelector(".example-select");
  exampleSelect.innerHTML = "";
  examplesPayload.examples.forEach((example) => {
    const option = document.createElement("option");
    option.value = example.id;
    option.textContent = example.title;
    exampleSelect.appendChild(option);
  });

  const digitSelect = card.querySelector(".digit-select");
  const variantSelect = card.querySelector(".variant-select");
  const leftSelect = card.querySelector(".left-select");
  const rightSelect = card.querySelector(".right-select");
  const operatorSelect = card.querySelector(".operator-select");
  if (digitSelect) {
    buildOptions(digitSelect, digitChoices, (value) => `Digit ${value}`);
  }
  if (variantSelect) {
    buildOptions(variantSelect, variantChoices, (value) => `Sample ${value}`);
  }
  if (leftSelect) {
    buildOptions(leftSelect, digitChoices, (value) => `Left ${value}`);
    leftSelect.value = "1";
  }
  if (rightSelect) {
    buildOptions(rightSelect, digitChoices, (value) => `Right ${value}`);
    rightSelect.value = "2";
  }
  if (operatorSelect) {
    buildOperatorOptions(operatorSelect);
  }

  card.querySelector(".load-example").addEventListener("click", () => refreshCard(card, true));
  card.querySelector(".run-structured").addEventListener("click", () => refreshCard(card, false));

  const advanced = card.querySelector(".dd-advanced");
  advanced.addEventListener("toggle", () => {
    if (advanced.open) {
      loadPresets(card).catch((error) => {
        setStatus(card, "error", `Preset metadata failed to load: ${error.message}`);
      });
    }
  });

  await refreshCard(card, true);
}

document.querySelectorAll(".lab-card").forEach((card) => {
  initializeCard(card).catch((error) => {
    setStatus(card, "error", `Initialization failed: ${error.message}`);
  });
});
