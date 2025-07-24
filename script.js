document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("theme-toggle");
    const themeLabel = document.getElementById("theme-label");
    const predictionForm = document.getElementById("predictionForm");
    const resultCard = document.getElementById("result-card");
    const resultText = document.getElementById("result");
    const suggestionsText = document.getElementById("suggestions");

    // Load saved theme
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.checked = true;
        themeLabel.innerText = "🌙 Dark Mode";
    }

    // Toggle Dark Mode
    themeToggle.addEventListener("change", function () {
        if (themeToggle.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("theme", "dark");
            themeLabel.innerText = "🌙 Dark Mode";
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("theme", "light");
            themeLabel.innerText = "🌞 Light Mode";
        }
    });

    // Form Submission Handler
    predictionForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        // Get user input
        const features = [
            parseFloat(document.getElementById("age").value),
            parseFloat(document.getElementById("sex").value),
            parseFloat(document.getElementById("bmi").value),
            parseFloat(document.getElementById("bp").value),
            parseFloat(document.getElementById("s1").value),
            parseFloat(document.getElementById("s2").value),
            parseFloat(document.getElementById("s3").value),
            parseFloat(document.getElementById("s4").value),
            parseFloat(document.getElementById("s5").value),
            parseFloat(document.getElementById("s6").value),
        ];

        // Send request to Flask API
        try {
            const response = await fetch("http://127.0.0.1:5000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ features }),
            });

            const data = await response.json();
            displayResult(data.prediction);
        } catch (error) {
            resultText.innerHTML = "⚠️ Error in prediction. Please try again.";
            resultCard.classList.remove("hidden");
        }
    });

    function displayResult(prediction) {
        resultText.innerHTML = `Predicted Diabetes Progression: <strong>${prediction.toFixed(2)}</strong>`;
        let suggestion = "";

        if (prediction < 100) {
            suggestion = "✅ Low Risk: Maintain a balanced diet and exercise regularly!";
        } else if (prediction >= 100 && prediction < 140) {
            suggestion = "⚠️ Moderate Risk: Monitor your sugar intake and consult a doctor if necessary.";
        } else {
            suggestion = "🚨 High Risk: Consider consulting a healthcare provider for proper management.";
        }

        suggestionsText.innerHTML = suggestion;
        resultCard.classList.remove("hidden");
    }
});
