// Function to get a cookie by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Signup Form toasts
document.addEventListener('DOMContentLoaded', (event) => {
    const signupForm = document.getElementById('signupForm');
    const usernameInput = document.getElementById('signupUsername');
    const emailInput = document.getElementById('signupEmail');
    const password1Input = document.getElementById('signupPassword');
    const password2Input = document.getElementById('signupPassword2');
    const errorToast = new bootstrap.Toast(document.getElementById('errorToast'));
    const toastBody = document.getElementById('toastBody');

    signupForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form from submitting immediately

        // Check if the username is between 3 and 20 characters
        if (usernameInput.value.length < 3 || usernameInput.value.length > 20) {
            toastBody.textContent = 'Username must be between 3 and 20 characters.';
            errorToast.show();
            return;
        }

        // Check if the email includes an '@'
        if (!emailInput.value.includes('@')) {
            toastBody.textContent = 'Please include an "@" in the email address.';
            errorToast.show();
            return;
        }

        // Check if the password is at least 8 characters and includes a digit and a special character
        const password1 = password1Input.value;
        if (password1.length < 8 || !/\d/.test(password1) || !/[!@#$%^&*]/.test(password1)) {
            toastBody.textContent = 'Password must be at least 8 characters and include at least one digit and one special character.';
            errorToast.show();
            return;
        }

        // Check if the passwords match
        if (password1 !== password2Input.value) {
            toastBody.textContent = 'Passwords do not match.';
            errorToast.show();
            return;
        }

        // Get the CSRF token
        const csrftoken = getCookie('csrftoken');

        // Check if the username or email is already taken
        fetch('/check_username_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                username: usernameInput.value,
                email: emailInput.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.username_taken) {
                toastBody.textContent = 'Username is already taken.';
                errorToast.show();
            } else if (data.email_taken) {
                toastBody.textContent = 'Email is already taken.';
                errorToast.show();
            } else {
                // If username and email are not taken, submit the form
                fetch('/signup/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        username: usernameInput.value,
                        email: emailInput.value,
                        password1: password1Input.value,
                        password2: password2Input.value
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        // Handle error
                        toastBody.textContent = 'There was an error during the signup process. Please try again.';
                        errorToast.show();
                        console.error('Error:', response.statusText);
                    } else {
                        // Handle success
                        toastBody.textContent = 'Signup successful! Redirecting to home page...';
                        errorToast.show();
                        setTimeout(() => {
                            window.location.href = '/'; // Redirect to home page
                        }, 2000); // Redirect after 2 seconds
                    }
                })
                .catch(error => {
                    // Handle the error
                    toastBody.textContent = 'There was an error during the signup process. Please try again.';
                    errorToast.show();
                    console.error('Error:', error);
                });
            }
        })
        .catch(error => {
            // Handle the error
            toastBody.textContent = 'There was an error checking the username and email. Please try again.';
            errorToast.show();
            console.error('Error:', error);
        });
    });
});