function updateTables() {
    fetch('/api/tables')
        .then(response => response.json())
        .then(data => {
            for (let id in data) {
                let table = document.getElementById(`table-${id}`);
                if (table) {
                    table.classList.toggle('occupied', data[id].occupied);
                    table.classList.toggle('empty', !data[id].occupied);
                    table.querySelector('.people-count').textContent = `Kişi Sayısı: ${data[id].people}`;
                }
            }
        });
}

// Sayfa yüklendikçe 1 saniyede bir güncelleme yap.
setInterval(updateTables, 1000);
