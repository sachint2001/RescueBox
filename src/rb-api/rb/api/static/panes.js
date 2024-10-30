function initPanes() {
    // https://split.js.org/
    Split(['#left-pane', '#right-pane'], {
        sizes: [20, 80],
        gutterSize: 5,
        cursor: 'row-resize',
        minSize: 250,
    });

}

document.addEventListener("DOMContentLoaded", initPanes);