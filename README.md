# Medical Chatbot - He Thong Chatbot Tam Soat Benh Nhan

Du an demo xay dung chatbot tu dong hoi trieu chung va de xuat khoa kham cho benh vien su dung LLM.

## Muc Luc
- [Gioi Thieu](#gioi-thieu)
- [Tech Stack](#tech-stack)
- [Cau Truc Thu Muc](#cau-truc-thu-muc)
- [Cai Dat](#cai-dat)
- [Chay Ung Dung](#chay-ung-dung)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Roadmap](#roadmap)

## Gioi Thieu

Day la du an demo cho khoa hoc, xay dung mot he thong chatbot tu dong:
- Hoi ve trieu chung cua benh nhan
- Phan tich va de xuat khoa kham phu hop
- Phat hien cac dau hieu nguy hiem can cap cuu
- Luu tru lich su hoi thoai

## Tech Stack

### Backend
- **Python 3.10+**
- **Flask** - Web framework
- **SQLite** - Database
- **Qwen3-4B** - LLM Model (via Ollama)

### Frontend
- **Angular 20+** - Frontend framework
- **TypeScript**
- **SCSS** - Styling

## Cau Truc Thu Muc

```
DummyChatBot/
├── backend/                    # Backend Flask
│   ├── app.py                 # Entry point
│   ├── config.py              # Cau hinh
│   ├── requirements.txt       # Dependencies
│   ├── routes/                # API endpoints
│   │   ├── chat_routes.py
│   │   └── department_routes.py
│   ├── models/                # Database models
│   │   ├── database.py
│   │   └── conversation.py
│   ├── services/              # Business logic
│   │   ├── chatbot_service.py
│   │   └── department_service.py
│   └── utils/                 # Utilities
│       ├── helpers.py
│       └── validators.py
├── frontend/                  # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # UI Components
│   │   │   ├── services/     # API Services
│   │   │   └── models/       # Data Models
│   │   └── environments/     # Environment configs
│   └── package.json
├── database/                  # Database
│   ├── chatbot.db            # SQLite database file
│   ├── schema.sql            # Database schema
│   ├── init_db.py            # Script tao schema
│   └── seed_data.py          # Script them du lieu mau
├── .gitignore
└── README.md
```

## Cai Dat

### 1. Clone Repository

```bash
cd DummyChatBot
```

### 2. Cai Dat Backend

```bash
# Di chuyen vao thu muc backend
cd backend

# Tao virtual environment
python -m venv venv

# Kich hoat virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cai dat dependencies
pip install -r requirements.txt
```

### 3. Khoi Tao Database

```bash
# Di chuyen vao thu muc database
cd ../database

# Chay script tao database
python init_db.py

# Them du lieu mau
python seed_data.py
```

### 4. Cai Dat Frontend

```bash
# Di chuyen vao thu muc frontend
cd ../frontend

# Cai dat dependencies
npm install
```

## Chay Ung Dung

### Chay Backend (Terminal 1)

```bash
cd backend

# Kich hoat virtual environment (neu chua)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Chay Flask server
python app.py
```

Backend se chay tai: `http://localhost:5000`

### Chay Frontend (Terminal 2)

```bash
cd frontend

# Chay Angular development server
ng serve
```

Frontend se chay tai: `http://localhost:4200`

## API Documentation

### Chat Endpoints

#### POST `/api/v1/chat`
Gui tin nhan den chatbot

**Request Body:**
```json
{
  "message": "Toi bi dau dau",
  "session_id": "uuid-string",
  "conversation_history": []
}
```

**Response:**
```json
{
  "response": "Cho toi biet them...",
  "session_id": "uuid-string",
  "suggested_department": "Khoa Than Kinh"
}
```

#### GET `/api/v1/chat/history/{session_id}`
Lay lich su chat

#### POST `/api/v1/chat/reset`
Reset cuoc hoi thoai

### Department Endpoints

#### GET `/api/v1/departments`
Lay danh sach tat ca cac khoa

#### GET `/api/v1/departments/{id}`
Lay thong tin chi tiet mot khoa

## Database Schema

### Table: departments
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Ten khoa |
| description | TEXT | Mo ta |
| common_symptoms | TEXT | Trieu chung thuong gap |
| location | TEXT | Vi tri |
| working_hours | TEXT | Gio lam viec |

### Table: symptom_rules
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| symptom_keyword | TEXT | Tu khoa trieu chung |
| department_id | INTEGER | Foreign key den departments |
| priority | INTEGER | Do uu tien (1-3) |

### Table: red_flags
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| keyword | TEXT | Tu khoa nguy hiem |
| severity | TEXT | Muc do nghiem trong |
| urgent_message | TEXT | Thong bao khan cap |

### Table: conversations
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | TEXT | ID cua session |
| user_message | TEXT | Tin nhan nguoi dung |
| bot_response | TEXT | Phan hoi tu bot |
| suggested_department | TEXT | Khoa duoc de xuat |
| timestamp | TIMESTAMP | Thoi gian |

## Kiem Tra Cai Dat

Checklist de dam bao setup thanh cong:

- [ ] Python 3.10+ da duoc cai dat
- [ ] Node.js va npm da duoc cai dat
- [ ] Angular CLI da duoc cai dat (`npm install -g @angular/cli`)
- [ ] Virtual environment da duoc tao trong `backend/venv/`
- [ ] Dependencies Python da duoc cai (`pip install -r requirements.txt`)
- [ ] Database da duoc tao (`database/chatbot.db` ton tai)
- [ ] Du lieu mau da duoc them
- [ ] Dependencies Angular da duoc cai (`node_modules/` ton tai)
- [ ] Backend chay thanh cong tai `http://localhost:5000`
- [ ] Frontend chay thanh cong tai `http://localhost:4200`
- [ ] Kiem tra endpoint health: `http://localhost:5000/api/health`

## Roadmap

### Phase 1: Setup Project Structure (COMPLETED)
- [x] Tao cau truc thu muc
- [x] Setup backend Flask
- [x] Setup frontend Angular
- [x] Tao database schema
- [x] Them du lieu mau

### Phase 2: Implement Core Features (NEXT)
- [ ] Implement database operations
- [ ] Tao UI cho chatbot
- [ ] Ket noi frontend voi backend API
- [ ] Implement logic phan tich trieu chung co ban

### Phase 3: LLM Integration
- [ ] Cai dat Qwen3-4B model
- [ ] Tich hop LLM vao chatbot service
- [ ] Fine-tune responses
- [ ] Implement context awareness

### Phase 4: UI/UX Enhancement
- [ ] Cai thien giao dien chat
- [ ] Them animations
- [ ] Responsive design
- [ ] Them feedback mechanism

### Phase 5: Testing & Optimization
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Security review

## Ho Tro

Neu gap van de trong qua trinh cai dat:

1. Kiem tra lai cac buoc trong phan [Cai Dat](#cai-dat)
2. Dam bao Python va Node.js version dung
3. Kiem tra log errors trong terminal

## License

Du an demo cho muc dich hoc tap.

---

**Buoc Tiep Theo:** Implement chi tiet database schema va ket noi API
