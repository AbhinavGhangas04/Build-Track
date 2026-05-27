import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class NotificationProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _notifications = [];
  List<Map<String, dynamic>> _unreadNotifications = [];
  int _unreadCount = 0;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get notifications => _notifications;
  List<Map<String, dynamic>> get unreadNotifications => _unreadNotifications;
  int get unreadCount => _unreadCount;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchNotifications() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.get(ApiEndpoints.notifications);
      if (response.statusCode == 200) {
        _notifications = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchUnreadNotifications() async {
    try {
      final response = await _apiService.get(ApiEndpoints.unreadNotifications);
      if (response.statusCode == 200) {
        _unreadNotifications = List<Map<String, dynamic>>.from(response.data);
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching unread notifications: $e');
    }
  }
  
  Future<void> fetchUnreadCount() async {
    try {
      final response = await _apiService.get(ApiEndpoints.notificationCount);
      if (response.statusCode == 200) {
        _unreadCount = response.data['unread_count'] ?? 0;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching unread count: $e');
    }
  }
  
  Future<bool> createNotification(Map<String, dynamic> notificationData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.notifications, data: notificationData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchNotifications();
        await fetchUnreadCount();
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> markAsRead(int notificationId) async {
    try {
      final path = '${ApiEndpoints.notifications}/${notificationId}/read';
      final response = await _apiService.patch(path);
      if (response.statusCode == 200) {
        await fetchNotifications();
        await fetchUnreadCount();
        return true;
      }
      return false;
    } catch (e) {
      print('Error marking notification as read: $e');
      return false;
    }
  }
  
  Future<bool> markAllAsRead() async {
    try {
      final response = await _apiService.patch('${ApiEndpoints.notifications}/mark-all-read');
      if (response.statusCode == 200) {
        await fetchNotifications();
        await fetchUnreadCount();
        return true;
      }
      return false;
    } catch (e) {
      print('Error marking all notifications as read: $e');
      return false;
    }
  }
  
  Future<bool> deleteNotification(int notificationId) async {
    try {
      final response = await _apiService.delete('${ApiEndpoints.notifications}/$notificationId');
      if (response.statusCode == 200) {
        await fetchNotifications();
        await fetchUnreadCount();
        return true;
      }
      return false;
    } catch (e) {
      print('Error deleting notification: $e');
      return false;
    }
  }
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
