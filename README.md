# 🐾 House Pet API (Flask)

API REST desenvolvida em Flask para gerenciamento de adoção de pets, com autenticação de usuários, cadastro de pets e sistema de adoção.

---

# 🚀 Tecnologias utilizadas

* Python 3
* Flask
* Flask-CORS
* JSON (como banco de dados local)
* Hashlib (criptografia de senha)
* Secrets (geração de token)

---

# 📁 Estrutura do projeto

```
/projeto
│
├── app.py
├── usuarios.json
├── pets.json
├── adocao.json
```

---

# ⚙️ Como executar o projeto

## 1. Instalar dependências

```bash
pip install flask flask-cors
```

## 2. Rodar o servidor

```bash
python app.py
```

Servidor será iniciado em:

```
http://localhost:5000
```

---

# 🔐 Autenticação

A API usa autenticação via **Token Bearer**.

## 📌 Como funciona

* Usuário faz login ou registro
* API gera um token único
* Token deve ser enviado no header das requisições protegidas

```http
Authorization: Bearer SEU_TOKEN
```

---

# 👤 ROTAS DE USUÁRIOS

## 📌 Registro

```http
POST /api/auth/registro
```

### Body:

```json
{
  "nome": "Adriel Carvalho",
  "email": "adrielcarvalholeite071@gmail.com",
  "senha": "Senha123"
}
```

---

## 📌 Login

```http
POST /api/auth/login
```

### Body:

```json
{
  "email": "adrielcarvalholeite071@gmail.com",
  "senha": "Senha123"
}
```

---

## 📌 Perfil

```http
GET /api/auth/profile
```

🔐 Requer token

---

# 🐶 ROTAS DE PETS

## 📌 Listar pets

```http
GET /api/pets
```

### Filtros opcionais:

```
?tipo=
?idade=
?porte=
?localizacao=
?buscar_nome=
```

---

## 📌 Buscar pet por ID

```http
GET /api/pets/<id>
```

---

## 📌 Criar pet

```http
POST /api/pets
```

🔐 Requer token

### Body:

```json
{
  "nome": "Rex",
  "tipo": "Cachorro",
  "idade": 3,
  "porte": "Médio",
  "genero": "Macho",
  "localizacao": "Palmas",
  "imagem": "url-da-imagem",
  "descricao": "Cachorro dócil",
  "vacinado": true,
  "castrado": false
}
```

---

## 📌 Atualizar pet

```http
PUT /api/pets/<id>
```

🔐 Requer token + ser dono do pet

---

## 📌 Deletar pet

```http
DELETE /api/pets/<id>
```

🔐 Requer token + ser dono do pet

---

# ❤️ SISTEMA DE ADOÇÃO

## 📌 Solicitar adoção

```http
POST /api/adoptions
```

🔐 Requer token

### Body:

```json
{
  "pet_id": "1"
}
```

---

## 📌 Atualizar adoção

```http
PUT /api/adoptions/<id>
```

🔐 Requer token

### Body:

```json
{
  "status": "aprovado"
}
```

ou

```json
{
  "status": "rejeitado"
}
```

---

## 📌 Listar adoções

```http
GET /api/adoptions
```

🔐 Requer token

---

# 📊 ESTATÍSTICAS

## 📌 Dashboard

```http
GET /api/stats
```

### Retorno:

* total de pets
* pets disponíveis
* total de usuários
* total de adoções
* adoções aprovadas

---

# 🩺 HEALTH CHECK

## 📌 Status da API

```http
GET /api/health
```

### Resposta:

```json
{
  "status": "ok"
}
```

---

# 🔐 SEGURANÇA

* Senhas criptografadas com SHA256
* Autenticação via token
* Controle de acesso por dono do recurso
* Proteção de rotas privadas

---

# ⚠️ LIMITAÇÕES

* Banco de dados em JSON (não escalável)
* IDs incrementais (pode gerar conflitos)
* Estrutura simples sem ORM
* Sem paginação

---

# 🚀 MELHORIAS FUTURAS

* Migrar para PostgreSQL/MySQL
* Implementar JWT
* Criar frontend (React/Vue)
* Deploy em cloud (Render/Railway)
* Paginação e cache

---

# 👨‍💻 AUTOR

Projeto acadêmico desenvolvido com Flask para sistema de adoção de pets.

