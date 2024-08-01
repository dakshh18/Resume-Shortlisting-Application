// password_toggle.js

document.addEventListener('DOMContentLoaded', function () {
    const loginEyeIcon = document.getElementById('login-eye-icon');
    const signupEyeIcon = document.getElementById('signup-eye-icon');

    // Function to toggle password visibility
    function togglePasswordVisibility(inputId, eyeIconId) {
        const input = document.getElementById(inputId);
        const eyeIcon = document.getElementById(eyeIconId);

        if (input && eyeIcon) {
            if (input.type === 'password') {
                input.type = 'text';
                eyeIcon.classList.remove('bi-eye-slash');
                eyeIcon.classList.add('bi-eye');
            } else {
                input.type = 'password';
                eyeIcon.classList.remove('bi-eye');
                eyeIcon.classList.add('bi-eye-slash');
            }
        }
    }

    // Add event listeners to eye icons
    if (loginEyeIcon) {
        loginEyeIcon.addEventListener('click', function () {
            togglePasswordVisibility('login-password', 'login-eye-icon');
        });
    }

    if (signupEyeIcon) {
        signupEyeIcon.addEventListener('click', function () {
            togglePasswordVisibility('signup-password', 'signup-eye-icon');
        });
    }
});

