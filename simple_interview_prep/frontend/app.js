const API_BASE = "http://127.0.0.1:8001";

// DOM Views
const setupView = document.getElementById("setup-view");
const chatView = document.getElementById("chat-view");
const resultView = document.getElementById("result-view");

// DOM Elements
const startForm = document.getElementById("start-form");
const answerForm = document.getElementById("answer-form");
const roleSelect = document.getElementById("role");
const difficultySelect = document.getElementById("difficulty");
const questionsSelect = document.getElementById("questions");
const answerInput = document.getElementById("answer-input");
const messagesContainer = document.getElementById("messages-container");
const activeRoleBadge = document.getElementById("active-role");
const activeProgressBadge = document.getElementById("active-progress");
const scoreDisplay = document.getElementById("score-display");
const feedbackDisplay = document.getElementById("feedback-display");
const restartBtn = document.getElementById("restart-btn");
const startBtn = document.getElementById("start-btn");
const submitBtn = document.getElementById("submit-btn");

// App State
let currentInterviewId = null;
let currentRole = "";
let maxQuestions = 3;
let currentQuestionNum = 1;

// 1. START INTERVIEW HANDLER
startForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  currentRole = roleSelect.value;
  const difficulty = parseInt(difficultySelect.value);
  maxQuestions = parseInt(questionsSelect.value);

  startBtn.disabled = true;
  startBtn.textContent = "Initializing AI Interviewer...";

  try {
    const res = await fetch(`${API_BASE}/interviews/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        role_category: currentRole,
        difficulty_level: difficulty,
        max_questions: maxQuestions
      })
    });

    if (!res.ok) throw new Error("Failed to start interview session.");

    const data = await res.json();
    currentInterviewId = data.id;
    currentQuestionNum = 1;

    // Render Initial State
    activeRoleBadge.textContent = `Role: ${currentRole}`;
    activeProgressBadge.textContent = `Question 1 of ${maxQuestions}`;
    messagesContainer.innerHTML = "";
    
    appendMessage("assistant", data.first_question);

    // Switch View
    setupView.classList.add("hidden");
    chatView.classList.remove("hidden");
  } catch (err) {
    alert("Error starting interview: " + err.message);
  } finally {
    startBtn.disabled = false;
    startBtn.textContent = "Start Interview";
  }
});

// 2. SUBMIT ANSWER HANDLER
answerForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const answerText = answerInput.value.trim();
  if (!answerText || !currentInterviewId) return;

  // Append user answer immediately to UI
  appendMessage("user", answerText);
  answerInput.value = "";
  submitBtn.disabled = true;
  submitBtn.textContent = "AI is thinking...";

  try {
    const res = await fetch(`${API_BASE}/interviews/submit-answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interview_id: currentInterviewId,
        answer: answerText
      })
    });

    if (!res.ok) throw new Error("Failed to submit answer.");

    const data = await res.json();

    if (data.is_completed) {
      // Interview Completed ➔ Render Scorecard View
      scoreDisplay.textContent = data.score ? data.score.toFixed(1) : "8.0";
      feedbackDisplay.textContent = data.feedback || "Interview completed successfully.";

      chatView.classList.add("hidden");
      resultView.classList.remove("hidden");
    } else {
      // Display Next Question
      currentQuestionNum++;
      activeProgressBadge.textContent = `Question ${currentQuestionNum} of ${maxQuestions}`;
      appendMessage("assistant", data.next_question);
    }
  } catch (err) {
    alert("Error submitting answer: " + err.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Answer";
  }
});

// 3. RESTART HANDLER
restartBtn.addEventListener("click", () => {
  currentInterviewId = null;
  resultView.classList.add("hidden");
  setupView.classList.remove("hidden");
});

// HELPER: Append message bubble
function appendMessage(role, text) {
  const msgDiv = document.createElement("div");
  msgDiv.classList.add("msg", role === "user" ? "msg-user" : "msg-ai");
  msgDiv.textContent = text;
  messagesContainer.appendChild(msgDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
