function download(event, download_name) {
    let html = document.getElementById('preview').innerHTML
    let blob = new Blob([html], {type: 'text/html'})
    let a = document.createElement('a')
    a.download = download_name
    a.href = window.URL.createObjectURL(blob)
    try {
        a.click()
        pulse(event.currentTarget)
    } finally {
        window.URL.revokeObjectURL(a.href)
    }
}

function copy(event) {
    let elem = event.currentTarget
    let html = document.getElementById('preview').innerHTML
    navigator.clipboard.writeText(html).then(
        () => {
            pulse(elem)
        },
        (reason) => {
            alert('Fehler beim Kopieren in die Zwischenablage:\n\n' + reason)
        },
    )
}

function pulse(elem) {
    elem.classList.add('pulse')
    elem.addEventListener('transitionend', () => {
        elem.classList.remove('pulse')
    }, {once: true})
}