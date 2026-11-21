import { request } from './http.js';
import { createActionQueue } from './action-queue.js';

// Anonymous mock session identifier created once per application lifecycle
const sessionCode = crypto.randomUUID();
let planCode = null;
let catalogueCache = [];

const enqueue = createActionQueue();

// DOM elements
const sessionCodeEl = document.getElementById('session-code');
const sessionP = document.getElementById('session');
const planCodeEl = document.getElementById('plan-code');
const healthBtn = document.getElementById('health');
const healthStatusEl = document.getElementById('health-status');
const statusP = document.getElementById('status');
const errorMessageEl = document.getElementById('error-message');
const errorTextEl = document.getElementById('error-text');
const successMessageEl = document.getElementById('success-message');
const successTextEl = document.getElementById('success-text');
const catalogueListEl = document.getElementById('catalogue-list');
const equipmentDetailEl = document.getElementById('equipment-detail');
const detailCodeEl = document.getElementById('detail-code');
const detailNameEl = document.getElementById('detail-name');
const detailMassEl = document.getElementById('detail-mass');
const detailNotesEl = document.getElementById('detail-notes');
const totalMassEl = document.getElementById('total-mass');
const planItemsBodyEl = document.getElementById('plan-items-body');
const addItemForm = document.getElementById('add-item-form');
const equipmentSelect = document.getElementById('equipment-select');
const unitCountInput = document.getElementById('unit-count-input');
const addBtn = document.getElementById('add-btn');
const outputEl = document.getElementById('output');

sessionCodeEl.textContent = sessionCode;
if (sessionP) sessionP.textContent = `Session Code: ${sessionCode}`;

/** Display visible error alert on the page */
function showError(error) {
  const code = error.code ? ` [${error.code}]` : '';
  const message = error.serverMessage || error.message || 'An unexpected error occurred.';
  errorTextEl.textContent = `${message}${code}`;
  errorMessageEl.classList.remove('hidden');
  successMessageEl.classList.add('hidden');
  if (statusP) {
    statusP.textContent = `Error: ${message}${code}`;
    statusP.classList.remove('hidden');
  }
  if (outputEl) {
    outputEl.textContent = JSON.stringify({ error: message, code: error.code, status: error.status }, null, 2);
  }
}

/** Display visible success banner */
function showSuccess(message) {
  successTextEl.textContent = message;
  successMessageEl.classList.remove('hidden');
  errorMessageEl.classList.add('hidden');
  if (statusP) {
    statusP.textContent = message;
    statusP.classList.remove('hidden');
  }
}

/** Clear notification alerts */
function clearNotifications() {
  errorMessageEl.classList.add('hidden');
  successMessageEl.classList.add('hidden');
  if (statusP) statusP.classList.add('hidden');
}

/** Check backend health */
async function checkHealth() {
  healthBtn.disabled = true;
  healthStatusEl.textContent = 'Checking...';
  try {
    const res = await request('/health');
    healthStatusEl.textContent = res?.status === 'ok' ? '✓ Online' : '✓ Connected';
    healthStatusEl.style.color = '#15803d';
    outputEl.textContent = JSON.stringify(res, null, 2);
  } catch (err) {
    healthStatusEl.textContent = '✗ Offline';
    healthStatusEl.style.color = '#b91c1c';
    showError(err);
  } finally {
    healthBtn.disabled = false;
  }
}

/** Fetch and render the equipment catalogue */
async function loadCatalogue() {
  try {
    catalogueListEl.innerHTML = '<p class="empty-state">Loading equipment catalogue...</p>';
    const items = await request('/equipment-types');

    catalogueCache = items || [];

    if (!catalogueCache.length) {
      catalogueListEl.innerHTML = '<p class="empty-state">No equipment available in catalogue.</p>';
      return;
    }

    // Populate catalogue selection cards
    catalogueListEl.innerHTML = '';
    equipmentSelect.innerHTML = '<option value="" disabled selected>Select an item...</option>';

    catalogueCache.forEach(item => {
      // Equipment item button/card
      const card = document.createElement('div');
      card.className = 'equipment-item';
      card.dataset.code = item.equipmentCode;
      card.innerHTML = `
        <div>
          <strong>${item.name}</strong>
          <div style="font-size: 0.85rem; color: #475569;">${item.equipmentCode}</div>
        </div>
        <span style="font-size: 0.9rem; font-weight: 500;">${item.unitMassKg} kg</span>
      `;
      card.addEventListener('click', () => loadEquipmentDetail(item.equipmentCode, card));
      catalogueListEl.appendChild(card);

      // Add to select dropdown
      const option = document.createElement('option');
      option.value = item.equipmentCode;
      option.textContent = `${item.equipmentCode} - ${item.name} (${item.unitMassKg} kg)`;
      equipmentSelect.appendChild(option);
    });
  } catch (err) {
    showError(err);
    catalogueListEl.innerHTML = '<p class="empty-state" style="color: #b91c1c;">Failed to load catalogue.</p>';
  }
}

/** Fetch and display details for a selected equipment item */
async function loadEquipmentDetail(equipmentCode, cardElement) {
  try {
    document.querySelectorAll('.equipment-item').forEach(el => el.classList.remove('selected'));
    if (cardElement) cardElement.classList.add('selected');

    const item = await request(`/equipment-types/${equipmentCode}`);

    if (!item) return;

    detailCodeEl.textContent = item.equipmentCode;
    detailNameEl.textContent = item.name;
    detailMassEl.textContent = item.unitMassKg;
    detailNotesEl.textContent = item.handlingNotes || 'None';
    equipmentDetailEl.classList.remove('hidden');

    // Preselect in the dropdown for user convenience
    equipmentSelect.value = item.equipmentCode;
    outputEl.textContent = JSON.stringify(item, null, 2);
  } catch (err) {
    showError(err);
  }
}

/** Initialise or retrieve the session's load plan */
async function initLoadPlan() {
  try {
    const res = await enqueue(() => request('/load-plans', {
      method: 'POST',
      session: sessionCode
    }));
    planCode = res?.planCode;

    planCodeEl.textContent = planCode || 'Unknown';
    outputEl.textContent = JSON.stringify(res, null, 2);

    await fetchAndRenderPlan();
  } catch (err) {
    showError(err);
  }
}

/** Fetch authoritative load plan from backend and redraw UI */
async function fetchAndRenderPlan() {
  if (!planCode) return;
  try {
    const plan = await request(`/load-plans/${planCode}`, { session: sessionCode });

    outputEl.textContent = JSON.stringify(plan, null, 2);

    // Display the server's authoritative total mass (NEVER calculate client-side)
    totalMassEl.textContent = plan.totalMassKg !== undefined ? plan.totalMassKg : 0;

    const items = plan.items || [];
    if (!items.length) {
      planItemsBodyEl.innerHTML = `
        <tr>
          <td colspan="6" class="empty-state">No equipment in load plan yet. Add items below.</td>
        </tr>
      `;
      return;
    }

    planItemsBodyEl.innerHTML = '';
    items.forEach(item => {
      const lineMass = item.lineMassKg; // calculated by the server
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><code>${item.equipmentCode}</code></td>
        <td><strong>${item.name || item.equipmentCode}</strong></td>
        <td>
          <input
            type="number"
            class="item-count-input"
            data-code="${item.equipmentCode}"
            value="${item.unitCount}"
            min="0"
            max="20"
            step="1"
          />
        </td>
        <td>${item.unitMassKg} kg</td>
        <td><strong>${lineMass} kg</strong></td>
        <td class="actions-cell">
          <button class="btn-sm btn-outline update-btn" data-code="${item.equipmentCode}" type="button">Update</button>
          <button class="btn-sm btn-danger remove-btn" data-code="${item.equipmentCode}" type="button">Remove</button>
        </td>
      `;

      // Wire update button
      const countInput = row.querySelector('.item-count-input');
      const updateBtn = row.querySelector('.update-btn');
      updateBtn.addEventListener('click', () => {
        const rawVal = countInput.value.trim();
        const count = rawVal === '' ? NaN : Number(rawVal);
        handleUpdateItem(item.equipmentCode, count, updateBtn);
      });

      // Wire remove button
      const removeBtn = row.querySelector('.remove-btn');
      removeBtn.addEventListener('click', () => {
        handleRemoveItem(item.equipmentCode, removeBtn);
      });

      planItemsBodyEl.appendChild(row);
    });
  } catch (err) {
    showError(err);
  }
}

/** Add equipment to plan */
async function handleAddItem(e) {
  e.preventDefault();
  clearNotifications();

  const equipmentCode = equipmentSelect.value;
  const rawCount = unitCountInput.value.trim();
  const unitCount = rawCount === '' ? NaN : Number(rawCount);

  if (!equipmentCode) {
    showError(new Error('Please select an equipment item.'));
    return;
  }

  addBtn.disabled = true;
  try {
    await enqueue(async () => {
      const result = await request(`/load-plans/${planCode}/items`, {
        method: 'POST',
        session: sessionCode,
        body: { equipmentCode, unitCount }
      });
      showSuccess(`Added ${equipmentCode} (${unitCount} units) to load plan.`);
      outputEl.textContent = JSON.stringify(result, null, 2);
      await fetchAndRenderPlan();
    });
  } catch (err) {
    showError(err);
  } finally {
    addBtn.disabled = false;
  }
}

/** Update equipment count in load plan */
async function handleUpdateItem(equipmentCode, unitCount, button) {
  clearNotifications();
  button.disabled = true;

  try {
    await enqueue(async () => {
      const result = await request(`/load-plans/${planCode}/items/${equipmentCode}`, {
        method: 'PUT',
        session: sessionCode,
        body: { unitCount }
      });
      showSuccess(`Updated ${equipmentCode} quantity to ${unitCount}.`);
      outputEl.textContent = JSON.stringify(result, null, 2);
      await fetchAndRenderPlan();
    });
  } catch (err) {
    showError(err);
    // On failure, re-render the plan to ensure UI reflects unchanged server state
    await enqueue(() => fetchAndRenderPlan());
  } finally {
    button.disabled = false;
  }
}

/** Remove equipment item from load plan */
async function handleRemoveItem(equipmentCode, button) {
  clearNotifications();
  button.disabled = true;

  try {
    await enqueue(async () => {
      await request(`/load-plans/${planCode}/items/${equipmentCode}`, {
        method: 'DELETE',
        session: sessionCode
      });
      showSuccess(`Removed ${equipmentCode} from load plan.`);
      await fetchAndRenderPlan();
    });
  } catch (err) {
    showError(err);
  } finally {
    button.disabled = false;
  }
}

// Event listeners
healthBtn.addEventListener('click', checkHealth);
addItemForm.addEventListener('submit', handleAddItem);

// Initialise application
(async function init() {
  await loadCatalogue();
  await initLoadPlan();
})();