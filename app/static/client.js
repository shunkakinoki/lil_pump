var el = x => document.getElementById(x);
var textData = "";

function showText(input) {
    textData = String(input.value);
    var reader = new FileReader();
    reader.onload = function (e) {
        el('text-input').src = e.target.result;
        el('text-input').className = '';
    }    
}

function analyze() {
    console.log(textData);
    
    el('analyze-button').innerHTML = 'Generating...';
    el('result-label').innerHTML = 'Please refresh and try again if nothing shows up after 2 minutes.'
    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `${response['result']}`;
        }
        el('analyze-button').innerHTML = 'Generate Tweet';
    }

    var fileData = new FormData();
    fileData.append('predict_text', textData);
    fileData.append('length', 30)
    xhr.send(fileData);
}