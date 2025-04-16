document.addEventListener('DOMContentLoaded', function () {
    var dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(function (dropdown) {
        dropdown.addEventListener('click', function () {
            var content = this.querySelector('.dropdown-content');
            content.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    window.addEventListener('click', function (event) {
        if (!event.target.matches('.dropbtn')) {
            dropdowns.forEach(function (dropdown) {
                var content = dropdown.querySelector('.dropdown-content');
                if (content.classList.contains('show')) {
                    content.classList.remove('show');
                }
            });
        }
    });
