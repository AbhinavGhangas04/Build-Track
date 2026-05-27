# BuildTrack Pro - Complete Contractor Management System

A production-ready mobile application for contractors, builders, and civil engineers to manage construction site activities, expenses, labour, materials, payments, bills, and reports from mobile devices.

## 🚀 Project Overview

BuildTrack Pro is a comprehensive contractor management system that helps construction professionals:
- Manage multiple construction sites
- Track expenses and income
- Manage labour and attendance
- Monitor material usage and inventory
- Track client payments
- Generate detailed reports
- Use AI-powered insights and predictions
- Scan bills using OCR technology

## ✨ Features

### Core Features
- **Authentication**: Secure JWT-based login/signup system
- **Dashboard**: Real-time analytics with charts and graphs
- **Site Management**: Create and manage multiple construction sites
- **Expense Tracking**: Categorize and track all project expenses
- **Labour Management**: Worker database, attendance, and payments
- **Material Management**: Inventory tracking with supplier details
- **Payment Tracker**: Client payment tracking with reminders
- **Reports**: Generate Excel and PDF reports
- **OCR Bill Scanner**: Automatically extract data from bill images
- **AI Features**: Expense prediction and material estimation
- **Notifications**: Payment and material shortage alerts
- **Daily Logs**: Site diary with weather and activities

### Advanced Features
- Multi-language support (English + Hindi)
- Dark mode support
- Offline mode capability
- GPS site location tracking
- WhatsApp invoice sharing
- Cloud sync
- Multi-user access with admin panel
- Voice input in Hindi

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Neon/Supabase)
- **Authentication**: JWT (python-jose)
- **OCR**: Tesseract OCR (pytesseract)
- **Excel Export**: pandas + openpyxl
- **PDF Generation**: reportlab
- **File Storage**: Cloudinary
- **Async**: asyncpg for PostgreSQL

### Frontend (Flutter)
- **Framework**: Flutter (latest stable)
- **State Management**: Provider
- **HTTP Client**: Dio
- **Charts**: FL Chart
- **OCR**: Google ML Kit Text Recognition
- **Local Storage**: flutter_secure_storage, shared_preferences
- **Image Handling**: image_picker, image_cropper
- **Excel**: excel package
- **PDF**: pdf + printing packages
- **Maps**: geolocator, geocoding
- **Notifications**: flutter_local_notifications

## 📁 Project Structure

```
buildtrack/
├── api/                          # FastAPI API modules
│   ├── __init__.py
│   ├── auth.py                   # Authentication endpoints
│   ├── projects.py               # Project/Site management
│   ├── bills.py                  # Bills and expenses
│   ├── labour.py                 # Labour and attendance
│   ├── materials.py              # Material management
│   ├── payments.py               # Client payments
│   ├── contracts.py              # Contracts and documents
│   ├── notifications.py          # Notifications
│   ├── ocr.py                    # OCR bill scanning
│   ├── reports.py                # Reports and analytics
│   ├── ai.py                     # AI features
│   ├── daily_logs.py             # Daily site logs
│   └── uploads.py                # File uploads
├── static/                       # Static files (web frontend)
│   ├── index.html
│   ├── css/
│   └── js/
├── flutter_app/                  # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart            # App entry point
│   │   ├── utils/
│   │   │   ├── constants.dart   # App constants
│   │   │   └── theme.dart       # App theme
│   │   ├── services/
│   │   │   └── api_service.dart # API communication
│   │   ├── providers/           # State management
│   │   │   ├── auth_provider.dart
│   │   │   ├── project_provider.dart
│   │   │   ├── expense_provider.dart
│   │   │   ├── labour_provider.dart
│   │   │   ├── material_provider.dart
│   │   │   ├── payment_provider.dart
│   │   │   └── notification_provider.dart
│   │   └── screens/
│   │       ├── splash_screen.dart
│   │       ├── auth/
│   │       │   ├── login_screen.dart
│   │       │   └── signup_screen.dart
│   │       ├── home/
│   │       │   └── dashboard_screen.dart
│   │       ├── projects/
│   │       │   └── projects_screen.dart
│   │       ├── expenses/
│   │       │   └── expenses_screen.dart
│   │       ├── labour/
│   │       │   └── labour_screen.dart
│   │       ├── materials/
│   │       │   └── materials_screen.dart
│   │       ├── payments/
│   │       │   └── payments_screen.dart
│   │       └── reports/
│   │           └── reports_screen.dart
│   ├── pubspec.yaml             # Flutter dependencies
│   └── assets/                  # Images, fonts, icons
├── database.py                   # Database connection and schema
├── main.py                       # FastAPI application entry
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🗄 Database Schema

### Tables
- **companies**: User/company accounts
- **projects**: Construction sites/projects
- **bills**: Expenses and income records
- **workers**: Labour/workers database
- **attendance**: Worker attendance tracking
- **labour_payments**: Labour payment records
- **materials**: Material inventory
- **material_usage**: Material usage tracking
- **client_payments**: Client payment tracking
- **contracts**: Contracts and documents
- **notifications**: System notifications
- **daily_logs**: Daily site logs
- **uploads**: File uploads

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Flutter 3.0+
- PostgreSQL database (Neon/Supabase recommended)
- Tesseract OCR (for bill scanning)
- Node.js (for some Flutter tools)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd buildtrack
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

5. **Install Tesseract OCR**
- **Windows**: Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

6. **Run the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Flutter App Setup

1. **Navigate to Flutter app directory**
```bash
cd flutter_app
```

2. **Install Flutter dependencies**
```bash
flutter pub get
```

3. **Configure API URL**
Edit `lib/utils/constants.dart`:
```dart
static const String baseUrl = 'http://your-backend-url/api';
```

4. **Run the app**
```bash
flutter run
```

For Android:
```bash
flutter run -d android
```

For iOS:
```bash
flutter run -d ios
```

### Database Setup

#### Using Neon (Recommended)
1. Create account at [neon.tech](https://neon.tech)
2. Create a new PostgreSQL database
3. Copy the connection string
4. Add to `.env` file as `DATABASE_URL`

#### Using Local PostgreSQL
```bash
# Install PostgreSQL
# Create database
createdb buildtrack

# Add connection string to .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/buildtrack
```

Tables will be created automatically on server startup.

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new company
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Bills/Expenses
- `GET /api/bills` - List all bills
- `POST /api/bills` - Create bill
- `GET /api/bills/summary` - Get financial summary
- `PUT /api/bills/{id}` - Update bill
- `DELETE /api/bills/{id}` - Delete bill

### Labour
- `GET /api/labour/workers` - List workers
- `POST /api/labour/workers` - Add worker
- `GET /api/labour/attendance` - Get attendance
- `POST /api/labour/attendance` - Mark attendance
- `GET /api/labour/attendance/summary` - Attendance summary

### Materials
- `GET /api/materials` - List materials
- `POST /api/materials` - Add material
- `GET /api/materials/usage` - Material usage history
- `POST /api/materials/usage` - Record usage
- `GET /api/materials/summary/overview` - Material summary

### Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Add payment
- `GET /api/payments/summary/overview` - Payment summary
- `PATCH /api/payments/{id}/status` - Update payment status

### OCR
- `POST /api/ocr/scan-bill` - Scan bill image
- `POST /api/ocr/process-and-save` - Scan and save as expense

### Reports
- `POST /api/reports/export/excel` - Export Excel report
- `GET /api/reports/dashboard/analytics` - Dashboard analytics
- `GET /api/reports/dashboard/category-breakdown` - Expense by category
- `GET /api/reports/dashboard/monthly-trends` - Monthly trends

### AI Features
- `POST /api/ai/predict/expense` - Predict future expenses
- `POST /api/ai/estimate/material` - Estimate material requirements
- `GET /api/ai/insights` - Get smart insights
- `GET /api/ai/analysis/expense-patterns` - Analyze expense patterns

### Daily Logs
- `GET /api/daily-logs` - List daily logs
- `POST /api/daily-logs` - Create daily log
- `GET /api/daily-logs/{id}` - Get log details

## 📱 App Screens

1. **Splash Screen** - App loading with animation
2. **Login Screen** - User authentication
3. **Signup Screen** - New user registration
4. **Dashboard** - Overview with analytics and charts
5. **Projects** - Construction site management
6. **Expenses** - Expense and bill tracking
7. **Labour** - Worker and attendance management
8. **Materials** - Material inventory tracking
9. **Payments** - Client payment tracking
10. **Reports** - Reports and analytics

## 🎨 UI/UX Features

- Modern premium design with glassmorphism
- Smooth animations and transitions
- Dark mode support
- Responsive layouts
- Professional color palette
- Construction-themed icons
- Mobile-first design
- Intuitive navigation

## 🔒 Security Features

- JWT authentication
- Secure token storage (flutter_secure_storage)
- Password hashing (bcrypt)
- CORS protection
- Input validation
- SQL injection prevention (parameterized queries)

## 📊 Analytics & Reports

### Dashboard Analytics
- Total income and expenses
- Profit/loss calculation
- Active projects count
- Total workers
- Pending payments
- Material costs
- Recent activity feed

### Report Types
- Expense reports
- Income reports
- Labour reports
- Material usage reports
- Profit/loss reports
- Category breakdown
- Monthly trends

### Export Formats
- Excel (.xlsx)
- PDF

## 🤖 AI Features

### Expense Prediction
- Predicts future expenses based on historical data
- Category-wise predictions
- Trend analysis
- Confidence scoring

### Material Estimation
- Estimates material requirements based on area
- Construction type-specific calculations
- Cost estimation
- Contingency calculation

### Smart Insights
- Unusual spending detection
- Material shortage alerts
- Budget overrun warnings
- Payment reminders

## 🚢 Deployment

### Backend Deployment (Vercel/Render)

1. **Deploy to Vercel**
```bash
npm install -g vercel
vercel
```

2. **Or deploy to Render**
- Create account at [render.com](https://render.com)
- Connect GitHub repository
- Deploy as Web Service
- Add environment variables

### Flutter App Deployment

#### Android
```bash
flutter build apk --release
flutter build appbundle --release
```

Upload APK/AAB to Google Play Console.

#### iOS
```bash
flutter build ios --release
```
- Open Xcode project
- Configure signing
- Archive and upload to App Store Connect

### Database Deployment

Use Neon (recommended) or Supabase for managed PostgreSQL:
- Automatic backups
- Serverless scaling
- Built-in connection pooling
- Free tier available

## 🧪 Testing

### Backend Testing
```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Flutter Testing
```bash
# Unit tests
flutter test

# Integration tests
flutter drive --target=test_driver/app.dart
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@buildtrack.pro or create an issue in the repository.

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- Flutter team for the cross-platform framework
- Tesseract OCR for text recognition
- All open-source contributors

## 📞 Contact

- **Email**: support@buildtrack.pro
- **Website**: https://buildtrack.pro
- **GitHub**: https://github.com/yourusername/buildtrack

---

**Built with ❤️ for construction professionals**
