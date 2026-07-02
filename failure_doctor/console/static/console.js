(async function () {
  const statusEl = document.getElementById("status");
  const reportsEl = document.getElementById("reports");
  const detailPanel = document.getElementById("detail");
  const detailTitle = document.getElementById("detail-title");
  const detailJson = document.getElementById("detail-json");

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    return response.json();
  }

  function showDetail(title, payload) {
    detailTitle.textContent = title;
    detailJson.textContent = JSON.stringify(payload, null, 2);
    detailPanel.classList.add("active");
    document.getElementById("dashboard").classList.remove("active");
  }

  document.querySelectorAll(".sidebar button").forEach((button) => {
    button.addEventListener("click", () => {
      const view = button.getAttribute("data-view");
      if (view === "dashboard") {
        detailPanel.classList.remove("active");
        document.getElementById("dashboard").classList.add("active");
      } else {
        showDetail(button.textContent, {
          status: "available",
          note: "Import a report to inspect this section. Missing files degrade to unavailable instead of failing.",
        });
      }
    });
  });

  try {
    const status = await fetchJson("/api/status");
    statusEl.textContent = `${status.version} · ${status.host}:${status.port} · telemetry ${status.telemetry}`;
    const reports = await fetchJson("/api/reports");
    reportsEl.innerHTML = "";
    if (!reports.reports.length) {
      reportsEl.innerHTML = "<div class='card'>No reports imported yet. Start the console with --import-report or use the API.</div>";
      return;
    }
    reports.reports.forEach((report) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<strong>${report.id}</strong><p>${report.summary.user_facing_category} / ${report.summary.subtype}</p>`;
      const button = document.createElement("button");
      button.textContent = "Open report";
      button.addEventListener("click", async () => {
        showDetail(report.id, await fetchJson(`/api/report/${encodeURIComponent(report.id)}`));
      });
      card.appendChild(button);
      reportsEl.appendChild(card);
    });
  } catch (error) {
    statusEl.textContent = `Console load failed: ${error}`;
  }
})();
