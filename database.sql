-- ============================================
-- БАЗА ДАННЫХ "ПРИЮТ ДЛЯ ЖИВОТНЫХ"
-- По курсовой работе (разделы 1.3, 1.5, 2.1)
-- ============================================

-- 1. Таблица ПОЛЬЗОВАТЕЛИ (все роли в одной таблице)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,                    -- ФИО (п. 1.3)
    email TEXT UNIQUE,                          -- Email
    phone TEXT NOT NULL,                        -- Телефон (п. 1.5 Обязательное)
    role TEXT NOT NULL CHECK (role IN (         -- Роль (п. 2.1)
        'guest',      -- Гость
        'owner',      -- Хозяин
        'volunteer',  -- Волонтер
        'curator',    -- Куратор
        'vet',        -- Ветеринар
        'admin'       -- Администратор
    )),
    education TEXT,                             -- Образование (для ветеринара)
    experience TEXT,                            -- Опыт работы (для куратора)
    is_blocked INTEGER DEFAULT 0,               -- Блокировка (п. 2.3)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Таблица ЖИВОТНЫЕ (п. 1.3)
CREATE TABLE IF NOT EXISTS animals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                         -- Кличка (ОБЯЗАТЕЛЬНО п. 1.5)
    type TEXT NOT NULL CHECK (type IN (         -- Вид (справочник п. 1.5)
        'cat', 
        'dog'
    )),
    breed TEXT,                                 -- Порода
    gender TEXT CHECK (gender IN ('male', 'female')),  -- Пол
    color TEXT,                                 -- Окрас
    photo_url TEXT,                             -- Фото
    status TEXT DEFAULT 'available' CHECK (status IN (
        'available',    -- Свободен
        'adopted',      -- Усыновлен
        'treatment'     -- На лечении
    )),
    curator_id INTEGER,                         -- Куратор (связь п. 1.3)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Дата поступления (п. 1.4)
    FOREIGN KEY (curator_id) REFERENCES users(id)
);

-- 3. Таблица МЕДИЦИНСКАЯ КАРТА (п. 1.3)
CREATE TABLE IF NOT EXISTS medical_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER UNIQUE NOT NULL,          -- Животное (связь п. 1.3)
    vet_id INTEGER,                             -- Ветеринар (связь п. 1.3)
    exam_date TEXT,                             -- Дата осмотра (п. 1.5 Формат ДД-ММ-ГГ)
    is_sterilized INTEGER DEFAULT 0,            -- Стерилизация (п. 1.3)
    vaccination_date TEXT,                      -- Дата прививки
    diagnosis TEXT,                             -- Диагноз
    weight REAL,                                -- Вес
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (vet_id) REFERENCES users(id)
);

-- 4. Таблица ХОЗЯЕВА (п. 1.3)
CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,                    -- ФИО (п. 1.3)
    phone TEXT NOT NULL,                        -- Телефон (ОБЯЗАТЕЛЬНО п. 1.5)
    email TEXT,                                 -- Email (п. 1.3)
    address TEXT                                -- Место проживания (п. 1.3)
);

-- 5. Таблица ЗАЯВКИ НА УСЫНОВЛЕНИЕ (п. 2.2)
CREATE TABLE IF NOT EXISTS adoption_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,                 -- Животное
    owner_id INTEGER NOT NULL,                  -- Хозяин
    curator_id INTEGER,                         -- Куратор (п. 2.3)
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending',    -- На рассмотрении
        'approved',   -- Одобрено
        'rejected'    -- Отказано
    )),
    contract_date TEXT,                         -- Дата договора
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (owner_id) REFERENCES owners(id),
    FOREIGN KEY (curator_id) REFERENCES users(id)
);

-- 6. Таблица ПОЖЕРТВОВАНИЯ (п. 1.3)
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER,                       -- Волонтер (п. 1.3)
    donor_name TEXT,                            -- От кого ФИО
    type TEXT CHECK (type IN ('money', 'food')), -- Тип (п. 1.3)
    amount REAL,                                -- Сумма/количество
    donation_date TEXT,                         -- Дата
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES users(id)
);

-- ============================================
-- ТЕСТОВЫЕ ДАННЫЕ (для демонстрации)
-- ============================================

-- Пользователи (п. 2.1 Роли)
INSERT OR IGNORE INTO users (full_name, email, phone, role, education, experience) VALUES
('Администратор', 'admin@shelter.ru', '+7(999)000-00-00', 'admin', NULL, NULL),
('Куратор Иванова', 'curator@shelter.ru', '+7(999)111-11-11', 'curator', NULL, '5 лет'),
('Ветеринар Петров', 'vet@shelter.ru', '+7(999)222-22-22', 'vet', 'Ветеринарный университет', NULL),
('Волонтер Сидоров', 'volunteer@shelter.ru', '+7(999)333-33-33', 'volunteer', NULL, NULL);

-- Животные (п. 1.3, 1.5)
INSERT OR IGNORE INTO animals (name, type, breed, gender, color, status, curator_id) VALUES
('Барсик', 'cat', 'Дворовая', 'male', 'Рыжий', 'available', 2),
('Рекс', 'dog', 'Овчарка', 'male', 'Черный', 'adopted', 2),
('Мурка', 'cat', 'Британская', 'female', 'Серый', 'treatment', 2);

-- Хозяева (п. 1.3)
INSERT OR IGNORE INTO owners (full_name, phone, email, address) VALUES
('Смирнов Петр', '+7(999)444-44-44', 'smirnov@mail.ru', 'г. Москва, ул. Ленина 1'),
('Козлова Мария', '+7(999)555-55-55', 'kozlova@mail.ru', 'г. Москва, ул. Мира 5');

-- Заявки (п. 2.2, 2.3)
INSERT OR IGNORE INTO adoption_requests (animal_id, owner_id, curator_id, status) VALUES
(2, 1, 2, 'approved'),   -- Рекс усыновлен
(1, 2, NULL, 'pending'); -- Барсик на рассмотрении

-- Медицинские карты (п. 1.3)
INSERT OR IGNORE INTO medical_cards (animal_id, vet_id, exam_date, is_sterilized, vaccination_date, diagnosis) VALUES
(1, 3, '15-01-25', 1, '10-01-25', 'Здоров'),
(2, 3, '10-01-25', 1, '05-01-25', 'Здоров'),
(3, 3, '20-01-25', 0, NULL, 'Требует лечения');

-- Пожертвования (п. 1.3)
INSERT OR IGNORE INTO donations (volunteer_id, donor_name, type, amount, donation_date) VALUES
(4, 'Волонтеров Олег', 'money', 5000, '20-01-25'),
(4, 'Волонтеров Олег', 'food', 10, '21-01-25');
