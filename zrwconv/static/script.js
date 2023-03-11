function setup_buttons() {
    if (!navigator.clipboard) {
        let button = document.getElementById("copy")
        button.setAttribute("disabled", true)
        if (window.isSecureContext) {
            button.setAttribute(
                "title",
                "Ihr Browser unterstützt leider das Kopieren in die Zwischenablage nicht."
            )    
        } else {
            button.setAttribute(
                "title",
                "Für diese Funktion wird eine SSL-Verbindung benötigt. Bitte kontaktieren Sie Ihren Administrator."
            )
        }
    }
}

function download(event, download_name) {
    let html = document.getElementById('preview').innerHTML
    let blob = new Blob([html], { type: 'text/html' })
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
    let has_clipboard_write = !!navigator.clipboard.write
    let result
    if (has_clipboard_write) {
        result = navigator.clipboard.write([
            new ClipboardItem({
                'text/html': new Blob([html], { type: 'text/html' }),
                'text/plain': new Blob([html], { type: 'text/plain' }),
            })
        ])
    } else {
        result = navigator.clipboard.writeText(html)
    }
    result.then(
        () => {
            pulse(elem)
            let hint = document.getElementById("clipboard-hint")
            if (!has_clipboard_write) {
                hint.classList.remove("inactive")
            }
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
    }, { once: true })
}
