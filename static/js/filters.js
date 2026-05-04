document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchNPC');
    const categoryFilter = document.getElementById('filterCategory');
    const raceFilter = document.getElementById('filterRace');
    const npcCards = document.querySelectorAll('.npc-card');
    
    function filterNPCs() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedCategory = categoryFilter.value;
        const selectedRace = raceFilter.value;
        
        npcCards.forEach(card => {
            const name = card.dataset.name;
            const category = card.dataset.category;
            const race = card.dataset.race;
            
            const matchesSearch = name.includes(searchTerm) || searchTerm === '';
            const matchesCategory = selectedCategory === '' || category === selectedCategory;
            const matchesRace = selectedRace === '' || race === selectedRace;
            
            if (matchesSearch && matchesCategory && matchesRace) {
                card.style.display = 'block';
                card.classList.add('animate__animated', 'animate__fadeIn');
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    searchInput.addEventListener('input', filterNPCs);
    categoryFilter.addEventListener('change', filterNPCs);
    raceFilter.addEventListener('change', filterNPCs);
    
    // Сортировка NPC по важности (если нужно)
    function sortNPCs() {
        const container = document.getElementById('npcsContainer');
        const cards = Array.from(npcCards);
        
        cards.sort((a, b) => {
            const importanceA = parseInt(a.dataset.importance) || 0;
            const importanceB = parseInt(b.dataset.importance) || 0;
            return importanceB - importanceA;
        });
        
        cards.forEach(card => {
            container.appendChild(card);
        });
    }
});