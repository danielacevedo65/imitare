function getTwitter() {
    var user = document.getElementById("twitterUser").value;
    var amount = document.getElementById("amount").value;
    var which = document.getElementById("which").value;
    var result = "";
    var res = "";
    
    $.ajax({
        url: "/twitter",
        data:{"username":user, "amount":amount, "which":which, "result":result}, 
        beforeSend: function() { $("#loadGIF").show(); },
        complete: function() {$("#loadGIF").hide(); },
        error:function(xhr, status, error) {
            alert(xhr.responseText, status, error);
        },
        success:function(data) {
            for (key in data.result) {
                document.getElementById("display").innerHTML += '<br>';
                document.getElementById("display").innerHTML += data.result[key];
                document.getElementById("display").innerHTML += '<br>';
            }
        }
    });
}

function getYelp() {
    var amount = document.getElementById("Yamount").value;
    var which = document.getElementById("Ywhich").value;
    var result = "";
    var res = "";
    
    $.ajax({
        url: "/yelp",
        data:{"amount":amount, "which":which, "result":result}, 
        beforeSend: function() { $("#loadGIF").show(); },
        complete: function() {$("#loadGIF").hide(); },
        error:function(xhr, status, error) {
            alert(xhr.responseText, status, error);
        },
        success:function(data) {
            for (key in data.result) {
                document.getElementById("Ydisplay").innerHTML += '<br>';
                document.getElementById("Ydisplay").innerHTML += data.result[key];
                document.getElementById("Ydisplay").innerHTML += '<br>';
            }
        }
    });
}

function getGutenberg() {
    var amount = document.getElementById("Gamount").value;
    var which = document.getElementById("Gwhich").value;
    var result = "";
    var res = "";
    
    $.ajax({
        url: "/gutenberg",
        data:{"amount":amount, "which":which, "result":result}, 
        beforeSend: function() { $("#loadGIF").show(); },
        complete: function() {$("#loadGIF").hide(); },
        error:function(xhr, status, error) {
            alert(xhr.responseText, status, error);
        },
        success:function(data) {
            for (key in data.result) {
                document.getElementById("Gdisplay").innerHTML += '<br>';
                document.getElementById("Gdisplay").innerHTML += data.result[key];
                document.getElementById("Gdisplay").innerHTML += '<br>';
            }
        }
    });
}