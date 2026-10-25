/**
 * CareerPilot AI — Client-side Interactivity & Chart Renderers
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // 2. Drag & Drop File Upload UI enhancement
  const dropzone = document.getElementById("resume-dropzone");
  const fileInput = document.getElementById("resume_file");
  const fileInfo = document.getElementById("selected-file-info");
  const fileNameDisplay = document.getElementById("selected-file-name");

  if (dropzone && fileInput) {
    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("border-primary", "bg-light");
    });

    dropzone.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropzone.classList.remove("border-primary", "bg-light");
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("border-primary", "bg-light");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        updateSelectedFileInfo();
      }
    });

    fileInput.addEventListener("change", updateSelectedFileInfo);

    function updateSelectedFileInfo() {
      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (fileNameDisplay) {
          fileNameDisplay.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
        }
        if (fileInfo) fileInfo.classList.remove("d-none");
      }
    }
  }

  // 3. Interactive Roadmap Toggle via AJAX
  const roadmapToggles = document.querySelectorAll(".roadmap-toggle-btn");
  roadmapToggles.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const form = this.closest("form");
      const url = form.action;
      const csrfToken = form.querySelector('input[name="csrf_token"]')?.value;

      fetch(url, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrfToken || "",
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            window.location.reload();
          }
        })
        .catch(() => {
          form.submit();
        });
    });
  });

  // 4. Interview Practice Question Switcher
  const questionSelectors = document.querySelectorAll(".select-interview-q");
  const activeQuestionDisplay = document.getElementById("active-question-text");
  const activeQuestionCategory = document.getElementById("active-question-category");
  const activeQuestionOutline = document.getElementById("active-question-outline");
  const hiddenQText = document.getElementById("question_text");
  const hiddenConcepts = document.getElementById("key_concepts");
  const hiddenCategory = document.getElementById("category");

  questionSelectors.forEach((btn) => {
    btn.addEventListener("click", function () {
      const qText = this.getAttribute("data-question");
      const qCat = this.getAttribute("data-category");
      const qOutline = this.getAttribute("data-outline");
      const qConcepts = this.getAttribute("data-concepts");

      if (activeQuestionDisplay) activeQuestionDisplay.textContent = qText;
      if (activeQuestionCategory) activeQuestionCategory.textContent = qCat;
      if (activeQuestionOutline) activeQuestionOutline.textContent = qOutline;

      if (hiddenQText) hiddenQText.value = qText;
      if (hiddenCategory) hiddenCategory.value = qCat;
      if (hiddenConcepts) hiddenConcepts.value = qConcepts;

      questionSelectors.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
    });
  });
});

/**
 * Chart.js Helper: Render Radar Chart for Score Breakdown
 */
function renderScoreRadarChart(canvasId, labels, scores, maxScores) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return;

  const normalized = scores.map((s, i) => Math.round((s / maxScores[i]) * 100));

  new Chart(canvas, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Your Score (%)",
          data: normalized,
          backgroundColor: "rgba(37, 99, 235, 0.2)",
          borderColor: "#2563EB",
          pointBackgroundColor: "#2563EB",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#2563EB",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { stepSize: 20 },
          pointLabels: {
            font: { size: 12, family: "'Inter', sans-serif" },
            color: "#334155",
          },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

/**
 * Chart.js Helper: Render Match Doughnut Chart
 */
function renderMatchDoughnutChart(canvasId, matchPct) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === "undefined") return;

  const remaining = 100 - matchPct;

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: ["Matched", "Gap"],
      datasets: [
        {
          data: [matchPct, remaining],
          backgroundColor: ["#2563EB", "#E2E8F0"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "75%",
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true },
      },
    },
  });
}
