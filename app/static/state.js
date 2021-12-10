function setState(state) {
    document.getElementById("status").textContent = state.status

    if (state.progress.value != null) {
        document.getElementById("progress").value = state.progress.value
        document.getElementById("progress").max = state.progress.max
    } else {
        document.getElementById("progress").removeAttribute("value")
    }

    if (state.end) {
        document.getElementById("progress").style.display = "none"
    }

    let message_link = document.getElementById("message_link");
    if (state.link.text != null) {
        message_link.textContent = state.link.text;
        message_link.href = state.link.href;
    } else {
        message_link.textContent = "";
        message_link.href = "";
    }

}

var socket = io();

socket.on('connect', function () {
    socket.emit('get_status')
})

socket.on('status', function (data) {
    console.log("DATA: ", data)
    setState(data)
})

socket.on('status_changed', function (data) {
    setState(data)
});