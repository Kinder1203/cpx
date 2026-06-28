const state = {
  ready: false,
  pending: false,
  loadError: "",
  cases: [],
  currentCase: null,
  sessionId: null,
  session: null,
  completed: false,
  report: null,
  nextCase: null,
  selectedReportItemId: null,
};

const elements = Object.fromEntries(
  [
    "infoBtn", "caseReadiness", "caseTitle", "caseMeta", "caseSelect", "readinessList",
    "patientBubble", "learnerBubble", "learnerSprite", "coachSprite", "coachLine",
    "recordToggle", "recordCount", "recordPreview", "recordModal", "recordFeed",
    "closeRecordBtn", "composer", "freeQuestion", "sendBtn", "startBtn", "resetBtn",
    "finishBtn", "assessmentPanel", "assessmentForm", "closeAssessmentBtn",
    "resumeEncounterBtn", "submitAssessmentBtn", "assessmentSummary", "assessmentPrimary",
    "assessmentDifferentials", "assessmentReasoning", "reportPanel", "closeReportBtn",
    "reportCoverage", "reportMissed", "reportReasoning", "missedList", "reportDetail",
    "weaknessTags", "nextFocus", "nextCaseList", "nextCaseBtn",
  ].map((id) => [id, document.querySelector(`#${id}`)]),
);

function setText(node, value) {
  if (node) node.textContent = value;
}

function createTextElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = text;
  return node;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `요청 실패 (${response.status})`);
  return payload;
}

function messages() {
  return state.session?.messages || [];
}

function renderReadiness() {
  elements.readinessList.replaceChildren();
  if (!state.ready) {
    elements.readinessList.append(
      createTextElement("li", state.loadError ? "missing" : "pending", state.loadError || "문진 서버 연결 중"),
    );
    setText(elements.caseTitle, state.loadError ? "서버 확인 필요" : "케이스 준비 중");
    setText(elements.caseMeta, state.loadError || "합성 교육용 데모 카드를 불러오고 있습니다.");
    return;
  }

  elements.caseSelect.replaceChildren(
    ...state.cases.map((caseItem) => {
      const option = document.createElement("option");
      option.value = caseItem.case_id;
      option.textContent = caseItem.title;
      return option;
    }),
  );
  elements.caseSelect.value = state.currentCase.case_id;
  setText(elements.caseTitle, state.currentCase.title);
  setText(elements.caseMeta, state.currentCase.safe_metadata);
  [
    "카드 스키마 검사 통과",
    "질문 기반 정보 공개",
    "형성평가 리포트",
    "로컬 학습 프로필",
  ].forEach((label) => elements.readinessList.append(createTextElement("li", "ready", label)));
}

function renderStatus() {
  const started = Boolean(state.sessionId);

  elements.startBtn.disabled = !state.ready || started || state.pending;
  elements.sendBtn.disabled = !started || state.completed || state.pending;
  elements.freeQuestion.disabled = !started || state.completed || state.pending;
  elements.finishBtn.disabled = !started || state.completed || state.pending || !state.session?.can_complete;
  elements.submitAssessmentBtn.disabled = state.pending;
  elements.caseSelect.disabled = !state.ready || started || state.pending;
}

function renderConversation() {
  const transcript = messages();
  const latestPatient = [...transcript].reverse().find((message) => message.role === "patient");
  const latestLearner = [...transcript].reverse().find((message) => message.role === "learner");
  setText(
    elements.patientBubble,
    latestPatient?.content || "문진 시작을 누르면 표준화 환자 문진이 시작됩니다.",
  );
  if (latestLearner) {
    setText(elements.learnerBubble, latestLearner.content);
    elements.learnerBubble.hidden = false;
  } else {
    elements.learnerBubble.hidden = true;
  }
  renderRecord();
}

function renderRecord() {
  elements.recordFeed.replaceChildren();
  const transcript = messages();
  const questionCount = transcript.filter((message) => message.role === "learner").length;
  setText(elements.recordCount, questionCount ? `질문 ${questionCount}개` : "기록 없음");
  if (!transcript.length) {
    elements.recordFeed.append(createTextElement("p", "empty-state", "질문과 환자 답변이 여기에 기록됩니다."));
    setText(elements.recordPreview, "아직 기록 없음");
    return;
  }
  transcript.forEach((message) => {
    const line = document.createElement("p");
    line.className = `log-line ${message.role}`;
    line.append(createTextElement("strong", "", message.role === "learner" ? "학습자" : "환자"));
    line.append(document.createTextNode(message.content));
    elements.recordFeed.append(line);
  });
  setText(elements.recordPreview, transcript[transcript.length - 1].content);
}

function toggleRecord(forceOpen) {
  const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : elements.recordModal.hidden;
  elements.recordModal.hidden = !shouldOpen;
  elements.recordToggle.setAttribute("aria-expanded", String(shouldOpen));
  if (shouldOpen) elements.recordModal.parentElement.scrollTo({ top: 0, behavior: "auto" });
  if (shouldOpen) elements.closeRecordBtn.focus();
  else elements.recordToggle.focus();
}

async function startEncounter() {
  if (!state.ready || state.sessionId || state.pending) return;
  state.pending = true;
  renderStatus();
  try {
    const payload = await api("/api/sessions", {
      method: "POST",
      body: JSON.stringify({ case_id: state.currentCase.case_id }),
    });
    state.sessionId = payload.session_id;
    state.session = payload.session;
    state.currentCase = payload.case;
    setText(elements.coachLine, "환자에게 직접 질문하세요. 질문한 내용에 한해 답변합니다.");
    renderConversation();
    requestAnimationFrame(() => elements.freeQuestion.focus());
  } catch (error) {
    setText(elements.coachLine, error.message);
  } finally {
    state.pending = false;
    renderStatus();
  }
}

async function submitQuestion(value) {
  const question = value.trim();
  if (!question || !state.sessionId || state.pending || state.completed) return;
  state.pending = true;
  elements.freeQuestion.value = "";
  elements.learnerSprite.classList.add("typing");
  setText(elements.coachLine, "환자 답변을 확인하고 있습니다.");
  renderStatus();
  try {
    const payload = await api(`/api/sessions/${encodeURIComponent(state.sessionId)}/questions`, {
      method: "POST",
      body: JSON.stringify({ question }),
    });
    state.session = payload.session;
    const guidance = {
      answered: "답변에서 확인한 내용을 다음 질문으로 연결하세요.",
      unmatched: "증상, 시작 시점, 병력처럼 한 항목씩 구체적으로 질문하세요.",
      boundary: "환자 역할에서 답할 수 있는 증상과 경험을 질문해 주세요.",
    };
    setText(elements.coachLine, guidance[payload.result.kind] || guidance.answered);
    renderConversation();
  } catch (error) {
    setText(elements.coachLine, error.message);
    elements.freeQuestion.value = question;
  } finally {
    state.pending = false;
    elements.learnerSprite.classList.remove("typing");
    renderStatus();
    elements.freeQuestion.focus();
  }
}

function reportItems() {
  const items = state.report?.items || [];
  const priority = { missed: 0, needs_review: 1, completed: 2 };
  return [...items].sort(
    (left, right) => (priority[left.status] ?? 3) - (priority[right.status] ?? 3),
  );
}

function renderReportList() {
  elements.missedList.replaceChildren();
  reportItems().forEach((item) => {
    const listItem = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "report-item-button";
    button.setAttribute("aria-pressed", String(item.id === state.selectedReportItemId));
    const statusLabel = item.status === "missed"
      ? "놓친 항목"
      : item.status === "needs_review"
        ? "보완 필요"
        : "확인 완료";
    button.append(createTextElement("span", "", `${item.category} · ${statusLabel}`));
    button.append(createTextElement("strong", "", item.label));
    button.append(createTextElement("small", "", item.feedback));
    button.addEventListener("click", () => {
      state.selectedReportItemId = item.id;
      renderReportList();
      renderReportDetail();
    });
    listItem.append(button);
    elements.missedList.append(listItem);
  });
}

function renderReportDetail() {
  elements.reportDetail.replaceChildren();
  const item = reportItems().find((entry) => entry.id === state.selectedReportItemId);
  if (!item) {
    elements.reportDetail.append(createTextElement("p", "empty-state", "표시할 피드백이 없습니다."));
    return;
  }
  elements.reportDetail.append(createTextElement("h3", "", item.label));
  elements.reportDetail.append(createTextElement("p", "detail-summary", item.feedback));

  const whySection = document.createElement("section");
  whySection.className = "detail-section";
  whySection.append(createTextElement("h4", "", "왜 중요한가"));
  whySection.append(createTextElement("p", "detail-copy", item.why_it_matters));
  elements.reportDetail.append(whySection);

  const learnerSection = document.createElement("section");
  learnerSection.className = "detail-section";
  learnerSection.append(createTextElement("h4", "", "내 기록"));
  const learnerEvidence = Array.isArray(item.learner_evidence) ? item.learner_evidence : [];
  if (learnerEvidence.length) {
    const list = document.createElement("ul");
    learnerEvidence.forEach((entry) => list.append(createTextElement("li", "", entry)));
    learnerSection.append(list);
  } else {
    learnerSection.append(createTextElement("p", "detail-copy", "관련 질문 기록이 없습니다."));
  }
  elements.reportDetail.append(learnerSection);

  const evidence = Array.isArray(item.evidence) ? item.evidence : [];
  const validEvidence = evidence.filter((entry) => {
    if (!entry || typeof entry.title !== "string" || typeof entry.url !== "string") return false;
    try {
      return ["http:", "https:"].includes(new URL(entry.url).protocol);
    } catch {
      return false;
    }
  });
  if (validEvidence.length) {
    const evidenceSection = document.createElement("section");
    evidenceSection.className = "detail-section";
    evidenceSection.append(createTextElement("h4", "", "관련 근거"));
    const list = document.createElement("ul");
    validEvidence.forEach((entry) => {
      const listItem = document.createElement("li");
      const link = document.createElement("a");
      link.href = entry.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = entry.title;
      listItem.append(link);
      list.append(listItem);
    });
    evidenceSection.append(list);
    elements.reportDetail.append(evidenceSection);
  }
}

function renderNextPractice() {
  elements.weaknessTags.replaceChildren();
  elements.nextCaseList.replaceChildren();
  const reviewItems = state.report.items.filter((item) => ["missed", "needs_review"].includes(item.status));
  reviewItems.slice(0, 4).forEach((item) => {
    elements.weaknessTags.append(createTextElement("span", "", item.label));
  });
  const modeLabel = state.nextCase?.mode === "progression" ? "확장 연습" : "보완 연습";
  if (!reviewItems.length && state.nextCase?.mode === "progression") {
    elements.weaknessTags.append(createTextElement("span", "", "새로운 계통 적용"));
  }
  const directions = state.nextCase?.directions || [];
  const nextFocus = directions[0] || "같은 핵심 문진을 유지하며 질문 순서를 반복합니다.";
  setText(elements.nextFocus, `${modeLabel} · ${nextFocus}`);
  directions.slice(1).forEach((direction) => {
    elements.nextCaseList.append(createTextElement("li", "", direction));
  });
  const recommendedCase = state.nextCase?.case;
  elements.nextCaseBtn.hidden = !recommendedCase;
  if (recommendedCase) {
    setText(elements.nextCaseBtn, `${recommendedCase.title} 시작`);
  }
}

function toggleAssessment(forceOpen) {
  const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : elements.assessmentPanel.hidden;
  elements.assessmentPanel.hidden = !shouldOpen;
  if (!shouldOpen) {
    elements.finishBtn.focus();
    return;
  }
  toggleRecord(false);
  elements.assessmentPanel.parentElement.scrollTo({ top: 0, behavior: "auto" });
  elements.assessmentSummary.focus();
}

function assessmentPayload() {
  return {
    problem_summary: elements.assessmentSummary.value,
    primary_impression: elements.assessmentPrimary.value,
    differential_diagnoses: elements.assessmentDifferentials.value,
    reasoning: elements.assessmentReasoning.value,
  };
}

async function finishEncounter() {
  if (!state.session?.can_complete || state.pending || state.completed) return;
  state.pending = true;
  renderStatus();
  try {
    const payload = await api(`/api/sessions/${encodeURIComponent(state.sessionId)}/complete`, {
      method: "POST",
      body: JSON.stringify({ assessment: assessmentPayload() }),
    });
    state.completed = true;
    state.report = payload.report;
    state.nextCase = payload.next_case;
    const items = reportItems();
    state.selectedReportItemId = items[0]?.id || null;
    setText(elements.reportCoverage, `${state.report.coverage_percent}%`);
    setText(elements.reportMissed, String(state.report.items.filter((item) => item.status === "missed").length));
    setText(elements.reportReasoning, String(state.report.assessment_review_count));
    renderReportList();
    renderReportDetail();
    renderNextPractice();
    toggleRecord(false);
    elements.assessmentPanel.hidden = true;
    elements.reportPanel.parentElement.scrollTo({ top: 0, behavior: "auto" });
    elements.reportPanel.hidden = false;
    elements.reportPanel.focus({ preventScroll: true });
    setText(elements.patientBubble, "문진이 종료됐습니다. 교육용 리포트를 확인해 주세요.");
    setText(elements.coachLine, "리포트는 문진 기록과 데모 카드의 비공개 형성평가 기준으로 생성했습니다.");
    elements.coachSprite.classList.add("writing");
  } catch (error) {
    setText(elements.coachLine, error.message);
  } finally {
    state.pending = false;
    renderStatus();
  }
}

function resetEncounter() {
  state.sessionId = null;
  state.session = null;
  state.completed = false;
  state.report = null;
  state.nextCase = null;
  state.selectedReportItemId = null;
  elements.assessmentForm.reset();
  elements.assessmentPanel.hidden = true;
  elements.reportPanel.hidden = true;
  elements.recordModal.hidden = true;
  elements.recordToggle.setAttribute("aria-expanded", "false");
  elements.coachSprite.classList.remove("writing");
  setText(elements.coachLine, "환자에게 직접 질문하면 질문한 내용에 한해 답변합니다.");
  renderConversation();
  renderStatus();
}

async function startRecommendedCase() {
  const recommendedCase = state.nextCase?.case;
  if (!recommendedCase || state.pending) return;
  state.currentCase = recommendedCase;
  resetEncounter();
  await startEncounter();
}

function closeReport() {
  elements.reportPanel.hidden = true;
  elements.resetBtn.focus();
}

function showFixtureInformation() {
  const shouldOpen = elements.caseReadiness.hidden;
  elements.caseReadiness.hidden = !shouldOpen;
  elements.infoBtn.setAttribute("aria-expanded", String(shouldOpen));
  if (!shouldOpen) return;
  elements.caseReadiness.scrollIntoView({ behavior: "smooth", block: "nearest" });
  elements.caseReadiness.focus({ preventScroll: true });
}

async function loadCases() {
  try {
    const payload = await api("/api/cases");
    if (!Array.isArray(payload.cases) || !payload.cases.length) throw new Error("사용 가능한 케이스가 없습니다.");
    state.cases = payload.cases;
    state.currentCase = payload.cases[0];
    state.ready = true;
  } catch (error) {
    state.loadError = `${error.message} CPX 서버를 먼저 실행하세요.`;
    console.error("CODE MEDI CPX API load failed", error);
  }
  renderReadiness();
  renderStatus();
}

elements.startBtn.addEventListener("click", startEncounter);
elements.resetBtn.addEventListener("click", resetEncounter);
elements.infoBtn.addEventListener("click", showFixtureInformation);
elements.caseSelect.addEventListener("change", () => {
  if (state.sessionId || state.pending) return;
  const selected = state.cases.find((caseItem) => caseItem.case_id === elements.caseSelect.value);
  if (!selected) return;
  state.currentCase = selected;
  renderReadiness();
  renderStatus();
});
elements.recordToggle.addEventListener("click", () => toggleRecord());
elements.closeRecordBtn.addEventListener("click", () => toggleRecord(false));
elements.finishBtn.addEventListener("click", () => toggleAssessment(true));
elements.closeAssessmentBtn.addEventListener("click", () => toggleAssessment(false));
elements.resumeEncounterBtn.addEventListener("click", () => toggleAssessment(false));
elements.assessmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await finishEncounter();
});
elements.closeReportBtn.addEventListener("click", closeReport);
elements.nextCaseBtn.addEventListener("click", startRecommendedCase);
elements.composer.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitQuestion(elements.freeQuestion.value);
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (!elements.recordModal.hidden) toggleRecord(false);
  else if (!elements.assessmentPanel.hidden) toggleAssessment(false);
  else if (!elements.reportPanel.hidden) closeReport();
});

renderConversation();
renderReadiness();
renderStatus();
loadCases();
