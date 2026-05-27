# BuildTrack Pro — Complete Setup & Deployment Guide

## Project Structure

```
buildtrack/
├── main.py                    ← FastAPI entry point
├── database.py                ← PostgreSQL connection & schema
├── requirements.txt           ← Python dependencies
├── vercel.json                ← Vercel deployment config
├── .env.example               ← Copy to .env
├── api/
│   ├── auth.py                ← Login, register, JWT
│   ├── projects.py            ← Projects & construction sites
│   ├── bills.py               ← Bills & expenses
│   ├── labour.py              ← Workers & attendance
│   ├── materials.py           ← Material management
│   ├── payments.py            ← Client payments
│   ├── contracts.py           ← Contracts & documents
│   ├── notifications.py       ← System notifications
│   ├── ocr.py                 ← OCR bill scanning
│   ├── reports.py             ← Reports & analytics
│   ├── ai.py                  ← AI features
│   ├── daily_logs.py          ← Daily site logs
│   └── uploads.py             ← File uploads (Cloudinary)
├── flutter_app/               ← Flutter mobile app
│   ├── lib/
│   │   ├── main.dart         ← App entry point
│   │   ├── utils/            ← Constants, theme
│   │   ├── services/         ← API service
│   │   ├── providers/        ← State management
│   │   └── screens/          ← UI screens
│   ├── pubspec.yaml          ← Flutter dependencies
│   └── assets/               ← Images, fonts, icons
└── static/
    └── index.html            ← Web frontend (optional)
```

---

## Step 1 — Backend Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database (Neon/Supabase recommended)
- Tesseract OCR (for bill scanning)

### Install Dependencies

```bash
cd buildtrack
pip install -r requirements.txt
```

### Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-odd-moon-xxxxxxxx.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-long-random-secret-key-here
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Install Tesseract OCR

- **Windows**: Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Run Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

---

## Step 2 — Flutter App Setup

### Prerequisites

- Flutter 3.0+
- Android Studio / Xcode
- Android SDK / iOS SDK

### Install Flutter Dependencies

```bash
cd flutter_app
flutter pub get
```

### Configure API URL

Edit `flutter_app/lib/utils/constants.dart`:

```dart
static const String baseUrl = 'http://localhost:8000/api';
```

For production, change to your deployed backend URL.

### Run Flutter App

```bash
# Run on connected device/emulator
flutter run

# Run specifically on Android
flutter run -d android

# Run specifically on iOS
flutter run -d ios
```

### Build for Production

```bash
# Android APK
flutter build apk --release

# Android App Bundle (for Play Store)
flutter build appbundle --release

# iOS (requires macOS and Xcode)
flutter build ios --release
```

---

## Step 3 — Database Setup

### Using Neon (Recommended)

1. Create account at [neon.tech](https://neon.tech)
2. Create a new PostgreSQL database
3. Copy the connection string from dashboard
4. Add to `.env` as `DATABASE_URL`

### Using Local PostgreSQL

```bash
# Install PostgreSQL
# Create database
createdb buildtrack

# Add to .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/buildtrack
```

Tables are created automatically on server startup.

---

## Step 4 — Set up Cloudinary (for file uploads)

1. Sign up free at https://cloudinary.com
2. Go to Dashboard → copy Cloud name, API Key, API Secret
3. Paste into your `.env`

---

## Step 5 — Deploy Backend on Vercel

```bash
npm install -g vercel
vercel login
vercel --prod
```

When prompted:

- Root directory: `buildtrack/`
- Framework: Other

Add environment variables in Vercel dashboard:

- Go to your project → Settings → Environment Variables
- Add: DATABASE_URL, SECRET_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

---

## Step 6 — Deploy Flutter App

### Android (Google Play Store)

1. Build APK or App Bundle
2. Create Google Play Console account
3. Upload app bundle
4. Complete store listing
5. Submit for review

### iOS (App Store)

1. Build iOS app
2. Open Xcode project
3. Configure signing and provisioning
4. Archive and upload to App Store Connect
5. Complete store listing
6. Submit for review

---

## Complete API Endpoints

### Authentication

| Feature          | Endpoint           | Method |
| ---------------- | ------------------ | ------ |
| Register         | /api/auth/register | POST   |
| Login            | /api/auth/login    | POST   |
| Get current user | /api/auth/me       | GET    |

### Projects

| Feature             | Endpoint           | Method |
| ------------------- | ------------------ | ------ |
| List projects       | /api/projects      | GET    |
| Create project      | /api/projects      | POST   |
| Get project details | /api/projects/{id} | GET    |
| Update project      | /api/projects/{id} | PUT    |
| Delete project      | /api/projects/{id} | DELETE |

### Bills/Expenses

| Feature     | Endpoint           | Method |
| ----------- | ------------------ | ------ |
| List bills  | /api/bills         | GET    |
| Create bill | /api/bills         | POST   |
| Get summary | /api/bills/summary | GET    |
| Update bill | /api/bills/{id}    | PUT    |
| Delete bill | /api/bills/{id}    | DELETE |

### Labour

| Feature            | Endpoint                       | Method |
| ------------------ | ------------------------------ | ------ |
| List workers       | /api/labour/workers            | GET    |
| Add worker         | /api/labour/workers            | POST   |
| Update worker      | /api/labour/workers/{id}       | PUT    |
| Delete worker      | /api/labour/workers/{id}       | DELETE |
| Get attendance     | /api/labour/attendance         | GET    |
| Mark attendance    | /api/labour/attendance         | POST   |
| Attendance summary | /api/labour/attendance/summary | GET    |

### Materials

| Feature           | Endpoint                        | Method |
| ----------------- | ------------------------------- | ------ |
| List materials    | /api/materials                  | GET    |
| Create material   | /api/materials                  | POST   |
| Update material   | /api/materials/{id}             | PUT    |
| Delete material   | /api/materials/{id}             | DELETE |
| Get usage history | /api/materials/usage            | GET    |
| Record usage      | /api/materials/usage            | POST   |
| Material summary  | /api/materials/summary/overview | GET    |

### Payments

| Feature         | Endpoint                       | Method |
| --------------- | ------------------------------ | ------ |
| List payments   | /api/payments                  | GET    |
| Create payment  | /api/payments                  | POST   |
| Update payment  | /api/payments/{id}             | PUT    |
| Delete payment  | /api/payments/{id}             | DELETE |
| Update status   | /api/payments/{id}/status      | PATCH  |
| Payment summary | /api/payments/summary/overview | GET    |

### Contracts

| Feature         | Endpoint                   | Method |
| --------------- | -------------------------- | ------ |
| List contracts  | /api/contracts             | GET    |
| Create contract | /api/contracts             | POST   |
| Update contract | /api/contracts/{id}        | PUT    |
| Delete contract | /api/contracts/{id}        | DELETE |
| Update status   | /api/contracts/{id}/status | PATCH  |

### Notifications

| Feature              | Endpoint                         | Method |
| -------------------- | -------------------------------- | ------ |
| List notifications   | /api/notifications               | GET    |
| Unread notifications | /api/notifications/unread        | GET    |
| Create notification  | /api/notifications               | POST   |
| Mark as read         | /api/notifications/{id}/read     | PATCH  |
| Mark all read        | /api/notifications/mark-all-read | PATCH  |
| Delete notification  | /api/notifications/{id}          | DELETE |
| Unread count         | /api/notifications/summary/count | GET    |

### OCR

| Feature       | Endpoint                  | Method |
| ------------- | ------------------------- | ------ |
| Scan bill     | /api/ocr/scan-bill        | POST   |
| Scan and save | /api/ocr/process-and-save | POST   |

### Reports

| Feature             | Endpoint                                  | Method |
| ------------------- | ----------------------------------------- | ------ |
| Export Excel        | /api/reports/export/excel                 | POST   |
| Dashboard analytics | /api/reports/dashboard/analytics          | GET    |
| Category breakdown  | /api/reports/dashboard/category-breakdown | GET    |
| Monthly trends      | /api/reports/dashboard/monthly-trends     | GET    |

### AI Features

| Feature           | Endpoint                          | Method |
| ----------------- | --------------------------------- | ------ |
| Predict expense   | /api/ai/predict/expense           | POST   |
| Estimate material | /api/ai/estimate/material         | POST   |
| Get insights      | /api/ai/insights                  | GET    |
| Expense patterns  | /api/ai/analysis/expense-patterns | GET    |

### Daily Logs

| Feature         | Endpoint             | Method |
| --------------- | -------------------- | ------ |
| List logs       | /api/daily-logs      | GET    |
| Create log      | /api/daily-logs      | POST   |
| Get log details | /api/daily-logs/{id} | GET    |
| Update log      | /api/daily-logs/{id} | PUT    |
| Delete log      | /api/daily-logs/{id} | DELETE |

### Uploads

| Feature      | Endpoint     | Method |
| ------------ | ------------ | ------ |
| Upload file  | /api/uploads | POST   |
| View uploads | /api/uploads | GET    |

---

## Flutter App Screens

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

---

## Troubleshooting

### Backend Issues

- **Database connection error**: Check DATABASE_URL in .env
- **Tesseract not found**: Install Tesseract OCR for your OS
- **Port already in use**: Change port with `--port 8001`

### Flutter Issues

- **API connection failed**: Check baseUrl in constants.dart
- **Build failed**: Run `flutter clean` then `flutter pub get`
- **iOS build fails**: Ensure Xcode and CocoaPods are installed

---

## Support

For issues and questions:

- Email: support@buildtrack.pro
- GitHub Issues: https://github.com/yourusername/buildtrack/issues
