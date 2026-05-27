class AppConstants {
  static const String appName = 'BuildTrack Pro';
  static const String appVersion = '1.0.0';
  
  // API Configuration
  static const String baseUrl = 'http://localhost:8000/api';
  static const int connectionTimeout = 30000;
  static const int receiveTimeout = 30000;
  
  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userKey = 'user_data';
  static const String themeKey = 'theme_mode';
  static const String languageKey = 'language';
  
  // Expense Categories
  static const List<String> expenseCategories = [
    'Labour',
    'Cement',
    'Steel',
    'Sand',
    'Bricks',
    'Tiles',
    'Transport',
    'Machinery',
    'Miscellaneous',
  ];
  
  // Material Categories
  static const List<String> materialCategories = [
    'Cement',
    'Steel',
    'Bricks',
    'Sand',
    'Paint',
    'Electrical',
    'Plumbing',
    'Wood',
    'Glass',
    'Other',
  ];
  
  // Payment Types
  static const List<String> paymentTypes = ['Advance', 'Milestone', 'Final'];
  
  // Labour Payment Types
  static const List<String> labourPaymentTypes = ['Daily', 'Weekly', 'Monthly'];
  
  // Construction Types
  static const List<String> constructionTypes = ['Residential', 'Commercial', 'Industrial'];
  
  // Project Status
  static const List<String> projectStatus = ['Active', 'Completed', 'On Hold', 'Cancelled'];
  
  // Bill Status
  static const List<String> billStatus = ['Pending', 'Paid', 'Cancelled'];
  
  // Attendance Status
  static const List<String> attendanceStatus = ['Present', 'Absent', 'Holiday'];
  
  // Notification Types
  static const List<String> notificationTypes = ['Payment', 'Material', 'Labour', 'General'];
  
  // Languages
  static const List<String> languages = ['English', 'Hindi'];
  
  // Chart Colors
  static const List<Color> chartColors = [
    Color(0xFF4CAF50),
    Color(0xFF2196F3),
    Color(0xFFFF9800),
    Color(0xFFE91E63),
    Color(0xFF9C27B0),
    Color(0xFF00BCD4),
    Color(0xFF8BC34A),
    Color(0xFFFF5722),
  ];
}

class ApiEndpoints {
  // Auth
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String me = '/auth/me';
  
  // Projects
  static const String projects = '/projects';
  static const String projectDetails = '/projects/{id}';
  
  // Bills/Expenses
  static const String bills = '/bills';
  static const String billDetails = '/bills/{id}';
  static const String billSummary = '/bills/summary';
  
  // Labour
  static const String workers = '/labour/workers';
  static const String workerDetails = '/labour/workers/{id}';
  static const String attendance = '/labour/attendance';
  static const String attendanceSummary = '/labour/attendance/summary';
  
  // Materials
  static const String materials = '/materials';
  static const String materialDetails = '/materials/{id}';
  static const String materialUsage = '/materials/usage';
  static const String materialSummary = '/materials/summary/overview';
  
  // Payments
  static const String payments = '/payments';
  static const String paymentDetails = '/payments/{id}';
  static const String paymentSummary = '/payments/summary/overview';
  
  // Contracts
  static const String contracts = '/contracts';
  static const String contractDetails = '/contracts/{id}';
  
  // Notifications
  static const String notifications = '/notifications';
  static const String unreadNotifications = '/notifications/unread';
  static const String notificationCount = '/notifications/summary/count';
  
  // OCR
  static const String scanBill = '/ocr/scan-bill';
  static const String processAndSave = '/ocr/process-and-save';
  
  // Reports
  static const String exportExcel = '/reports/export/excel';
  static const String dashboardAnalytics = '/reports/dashboard/analytics';
  static const String categoryBreakdown = '/reports/dashboard/category-breakdown';
  static const String monthlyTrends = '/reports/dashboard/monthly-trends';
  
  // AI
  static const String predictExpense = '/ai/predict/expense';
  static const String estimateMaterial = '/ai/estimate/material';
  static const String insights = '/ai/insights';
  static const String expensePatterns = '/ai/analysis/expense-patterns';
  
  // Daily Logs
  static const String dailyLogs = '/daily-logs';
  static const String dailyLogDetails = '/daily-logs/{id}';
  
  // Uploads
  static const String upload = '/uploads';
}
