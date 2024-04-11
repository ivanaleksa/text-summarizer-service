const BACK_URL = "http://127.0.0.1:8000/";
const FRONT_URL = "http://127.0.0.1:8543/";

function log_in_redirect(type) {
    fetch(BACK_URL + "get_user", {
        method: "GET",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
        }
    })
    .then(response => {
        if (response.status == 401) {
            window.location.replace(FRONT_URL + ((type === 2) ? "log_in.html" : "registrate.html"));
        } else {
            window.location.replace(FRONT_URL + "account.html");
        }
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });
}

function login_submit(type) {
    const data = {
        login: document.getElementById("login").value,
        password: document.getElementById("password").value
    };
    
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };
    
    fetch(BACK_URL + ((type === 1) ? "register" : "login"), options)
        .then(response => {
            if (!response.ok) {
                alert("You entered wrong data");
            } else {
                return response.json();
            }
        })
        .then(data => {
            localStorage.setItem("token", data["access_token"]);
            window.location.replace(FRONT_URL + "account.html");
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
}

