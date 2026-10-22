const FIELDS = ["name", "email", "phone", "notes"];

let contacts = [];
let editingId = null;
const selected = new Set();

const rowsEl = document.getElementById("rows");
const statusEl = document.getElementById("status");
const bulkBtn = document.getElementById("bulk-delete");
const selectAll = document.getElementById("select-all");
let bulkDeleting = false;

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function setStatus(text) {
  statusEl.textContent = text;
}

function setBulkDeleting(value) {
  bulkDeleting = value;
  bulkBtn.textContent = value ? "Deleting..." : "Delete selected";
  bulkBtn.setAttribute("aria-busy", String(value));
  bulkBtn.classList.toggle("loading", value);
  bulkBtn.disabled = value || selected.size === 0;
}

async function load() {
  contacts = await api("GET", "/api/contacts");
  render();
}

function el(tag, props = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  node.append(...children);
  return node;
}

function render() {
  rowsEl.replaceChildren(...contacts.map(renderRow));
  bulkBtn.disabled = bulkDeleting || selected.size === 0;
  selectAll.checked = contacts.length > 0 && selected.size === contacts.length;
}

function renderRow(c) {
  const tr = el("tr");
  const check = el("input", { type: "checkbox", checked: selected.has(c.id) });
  check.addEventListener("change", () => {
    check.checked ? selected.add(c.id) : selected.delete(c.id);
    render();
  });
  tr.append(el("td", {}, check));

  if (editingId === c.id) {
    const inputs = FIELDS.map((f) => el("input", { value: c[f], name: f }));
    inputs.forEach((i) => tr.append(el("td", {}, i)));
    const save = el("button", { textContent: "Save" });
    save.addEventListener("click", () => saveEdit(c.id, inputs));
    const cancel = el("button", { textContent: "Cancel" });
    cancel.addEventListener("click", () => {
      editingId = null;
      render();
    });
    tr.append(el("td", { className: "actions" }, save, cancel));
  } else {
    FIELDS.forEach((f) => tr.append(el("td", { textContent: c[f] })));
    const edit = el("button", { textContent: "Edit" });
    edit.addEventListener("click", () => {
      editingId = c.id;
      render();
    });
    const del = el("button", { textContent: "Delete" });
    del.addEventListener("click", () => deleteContact(c.id));
    tr.append(el("td", { className: "actions" }, edit, del));
  }
  return tr;
}

async function saveEdit(id, inputs) {
  const body = Object.fromEntries(inputs.map((i) => [i.name, i.value]));
  try {
    await api("PUT", `/api/contacts/${id}`, body);
    editingId = null;
    setStatus("Saved.");
    await load();
  } catch (err) {
    setStatus(`Could not save contact: ${err.message}`);
  }
}

async function deleteContact(id) {
  try {
    await api("DELETE", `/api/contacts/${id}`);
    selected.delete(id);
    setStatus("Deleted.");
    await load();
  } catch (err) {
    setStatus(`Could not delete contact: ${err.message}`);
  }
}

bulkBtn.addEventListener("click", async () => {
  const ids = [...selected];
  setStatus(`Deleting ${ids.length}...`);
  setBulkDeleting(true);
  try {
    await api("POST", "/api/contacts/bulk-delete", { ids });
    selected.clear();
    setStatus(`Deleted ${ids.length}.`);
    await load();
  } catch (err) {
    setStatus(`Could not delete selected contacts: ${err.message}`);
  } finally {
    setBulkDeleting(false);
    render();
  }
});

selectAll.addEventListener("change", () => {
  selected.clear();
  if (selectAll.checked) contacts.forEach((c) => selected.add(c.id));
  render();
});

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const body = Object.fromEntries(new FormData(form));
  try {
    await api("POST", "/api/contacts", body);
    form.reset();
    setStatus("Added.");
    await load();
  } catch (err) {
    setStatus(`Could not add contact: ${err.message}`);
  }
});

load().catch((err) => setStatus(`Could not load contacts: ${err.message}`));
