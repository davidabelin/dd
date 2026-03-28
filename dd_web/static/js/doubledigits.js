const digitChoices = Array.from({ length: 10 }, (_, index) => index);
const variantChoices = Array.from({ length: 12 }, (_, index) => index);

async function getJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
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

function renderInference(card, payload) {
  card.querySelector(".example-image").src = payload.example.image_uri;
  card.querySelector(".prediction").textContent = `Prediction: ${JSON.stringify(payload.prediction)}`;
  card.querySelector(".confidence").textContent = `Confidence: ${payload.confidence}`;
  card.querySelector(".explanation").textContent = payload.explanation;
  const resultImage = card.querySelector(".result-image");
  if (resultImage) {
    resultImage.src = payload.result_image_uri || "";
    resultImage.style.display = payload.result_image_uri ? "block" : "none";
  }
}

function renderVisualGroup(container, payload) {
  container.innerHTML = "";
  (payload.items || []).forEach((item) => {
    const card = document.createElement("div");
    card.className = "visual-card";
    const title = document.createElement("h3");
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
      ["image_uri", "coefficient_uri"].forEach((key) => {
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
  if (useExample) {
    return {
      level,
      example_id: card.querySelector(".example-select").value,
    };
  }
  if (level === "single") {
    return {
      level,
      digit: Number(card.querySelector(".digit-select").value),
      variant: Number(card.querySelector(".variant-select").value),
    };
  }
  if (level === "double") {
    return {
      level,
      left: Number(card.querySelector(".left-select").value),
      right: Number(card.querySelector(".right-select").value),
    };
  }
  return {
    level,
    left: Number(card.querySelector(".left-select").value),
    right: Number(card.querySelector(".right-select").value),
    operator: card.querySelector(".operator-select").value,
  };
}

async function refreshCard(card, useExample) {
  const payload = buildPayload(card, useExample);
  const inference = await getJson("/api/v1/infer", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderInference(card, inference);

  const params = new URLSearchParams();
  Object.entries(payload).forEach(([key, value]) => params.set(key, value));
  const featureMaps = await getJson(`/api/v1/visualizations/feature_maps?${params.toString()}`);
  const prototype = await getJson(`/api/v1/visualizations/prototype?${params.toString()}`);
  renderVisualGroup(card.querySelector(".feature-maps"), featureMaps);
  renderVisualGroup(card.querySelector(".prototype"), prototype);
}

async function initializeCard(card) {
  const level = card.dataset.level;
  const examplesPayload = await getJson(`/api/v1/examples?level=${level}`);
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

  card.querySelector(".load-example").addEventListener("click", () => refreshCard(card, true));
  card.querySelector(".run-structured").addEventListener("click", () => refreshCard(card, false));
  await refreshCard(card, true);
}

document.querySelectorAll(".lab-card").forEach((card) => {
  initializeCard(card);
});
