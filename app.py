from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from functools import wraps
import hashlib
import secrets

app = Flask(__name__)
CORS(app)

# Configuração de pastas
DATA_DIR = os.path.dirname(__file__)

# Arquivos de banco de dados
USUARIO_FILE = os.path.join(DATA_DIR, 'usuarios.json')
PETS_FILE = os.path.join(DATA_DIR, 'pets.json')
ADOCAO_FILE = os.path.join(DATA_DIR, 'adocao.json')

# Inicializar arquivos se não existirem
def init_db():
    if not os.path.exists(USUARIO_FILE):
        save_json(USUARIO_FILE, {})
    if not os.path.exists(PETS_FILE):
        save_json(PETS_FILE, [])
    if not os.path.exists(ADOCAO_FILE):
        save_json(ADOCAO_FILE, [])

# Funções auxiliares para JSON
def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if 'users' in filepath else []

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Hash de senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# Token de autenticação
def generate_token():
    return secrets.token_hex(32)

# Decorador para autenticação
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        users = load_json(USUARIO_FILE)
        
        # Procura o usuário com este token
        for user_id, user_data in users.items():
            if user_data.get('token') == token:
                request.current_user = user_data
                request.current_user_id = user_id
                return f(*args, **kwargs)
        
        return jsonify({'error': 'Não autorizado'}), 401
    return decorated

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/registro', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validações
    if not data.get('email') or not data.get('senha') or not data.get('nome'):
        return jsonify({'error': 'Email, senha e nome são obrigatórios'}), 400
    
    if len(data.get('senha', '')) < 6:
        return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
    
    users = load_json(USUARIO_FILE)
    
    # Verificar se email já existe
    for user_data in users.values():
        if user_data.get('email') == data['email']:
            return jsonify({'error': 'Email já cadastrado'}), 409
    
    # Criar novo usuário
    user_id = str(int(max([int(k) for k in users.keys()], default=0)) + 1)
    user = {
        'id': user_id,
        'nome': data['nome'],
        'email': data['email'],
        'senha': hash_password(data['senha']),
        'telefone': data.get('phone', ''),
        'aceitar_whatsapp': data.get('aceitar_whatsapp', False),
        'aceitar_ligacoes': data.get('aceitar_ligacoes', False),
        'token': generate_token(),
        'created_at': datetime.now().isoformat()
    }
    
    users[user_id] = user
    save_json(USUARIO_FILE, users)
    
    return jsonify({
        'message': 'Usuário criado com sucesso',
        'user': {
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'token': user['token']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('senha'):
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    users = load_json(USUARIO_FILE)
    
    for user_id, user_data in users.items():
        if user_data['email'] == data['email']:
            if verify_password(data['senha'], user_data['senha']):
                token = generate_token()
                user_data['token'] = token
                users[user_id] = user_data
                save_json(USUARIO_FILE, users)
                
                return jsonify({
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': user_data['id'],
                        'nome': user_data['nome'],
                        'email': user_data['email'],
                        'token': token
                    }
                }), 200
            else:
                return jsonify({'error': 'Senha incorreta'}), 401
    
    return jsonify({'error': 'Usuário não encontrado'}), 404

@app.route('/api/auth/profile', methods=['GET'])
@require_auth
def get_profile():
    return jsonify(request.current_user), 200

# ==================== ROTAS DE PETS ====================

@app.route('/api/pets', methods=['GET'])
def get_pets():
    pets = load_json(PETS_FILE)
    
    # Filtros
    pet_tipo = request.args.get('tipo', '')
    idade = request.args.get('idade', '')
    porte = request.args.get('porte', '')
    localizacao = request.args.get('localizacao', '')
    buscar_nome = request.args.get('buscar_nome', '').lower()
    
    filtered_pets = []
    for pet in pets:
        if pet_tipo and pet.get('tipo') != pet_tipo:
            continue
        if idade and pet.get('idade') != idade:
            continue
        if porte and pet.get('porte') != porte:
            continue
        if localizacao and localizacao.lower() not in pet.get('localizacao', '').lower():
            continue
        if buscar_nome and buscar_nome not in pet.get('nome', '').lower():
            continue
        
        filtered_pets.append(pet)
    
    return jsonify({
        'pets': filtered_pets,
        'total': len(filtered_pets)
    }), 200

@app.route('/api/pets/<pet_id>', methods=['GET'])
def get_pet(pet_id):
    pets = load_json(PETS_FILE)
    
    for pet in pets:
        if pet.get('id') == pet_id:
            return jsonify(pet), 200
    
    return jsonify({'error': 'Pet não encontrado'}), 404

@app.route('/api/pets', methods=['POST'])
@require_auth
def create_pet():
    data = request.get_json()
    
    # Validações
    required_fields = ['nome', 'tipo', 'idade', 'porte', 'genero', 'localizacao', 'imagem', 'descricao']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} é obrigatório'}), 400
    
    pets = load_json(PETS_FILE)
    pet_id = str(len(pets) + 1)
    
    new_pet = {
        'id': pet_id,
        'nome': data['nome'],
        'tipo': data['tipo'],
        'idade': data['idade'],
        'porte': data['porte'],
        'genero': data['genero'],
        'localizacao': data['localizacao'],
        'imagem': data['imagem'],
        'descricao': data['descricao'],
        'vacinado': data.get('vacinado', False),
        'castrado': data.get('castrado', False),
        'dono_id': request.current_user_id,
        'data de criacao': datetime.now().isoformat(),
        'disponivel': True
    }
    
    pets.append(new_pet)
    save_json(PETS_FILE, pets)
    
    return jsonify({
        'message': 'Pet cadastrado com sucesso',
        'pet': new_pet
    }), 201

@app.route('/api/pets/<pet_id>', methods=['PUT'])
@require_auth
def update_pet(pet_id):
    data = request.get_json()
    pets = load_json(PETS_FILE)
    
    for i, pet in enumerate(pets):
        if pet.get('id') == pet_id:
            # Verificar se é o dono
            if pet.get('dono_id') != request.current_user_id:
                return jsonify({'error': 'Você não tem permissão para atualizar este pet'}), 403
            
            # Atualizar campos
            for field in ['nome', 'tipo', 'idade', 'porte', 'genero', 'localizacao', 'imagem', 'descricao', 'vacinado', 'castrado']:
                if field in data:
                    pet[field] = data[field]
            
            pets[i] = pet
            save_json(PETS_FILE, pets)
            
            return jsonify({
                'message': 'Pet atualizado com sucesso',
                'pet': pet
            }), 200
    
    return jsonify({'error': 'Pet não encontrado'}), 404

@app.route('/api/pets/<pet_id>', methods=['DELETE'])
@require_auth
def delete_pet(pet_id):
    pets = load_json(PETS_FILE)
    
    for i, pet in enumerate(pets):
        if pet.get('id') == pet_id:
            if pet.get('dono_id') != request.current_user_id:
                return jsonify({'error': 'Você não tem permissão para deletar este pet'}), 403
            
            pets.pop(i)
            save_json(PETS_FILE, pets)
            
            return jsonify({'message': 'Pet deletado com sucesso'}), 200
    
    return jsonify({'error': 'Pet não encontrado'}), 404

# ==================== ROTAS DE ADOÇÃO ====================

@app.route('/api/adoptions', methods=['POST'])
@require_auth
def create_adoption():
    data = request.get_json()
    pet_id = data.get('pet_id')
    
    if not pet_id:
        return jsonify({'error': 'pet_id é obrigatório'}), 400
    
    # Verificar se pet existe
    pets = load_json(PETS_FILE)
    pet_exists = any(p.get('id') == pet_id for p in pets)
    
    if not pet_exists:
        return jsonify({'error': 'Pet não encontrado'}), 404
    
    adoptions = load_json(ADOCAO_FILE)
    adoption_id = str(len(adoptions) + 1)
    
    new_adoption = {
        'id': adoption_id,
        'pet_id': pet_id,
        'adotante_id': request.current_user_id,
        'status': 'pendente',  
        'data de criacao': datetime.now().isoformat(),
        'data de atualizacao': datetime.now().isoformat()
    }
    
    adoptions.append(new_adoption)
    save_json(ADOCAO_FILE, adoptions)
    
    return jsonify({
        'messagem': 'Solicitação de adoção enviada com sucesso',
        'adocao': new_adoption
    }), 201

@app.route('/api/adoptions/<adoption_id>', methods=['PUT'])
@require_auth
def update_adoption(adoption_id):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['aprovado', 'rejeitado']:
        return jsonify({'error': 'Status inválido'}), 400
    
    adoptions = load_json(ADOCAO_FILE)
    
    for i, adoption in enumerate(adoptions):
        if adoption.get('id') == adoption_id:
            # Verificar se é o dono do pet
            pet_id = adoption.get('pet_id')
            pets = load_json(PETS_FILE)
            
            for pet in pets:
                if pet.get('id') == pet_id:
                    if pet.get('dono_id') != request.current_user_id:
                        return jsonify({'error': 'Você não tem permissão para atualizar esta adoção'}), 403
            
            adoption['status'] = status
            adoption['data de atualizacao'] = datetime.now().isoformat()
            
            # Se aprovado, marcar pet como indisponível
            if status == 'approved':
                for j, pet in enumerate(pets):
                    if pet.get('id') == pet_id:
                        pet['disponivel'] = False
                        pets[j] = pet
                        save_json(PETS_FILE, pets)
            
            adoptions[i] = adoption
            save_json(ADOCAO_FILE, adoptions)
            
            return jsonify({
                'messagem': 'Adoção atualizada com sucesso',
                'adocao': adoption
            }), 200
    
    return jsonify({'error': 'Adoção não encontrada'}), 404

@app.route('/api/adoptions', methods=['GET'])
@require_auth
def get_adoptions():
    adoptions = load_json(ADOCAO_FILE)
    
    # Filtrar por usuário (minhas adoções ou adoções do meu pet)
    my_adoptions = []
    
    for adoption in adoptions:
        # Se sou o adotante
        if adoption.get('adopter_id') == request.current_user_id:
            my_adoptions.append(adoption)
        else:
            # Se sou dono do pet
            pet_id = adoption.get('pet_id')
            pets = load_json(PETS_FILE)
            for pet in pets:
                if pet.get('id') == pet_id and pet.get('dono_id') == request.current_user_id:
                    my_adoptions.append(adoption)
                    break
    
    return jsonify({
        'adoptions': my_adoptions,
        'total': len(my_adoptions)
    }), 200

# ==================== ROTAS DE ESTATÍSTICAS ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    pets = load_json(PETS_FILE)
    users = load_json(USUARIO_FILE)
    adoptions = load_json(ADOCAO_FILE)
    
    available_pets = sum(1 for p in pets if p.get('disponivel', True))
    approved_adoptions = sum(1 for a in adoptions if a.get('status') == 'approved')
    
    return jsonify({
        'total_pets': len(pets),
        'pets disponíveis': available_pets,
        'total_usuarios': len(users),
        'total_adocao': len(adoptions),
        'adoções aprovadas': approved_adoptions
    }), 200

# ==================== ROTAS DE SAÚDE ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# Inicializar banco de dados
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
