document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            if (this.getAttribute('href') === '#') {
                event.preventDefault();
            }
            navLinks.forEach(item => item.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
