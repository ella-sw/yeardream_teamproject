const form = document.querySelector("#scan-form");
const input = document.querySelector("#entry-url");
const startButton = document.querySelector("#start-button");
const scanPanel = document.querySelector("#scan-panel");
const stateHeading = document.querySelector("#scan-state");
const message = document.querySelector("#scan-message");
const counts = document.querySelector("#scan-counts");
const warnings = document.querySelector("#warning-list");
const findingsBody = document.querySelector("#findings-body");
const cancelButton = document.querySelector("#cancel-button");
const resultFile = document.querySelector("#result-file");

let activeJobId = null;
let pollTimer = null;

const labels = {
  QUEUED: "대기 중",
  RUNNING: "검사 중",
  COMPLETED: "검사 완료",
  PARTIAL: "일부 검사 완료",
  FAILED: "검사 실패",
  CANCELLED: "검사 취소",
};

function addCell(row, value, code = false) {
  const cell = document.createElement("td");
  if (code) {
    const node = document.createElement("code");
    node.textContent = value;
    cell.append(node);
  } else {
    cell.textContent = value;
  }
  row.append(cell);
}

function renderFindings(findings) {
  findingsBody.replaceChildren();
  for (const finding of findings || []) {
    const row = document.createElement("tr");
    addCell(row, finding.technique);
    addCell(row, finding.url);
    addCell(row, finding.evidence_text);
    addCell(row, finding.location, true);
    findingsBody.append(row);
  }
}

function renderWarnings(items) {
  warnings.replaceChildren();
  for (const warning of items || []) {
    const line = document.createElement("p");
    line.textContent = warning;
    warnings.append(line);
  }
}

async function refreshJob(jobId) {
  const response = await fetch(`/api/scans/${encodeURIComponent(jobId)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("검사 상태를 가져오지 못했습니다.");
  const job = await response.json();
  stateHeading.textContent = labels[job.state] || job.state;
  message.textContent = job.error || (job.state === "COMPLETED" && job.result_path
    ? `${job.entry_url} · 결과 파일: ${job.result_path}`
    : job.entry_url);
  counts.textContent = `확인한 페이지 ${job.progress.pages_done} · 검출 ${job.progress.finding_count} · 대기 ${job.progress.pending_pages}`;
  renderWarnings(job.progress.warnings);
  cancelButton.hidden = !["QUEUED", "RUNNING"].includes(job.state);
  if (["COMPLETED", "PARTIAL"].includes(job.state)) {
    const resultResponse = await fetch(`/api/scans/${encodeURIComponent(jobId)}/result`, { cache: "no-store" });
    if (resultResponse.ok) {
      const result = await resultResponse.json();
      renderFindings(result.findings);
      resultFile.href = `/api/scans/${encodeURIComponent(jobId)}/result`;
      resultFile.hidden = false;
    }
  }
  if (!["QUEUED", "RUNNING"].includes(job.state)) {
    clearInterval(pollTimer);
    pollTimer = null;
    startButton.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  scanPanel.hidden = false;
  stateHeading.textContent = "요청 확인 중";
  message.textContent = "입력 주소와 검사 범위를 확인합니다.";
  counts.textContent = "";
  renderWarnings([]);
  renderFindings([]);
  resultFile.hidden = true;
  startButton.disabled = true;
  try {
    const response = await fetch("/api/scans", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entry_url: input.value.trim() }),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail || "검사를 시작하지 못했습니다.");
    activeJobId = body.job_id;
    await refreshJob(activeJobId);
    if (["QUEUED", "RUNNING"].includes(body.state)) {
      pollTimer = setInterval(() => refreshJob(activeJobId).catch((error) => {
        message.textContent = error.message;
      }), 1000);
    }
  } catch (error) {
    stateHeading.textContent = "요청 실패";
    message.textContent = error.message;
    startButton.disabled = false;
  }
});

cancelButton.addEventListener("click", async () => {
  if (!activeJobId) return;
  await fetch(`/api/scans/${encodeURIComponent(activeJobId)}/cancel`, { method: "POST" });
  message.textContent = "현재 페이지 처리를 마친 뒤 취소합니다.";
});
