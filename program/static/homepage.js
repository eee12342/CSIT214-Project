var side_bar_open
function onSideBarClicked() {
    if (side_bar_open) {
        openSideBar()
        side_bar_open = false;
    }
    else {
        closeSideBar()
        side_bar_open = true;
    }
}

// called when we open the main menu sidebar
function openSideBar() {
    var sidebar = document.getElementById("mainMenuNav");
    sidebar.style.width = "15%";
    sidebar.style.fontSize = "20px";

    // hide the button to open the side bar
    document.getElementById("sideBarButtonOpen").style.visibilty = "hidden";
}

// called when we click the 'X' button on the main menu sidebar
function closeSideBar() {
    var sidebar = document.getElementById("mainMenuNav");
    sidebar.style.width = "0px";
    sidebar.style.fontSize = "0px";

    // reveal the open side bar button again
    document.getElementById("sideBarButtonClose").style.visibility = "visible";
}