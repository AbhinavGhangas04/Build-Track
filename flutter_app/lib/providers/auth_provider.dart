import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  String? _token;
  Map<String, dynamic>? _user;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  String? get token => _token;
  Map<String, dynamic>? get user => _user;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _token != null;
  
  AuthProvider() {
    _checkAuthStatus();
  }
  
  Future<void> _checkAuthStatus() async {
    _token = await _apiService.getToken();
    if (_token != null) {
      await fetchUserProfile();
    }
    notifyListeners();
  }
  
  Future<bool> login(String companyName, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final formData = {
        'username': companyName,
        'password': password,
      };
      
      final response = await _apiService.post(ApiEndpoints.login, data: formData);
      
      if (response.statusCode == 200) {
        _token = response.data['access_token'];
        await _apiService.setToken(_token!);
        _user = {
          'company_name': response.data['company_name'],
        };
        await fetchUserProfile();
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Login failed';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  Future<bool> register(String companyName, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final data = {
        'company_name': companyName,
        'password': password,
      };
      
      final response = await _apiService.post(ApiEndpoints.register, data: data);
      
      if (response.statusCode == 200) {
        _token = response.data['access_token'];
        await _apiService.setToken(_token!);
        _user = {
          'company_name': response.data['company_name'],
        };
        await fetchUserProfile();
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _errorMessage = 'Registration failed';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  Future<void> fetchUserProfile() async {
    try {
      final response = await _apiService.get(ApiEndpoints.me);
      if (response.statusCode == 200) {
        _user = response.data;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching user profile: $e');
    }
  }
  
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();
    
    await _apiService.clearToken();
    _token = null;
    _user = null;
    
    _isLoading = false;
    notifyListeners();
  }
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
