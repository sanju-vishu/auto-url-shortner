const form = document.getElementById("shorten-form");
const message = document.getElementById("message");
const result = document.getElementById("result");
const shortUrl = document.getElementById("short-url");
const originalUrl = document.getElementById("original-url");
const submitBtn = document.getElementById("submit-btn");
const copyBtn = document.getElementById("copy-btn");

function notify(text, isError=false) {
  message.textContent = text;
  message.style.color = isError ? "#b54747" : "#21875a";
}
async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    const old = button.textContent; button.textContent = "Copied!";
    setTimeout(() => button.textContent = old, 1200);
  } catch { window.prompt("Copy this link:", text); }
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  result.classList.add("hidden");
  submitBtn.disabled = true;
  submitBtn.textContent = "Creating link…";
  const data = Object.fromEntries(new FormData(form).entries());
  Object.keys(data).forEach(k => { if (!data[k]) delete data[k]; });
  try {
    const response = await fetch("/api/links", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });
    const body = await response.json();
    if (!response.ok) {
      const detail = body.detail;
      throw new Error(Array.isArray(detail) ? detail.map(x => x.msg).join(", ") : (detail || "Unable to create link."));
    }
    shortUrl.href = body.short_url;
    shortUrl.textContent = body.short_url;
    originalUrl.textContent = body.original_url;
    copyBtn.dataset.url = body.short_url;
    result.classList.remove("hidden");
    notify("Your short link is ready.");
    const empty = document.getElementById("empty-row"); if (empty) empty.remove();
    const row = document.createElement("tr");
    const safe = (s) => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
    row.innerHTML = `<td><a class="short-link" href="${safe(body.short_url)}" target="_blank" rel="noopener noreferrer">${safe(body.short_url)}</a><div class="subtext">${safe(body.title || "Untitled link")}</div></td><td class="destination" title="${safe(body.original_url)}">${safe(body.original_url)}</td><td><span class="click-count">0</span></td><td><span class="pill active">Active</span></td><td><button class="small-copy" data-url="${safe(body.short_url)}">Copy</button></td>`;
    document.getElementById("links-body").prepend(row);
    form.reset();
  } catch (err) { notify(err.message, true); }
  finally { submitBtn.disabled = false; submitBtn.innerHTML = 'Shorten URL <span>→</span>'; }
});
copyBtn.addEventListener("click", () => copyText(copyBtn.dataset.url, copyBtn));
document.addEventListener("click", (event) => {
  const button = event.target.closest(".small-copy");
  if (button) copyText(button.dataset.url, button);
});
