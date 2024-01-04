function registerUser() {
  const username = document.getElementById('username').value;
  // const password = document.getElementById('password').value;
  // const password = document.getElementById('password').value;
  // const password = document.getElementById('password').value;



  // Create a JSON object with registration data
  const registrationData = {
    username: username,
    password: password
  };

  // Use fetch API to make a POST request to the registration endpoint
  fetch('http://127.0.0.1:8000/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(registrationData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Registration successful:', data);
  })
  .catch(error => {
    console.error('Error during registration:', error);
  });
}

function loginUser() {
  const loginUsername = document.getElementById('loginUsername').value;
  const loginPassword = document.getElementById('loginPassword').value;

  // Create a JSON object with login data
  const loginData = {
    username: loginUsername,
    password: loginPassword
  };

  // Use fetch API to make a POST request to the login endpoint
  fetch('http://127.0.0.1:8000/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(loginData)
  })
  .then(response => response.json())
  .then(data => {
    console.log('Login successful:', data);
  })
  .catch(error => {
    console.error('Error during login:', error);
  });
}
