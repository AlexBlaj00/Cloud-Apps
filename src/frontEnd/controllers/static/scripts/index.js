function open_menu() {
    document.getElementById("side_menu").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
  }
  
  function close_menu() {
    document.getElementById("side_menu").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
    //document.getElementsByClassName("dropdown-side-btn").disabled = true;
  }
  
  function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
      x.className += " responsive";
    } else {
      x.className = "topnav";
    }
  }
