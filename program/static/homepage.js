var side_bar_open = false;
function onSideBarClicked() {
    // check if side bar is already open or not and call respective functions
    if (side_bar_open) {
        closeSideBar()
        side_bar_open = false;
    }
    else {
        openSideBar()
        side_bar_open = true;
    }
}

// called when we open the main menu sidebar
function openSideBar() {
    var sidebar = document.getElementById("mainMenuNav");
    sidebar.style.width = "15%";
    // make the fontsize relative to the viewport
    sidebar.style.fontSize = "2vw"; 

    // move the sidebar button with the sidebar to the top right side
    var sideBarButton = document.getElementById("sideBarButton");
    sideBarButton.style.right = "0";
    sideBarButton.style.position = "absolute";

}

// called when we click the 'X' button on the main menu sidebar
function closeSideBar() {
    var sidebar = document.getElementById("mainMenuNav");
    sidebar.style.width = "0px";
    sidebar.style.fontSize = "0px";

    // move the sidebar button back to the top left of the screen
    var sideBarButton = document.getElementById("sideBarButton");
    sideBarButton.style.right = "-40";

}