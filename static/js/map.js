document.addEventListener('DOMContentLoaded', function() {
    // Эмуляция интерактивной карты
    const mapMarkers = document.querySelectorAll('.map-marker');
    const locationButtons = document.querySelectorAll('[data-location]');
    
    function showLocationInfo(locationId) {
        // В реальном приложении здесь был бы AJAX запрос
        const locationData = {
            '1': {
                name: 'Город Белой Башни',
                description: 'Столица Альдерии, где расположен королевский дворец.',
                dangers: 'Коррупция, шпионы Культа Пустоты'
            },
            '2': {
                name: 'Лес Каменных Слёз',
                description: 'Зачарованный лес, где деревья плачут каменными слезами.',
                dangers: 'Ожившие статуи, туман забвения'
            },
            '3': {
                name: 'Замороженные Пики',
                description: 'Горный хребет, где время остановилось.',
                dangers: 'Ледяные элементали, лавины'
            }
        };
        
        const data = locationData[locationId];
        if (data) {
            const modalHtml = `
                <div class="modal fade" id="mapModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content bg-dark border-warning">
                            <div class="modal-header">
                                <h5 class="modal-title cinzel">${data.name}</h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <p>${data.description}</p>
                                <p><strong>Опасности:</strong> ${data.dangers}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Удаляем старый модал если есть
            const oldModal = document.getElementById('mapModal');
            if (oldModal) oldModal.remove();
            
            // Добавляем новый
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            const modal = new bootstrap.Modal(document.getElementById('mapModal'));
            modal.show();
        }
    }
    
    // Обработчики для маркеров
    mapMarkers.forEach(marker => {
        marker.addEventListener('click', function() {
            const locationId = this.dataset.location;
            showLocationInfo(locationId);
        });
    });
    
    // Обработчики для кнопок
    locationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const locationId = this.dataset.location;
            showLocationInfo(locationId);
        });
    });
    
    // Эффект наведения на маркеры
    mapMarkers.forEach(marker => {
        marker.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.5)';
            this.style.zIndex = '1000';
        });
        
        marker.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.zIndex = 'auto';
        });
    });
});