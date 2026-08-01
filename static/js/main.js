function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    if (cookie) return cookie.split('=')[1];
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
}

document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('navToggle');
    const links = document.getElementById('navLinks');
    if (toggle && links) {
        toggle.addEventListener('click', () => links.classList.toggle('open'));
    }

    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity .5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
