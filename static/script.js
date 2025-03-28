
document.querySelector("#trimite").onclick = () => {
    const mesaj = document.querySelector("#mesaj").value;
    trimiteMesaj(mesaj);
};

document.querySelector("#btnVorbeste").onclick = () => {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'ro-RO';
    recognition.start();
    recognition.onresult = (event) => {
        const spokenText = event.results[0][0].transcript;
        document.querySelector("#mesaj").value = spokenText;
        trimiteMesaj(spokenText);
    };
};

function trimiteMesaj(text){
    fetch('/ai', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({mesaj: text})
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector("#rezultatAI").textContent = data.raspuns;
        const speech = new SpeechSynthesisUtterance(data.raspuns);
        speech.lang = 'ro-RO';
        window.speechSynthesis.speak(speech);
    });
}

setInterval(() => {
    fetch('/verifica-evenimente')
    .then(res => res.json())
    .then(data => {
        if (data.mesaj) {
            const speech = new SpeechSynthesisUtterance(data.mesaj);
            speech.lang = 'ro-RO';
            window.speechSynthesis.speak(speech);
            alert(data.mesaj);
        }
    });
}, 60000);
