const canvas = document.getElementById("waveCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let waveOffset = 0;

function drawWave(color, amplitude, wavelength, yOffset) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.shadowColor = color;
    ctx.shadowBlur = 20;

    for (let x = 0; x < canvas.width; x++) {
        let y = amplitude * Math.sin((x + waveOffset) * wavelength) + yOffset;
        ctx.lineTo(x, y);
    }

    ctx.stroke();
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawWave("#ff00ff", 40, 0.01, canvas.height / 2);
    drawWave("#a855f7", 30, 0.015, canvas.height / 2 + 40);
    drawWave("#d946ef", 50, 0.008, canvas.height / 2 - 40);

    waveOffset += 2;

    requestAnimationFrame(animate);
}

animate();

function analyzeFile() {
    const fileInput = document.getElementById("fileInput");
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0) {
        resultDiv.innerHTML = "Please upload a file.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    resultDiv.innerHTML = `
        <div class="loader"></div>
        <p>Analyzing...</p>
    `;

    fetch("/analyze", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const reader = new FileReader();
        reader.onload = function(e) {
            resultDiv.innerHTML = `
                <div class="result-container">
                    <img src="${e.target.result}" class="preview">
                    <div class="analysis">
                        <h2>${data.result}</h2>
                        <div class="percentage">${data.confidence}%</div>
                    </div>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    });
}
