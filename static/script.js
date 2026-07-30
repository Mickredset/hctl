// static/script.js
document.addEventListener('DOMContentLoaded', function () {
    const houseTreeDiv = document.getElementById('houseTree');
    const residentsListDiv = document.getElementById('residentsList');

    // --- Загрузка данных при открытии страницы ---
    loadHouseStructure();

    // --- Функции для взаимодействия с сервером ---
    async function apiCall(endpoint, method, data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (data) {
            options.body = JSON.stringify(data);
        }
        const response = await fetch(`/api${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    async function loadHouseStructure() {
        try {
            const structure = await apiCall('/structure', 'GET');
            renderHouseTree(structure);
        } catch (error) {
            console.error('Ошибка загрузки структуры дома:', error);
            alert('Ошибка загрузки данных.');
        }
    }

    async function addFloor() {
        const floorNumInput = document.getElementById('floorNumberInput');
        const floorNum = parseInt(floorNumInput.value);
        if (isNaN(floorNum)) {
            alert('Введите корректный номер этажа.');
            return;
        }
        try {
            await apiCall('/floors', 'POST', { floor_number: floorNum });
            floorNumInput.value = ''; // Очистить поле ввода
            loadHouseStructure(); // Перезагрузить дерево
        } catch (error) {
            console.error('Ошибка добавления этажа:', error);
            alert('Ошибка добавления этажа.');
        }
    }

    async function addRoom() {
        const floorNumInput = document.getElementById('addRoomFloorNumberInput');
        const roomNumInput = document.getElementById('addRoomNumberInput');
        const roomTypeInput = document.getElementById('addRoomTypeInput');

        const floorNum = parseInt(floorNumInput.value);
        const roomNum = roomNumInput.value.trim();
        const roomType = roomTypeInput.value.trim() || 'Обычная';

        if (isNaN(floorNum) || !roomNum) {
            alert('Введите корректные номер этажа и номер комнаты.');
            return;
        }
        try {
            await apiCall('/rooms', 'POST', { floor_number: floorNum, room_number: roomNum, room_type: roomType });
            floorNumInput.value = '';
            roomNumInput.value = '';
            roomTypeInput.value = 'Обычная'; // Сбросить к значению по умолчанию
            loadHouseStructure(); // Перезагрузить дерево
        } catch (error) {
            console.error('Ошибка добавления комнаты:', error);
            alert('Ошибка добавления комнаты.');
        }
    }

    async function createUser() {
        const nameInput = document.getElementById('userNameInput');
        const ageInput = document.getElementById('userAgeInput');
        const emailInput = document.getElementById('userEmailInput');

        const name = nameInput.value.trim();
        const ageStr = ageInput.value.trim();
        const email = emailInput.value.trim();

        if (!name) {
            alert('Имя пользователя обязательно.');
            return;
        }
        const age = ageStr ? parseInt(ageStr) : null;
        if (ageStr && isNaN(age)) {
            alert('Введите корректный возраст.');
            return;
        }

        try {
            await apiCall('/users', 'POST', { name: name, age: age, email: email });
            nameInput.value = '';
            ageInput.value = '';
            emailInput.value = '';
            // Сообщение пользователю об успехе можно добавить, если нужно
        } catch (error) {
            console.error('Ошибка создания пользователя:', error);
            alert('Ошибка создания пользователя.');
        }
    }

    async function assignUserToRoom() {
        const userIdInput = document.getElementById('assignUserIdInput');
        const floorNumInput = document.getElementById('assignFloorNumberInput');
        const roomNumInput = document.getElementById('assignRoomNumberInput');

        const userId = parseInt(userIdInput.value);
        const floorNum = parseInt(floorNumInput.value);
        const roomNum = roomNumInput.value.trim();

        if (isNaN(userId) || isNaN(floorNum) || !roomNum) {
            alert('Введите корректные ID пользователя, номер этажа и номер комнаты.');
            return;
        }
        try {
            await apiCall('/assign', 'POST', { user_id: userId, floor_number: floorNum, room_number: roomNum });
            userIdInput.value = '';
            floorNumInput.value = '';
            roomNumInput.value = '';
            loadHouseStructure(); // Обновить дерево, чтобы отразить изменения
            // Сообщение пользователю об успехе можно добавить, если нужно
        } catch (error) {
            console.error('Ошибка назначения пользователя:', error);
            alert('Ошибка назначения пользователя. Возможно, пользователь или комната не существуют.');
        }
    }

    // --- Функции для отображения данных ---
    function renderHouseTree(structure) {
        houseTreeDiv.innerHTML = ''; // Очистить предыдущее содержимое

        for (const [floorNum, rooms] of Object.entries(structure)) {
            const floorDiv = document.createElement('div');
            floorDiv.className = 'floor-item';
            floorDiv.textContent = `Этаж ${floorNum}`;
            houseTreeDiv.appendChild(floorDiv);

            const roomsContainer = document.createElement('div');
            roomsContainer.className = 'rooms-container';
            houseTreeDiv.appendChild(roomsContainer);

            for (const [roomNum, roomData] of Object.entries(rooms)) {
                const roomDiv = document.createElement('div');
                roomDiv.className = 'room-item';
                roomDiv.textContent = `Комната ${roomNum} (${roomData.type}), Жильцы: ${roomData.residents.length}`;
                roomDiv.onclick = () => showResidents(floorNum, roomNum, roomData.residents);
                roomsContainer.appendChild(roomDiv);
            }
        }
    }

    function showResidents(floorNum, roomNum, residents) {
        // Снять выделение с других комнат
        document.querySelectorAll('.room-item').forEach(r => r.classList.remove('selected'));
        // Выделить текущую комнату
        event.target.classList.add('selected');

        residentsListDiv.innerHTML = `<h3>Жильцы комнаты ${roomNum} (этаж ${floorNum})</h3>`;
        if (residents.length > 0) {
            const ul = document.createElement('ul');
            residents.forEach(residentName => {
                const li = document.createElement('li');
                li.textContent = residentName;
                ul.appendChild(li);
            });
            residentsListDiv.appendChild(ul);
        } else {
            residentsListDiv.innerHTML += '<p>В этой комнате никто не проживает.</p>';
        }
    }

    // --- Привязка обработчиков к кнопкам ---
    document.getElementById('addFloorBtn').addEventListener('click', addFloor);
    document.getElementById('addRoomBtn').addEventListener('click', addRoom);
    document.getElementById('createUserBtn').addEventListener('click', createUser);
    document.getElementById('assignUserBtn').addEventListener('click', assignUserToRoom);
});