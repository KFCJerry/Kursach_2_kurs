# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Animal, MedicalCard, Owner, AdoptionRequest, Donation
import re
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.json.ensure_ascii = False
CORS(app)
db.init_app(app)

# ============================================
# ВАЛИДАЦИЯ (п. 1.5 Требования к качеству данных)
# ============================================
def validate_phone(phone):
    """Проверка формата телефона +7(XXX)XXX-XX-XX"""
    pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'
    return bool(re.match(pattern, phone))

def validate_date(date_str):
    """Проверка формата даты ДД-ММ-ГГ"""
    pattern = r'^\d{2}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))

def validate_animal_type(animal_type):
    """Проверка справочника видов (п. 1.5)"""
    return animal_type in ['cat', 'dog']

# ============================================
# ПРОВЕРКА ПРАВ ДОСТУПА (п. 2.2 Матрица доступа)
# ============================================
def get_user_role():
    """Получение роли из заголовка запроса"""
    return request.headers.get('X-User-Role', 'guest')

def check_role(allowed_roles):
    """Декоратор для проверки прав доступа"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            user_role = get_user_role()
            if user_role not in allowed_roles:
                return jsonify({'error': f'Доступ запрещен. Требуется роль: {", ".join(allowed_roles)}'}), 403
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ============================================
# API МАРШРУТЫ
# ============================================

@app.route('/')
def index():
    return jsonify({'message': 'API приюта для животных работает!', 'version': '1.0'})

# ============================================
# 🐕 ЖИВОТНЫЕ (п. 2.2 Матрица доступа)
# ============================================

@app.route('/api/animals', methods=['GET'])
def get_animals():
    """Просмотр списка - доступно ВСЕМ (п. 2.2)"""
    animals = Animal.query.all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'type': a.type,
        'breed': a.breed,
        'gender': a.gender,
        'color': a.color,
        'status': a.status,
        'created_at': a.created_at.strftime('%d-%m-%y') if a.created_at else None
    } for a in animals])

@app.route('/api/animals/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    """Просмотр одного животного - доступно ВСЕМ"""
    animal = Animal.query.get_or_404(animal_id)
    return jsonify({
        'id': animal.id,
        'name': animal.name,
        'type': animal.type,
        'breed': animal.breed,
        'status': animal.status
    })

@app.route('/api/animals', methods=['POST'])
@check_role(['vet', 'admin'])
def create_animal():
    """Создание - только Ветеринар и Админ (п. 2.2)"""
    data = request.json
    
    # Валидация обязательных полей (п. 1.5, 4.3)
    if not data.get('name'):
        return jsonify({'error': 'Укажите кличку животного'}), 400
    
    if not data.get('type'):
        return jsonify({'error': 'Укажите вид животного'}), 400
    
    if not validate_animal_type(data.get('type')):
        return jsonify({'error': 'Вид животного должен быть: cat или dog'}), 400
    
    animal = Animal(
        name=data['name'],
        type=data['type'],
        breed=data.get('breed'),
        gender=data.get('gender'),
        color=data.get('color'),
        status='available'
    )
    
    db.session.add(animal)
    db.session.commit()
    
    return jsonify({'message': 'Животное добавлено', 'animal_id': animal.id}), 201

@app.route('/api/animals/<int:animal_id>', methods=['PUT'])
@check_role(['vet', 'admin'])
def update_animal(animal_id):
    """Редактирование - только Ветеринар и Админ (п. 2.2)"""
    animal = Animal.query.get_or_404(animal_id)
    data = request.json
    
    animal.name = data.get('name', animal.name)
    animal.type = data.get('type', animal.type)
    animal.status = data.get('status', animal.status)
    
    db.session.commit()
    return jsonify({'message': 'Данные обновлены'})

@app.route('/api/animals/<int:animal_id>', methods=['DELETE'])
@check_role(['admin'])
def delete_animal(animal_id):
    """Удаление - только Админ (п. 2.3 Критичная операция)"""
    animal = Animal.query.get_or_404(animal_id)
    db.session.delete(animal)
    db.session.commit()
    return jsonify({'message': 'Животное удалено из системы'}), 200

# ============================================
# 🏥 МЕДИЦИНСКАЯ КАРТА
# ============================================

@app.route('/api/animals/<int:animal_id>/medical', methods=['GET'])
@check_role(['owner', 'volunteer', 'curator', 'vet', 'admin'])
def get_medical_card(animal_id):
    """Просмотр мед.карты - всем кроме Гостя (п. 2.2)"""
    medical_card = MedicalCard.query.filter_by(animal_id=animal_id).first()
    
    if not medical_card:
        return jsonify({'error': 'Медицинская карта не найдена'}), 404
    
    return jsonify({
        'animal_id': medical_card.animal_id,
        'exam_date': medical_card.exam_date,
        'is_sterilized': medical_card.is_sterilized,
        'vaccination_date': medical_card.vaccination_date,
        'diagnosis': medical_card.diagnosis
    })

@app.route('/api/animals/<int:animal_id>/medical', methods=['POST', 'PUT'])
@check_role(['vet', 'admin'])
def save_medical_card(animal_id):
    """Создание/Обновление - только Ветеринар и Админ (п. 2.2)"""
    data = request.json
    
    if data.get('exam_date') and not validate_date(data.get('exam_date')):
        return jsonify({'error': 'Неверный формат даты. Пример: 15-01-25'}), 400
    
    medical_card = MedicalCard.query.filter_by(animal_id=animal_id).first()
    
    if medical_card:
        medical_card.exam_date = data.get('exam_date', medical_card.exam_date)
        medical_card.is_sterilized = data.get('is_sterilized', medical_card.is_sterilized)
        medical_card.diagnosis = data.get('diagnosis', medical_card.diagnosis)
    else:
        medical_card = MedicalCard(
            animal_id=animal_id,
            exam_date=data.get('exam_date'),
            is_sterilized=data.get('is_sterilized', False),
            diagnosis=data.get('diagnosis'),
            vet_id=data.get('vet_id')
        )
        db.session.add(medical_card)
    
    db.session.commit()
    return jsonify({'message': 'Медицинская карта сохранена'}), 201

# ============================================
# 📋 ЗАЯВКИ НА УСЫНОВЛЕНИЕ
# ============================================

@app.route('/api/adoptions', methods=['POST'])
@check_role(['guest', 'owner', 'volunteer'])
def create_adoption_request():
    """Создание заявки - Гость, Хозяин, Волонтер (п. 2.2)"""
    data = request.json
    
    if data.get('owner_phone') and not validate_phone(data.get('owner_phone')):
        return jsonify({'error': 'Неверный формат телефона. Пример: +7(999)000-00-00'}), 400
    
    adoption = AdoptionRequest(
        animal_id=data['animal_id'],
        owner_id=data.get('owner_id'),
        status='pending'
    )
    
    db.session.add(adoption)
    db.session.commit()
    
    return jsonify({'message': 'Заявка создана. Ожидайте решения куратора'}), 201

@app.route('/api/adoptions', methods=['GET'])
def get_adoption_requests():
    """Просмотр заявок - все роли"""
    requests = AdoptionRequest.query.all()
    return jsonify([{
        'id': r.id,
        'animal_id': r.animal_id,
        'status': r.status,
        'created_at': r.created_at.strftime('%d-%m-%y') if r.created_at else None
    } for r in requests])

@app.route('/api/adoptions/<int:request_id>/decision', methods=['PUT'])
@check_role(['curator'])
def decide_adoption(request_id):
    """Подтверждение заявки - только Куратор (п. 2.3 Критичная операция)"""
    adoption = AdoptionRequest.query.get_or_404(request_id)
    data = request.json
    
    if data.get('decision') not in ['approved', 'rejected']:
        return jsonify({'error': 'Решение должно быть: approved или rejected'}), 400
    
    adoption.status = data['decision']
    
    if data['decision'] == 'approved':
        adoption.contract_date = datetime.now().strftime('%d-%m-%y')
        adoption.animal.status = 'adopted'
    
    db.session.commit()
    return jsonify({'message': f'Заявка {data["decision"]}'})

# ============================================
# 👤 ПОЛЬЗОВАТЕЛИ
# ============================================

@app.route('/api/users/<int:user_id>/block', methods=['PATCH'])
@check_role(['admin'])
def block_user(user_id):
    """Блокировка пользователя - только Админ (п. 2.3 Критичная операция)"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.is_blocked = data.get('is_blocked', True)
    db.session.commit()
    
    return jsonify({'message': f'Пользователь {"заблокирован" if user.is_blocked else "разблокирован"}'})

# ============================================
# ЗАПУСК
# ============================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)