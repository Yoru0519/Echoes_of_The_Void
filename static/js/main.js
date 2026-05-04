// Инициализация всплывающих подсказок
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех Bootstrap компонентов
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Система спойлеров
    document.querySelectorAll('.spoiler').forEach(function(spoiler) {
        spoiler.addEventListener('click', function() {
            if (this.style.color === 'black' || this.style.color === 'rgb(0, 0, 0)') {
                this.style.color = 'white';
                this.classList.add('bg-danger', 'p-2');
                this.innerHTML = '⚠️ ' + this.innerHTML;
            }
        });
    });
    
    // Анимация появления элементов
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .accordion-item').forEach(el => {
        observer.observe(el);
    });
});

// Функция для динамической загрузки контента
async function loadContent(url, containerId) {
    try {
        const response = await fetch(url);
        const html = await response.text();
        document.getElementById(containerId).innerHTML = html;
    } catch (error) {
        console.error('Ошибка загрузки:', error);
    }
}