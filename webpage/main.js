const BACK_URL = "http://127.0.0.1:8000/";
const FRONT_URL = "http://127.0.0.1:8543/";

function log_in_redirect(type) {
    fetch(BACK_URL + "get_user/", {
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

function logout()
{
    localStorage.removeItem("token");
    window.location.replace(FRONT_URL + "/");
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
    
    fetch(BACK_URL + ((type === 1) ? "register/" : "login/"), options)
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

function personal_account()
{
    fetch(BACK_URL + "get_user/", {
        method: "GET",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
        }
    })
    .then(response => {
        if (response.status == 401) {
            window.location.replace(FRONT_URL + "log_in.html");
        } else {
            return response.json();
        }
    })
    .then(user_data => {
        document.getElementById("user_login").appendChild(document.createTextNode(user_data["login"]));
        document.getElementById("user_balance").appendChild(document.createTextNode(user_data["balance"]));
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });


    fetch(BACK_URL + "history/", {
        method: "GET",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
        }
    })
    .then(response => {
        if (response.status == 401) {
            window.location.replace(FRONT_URL + "log_in.html");
        } else {
            return response.json();
        }
    })
    .then(transaction_data => {
        // Создание таблицы и заполнение данными
        const table = document.createElement("table");
        table.style.border = "3px solid #245488";
        table.style.borderCollapse = "collapse";
        const headerRow = table.insertRow();
        const headers = ["Input Text", "Output Text", "Cost"];
        
        // Создание заголовков столбцов
        headers.forEach(headerText => {
            const header = document.createElement("th");
            header.textContent = headerText;
            header.style.border = "3px solid #245488";
            header.style.borderCollapse = "collapse";
            headerRow.appendChild(header);
        });
        
        // Заполнение данными
        transaction_data.forEach(transaction => {
            const row = table.insertRow();
            const cellInputText = row.insertCell();
            const cellOutputText = row.insertCell();
            const cellCost = row.insertCell();
            cellInputText.style.border = "3px solid #245488";
            cellInputText.style.borderCollapse = "collapse";
            cellOutputText.style.border = "3px solid #245488";
            cellOutputText.style.borderCollapse = "collapse";
            cellCost.style.border = "3px solid #245488";
            cellCost.style.borderCollapse = "collapse";
            cellInputText.textContent = transaction.input_text;
            cellOutputText.textContent = transaction.output_text;
            cellCost.textContent = transaction.cost;
        });
        
        document.getElementById("transaction_history").appendChild(table);
    })
    .catch(error => {
        console.error('There was a problem with your fetch operation:', error);
    });
}

function increase_balance()
{
    let amount = document.getElementById("increase").value;

    fetch(BACK_URL + `balance/increase?amount=${amount}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
        }
    })
    .then(response => {
        if (response.status == 401) {
            window.location.replace(FRONT_URL + "log_in.html");
        } else {
            window.location.reload();
        }
    });
}

function prediction()
{
    const data = {
        input_text: document.getElementById("prediction_text").value,
        min_len: parseInt(document.getElementById("min_len").value),
        max_len: parseInt(document.getElementById("max_len").value)
    };

    fetch(BACK_URL + "predict/", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.status === 401) {
            window.location.replace(FRONT_URL + "log_in.html");
        } else {
            window.location.reload();
        }
        if (response.status === 400){
            alert("You don't have enough coins");
        }
    })
}
