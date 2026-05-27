import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class LabourProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _workers = [];
  List<Map<String, dynamic>> _attendance = [];
  Map<String, dynamic>? _attendanceSummary;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get workers => _workers;
  List<Map<String, dynamic>> get attendance => _attendance;
  Map<String, dynamic>? get attendanceSummary => _attendanceSummary;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchWorkers({int? projectId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = projectId != null ? {'project_id': projectId} : null;
      final response = await _apiService.get(ApiEndpoints.workers, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _workers = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchAttendance({DateTime? date}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = date != null ? {'att_date': date.toIso8601String().split('T')[0]} : null;
      final response = await _apiService.get(ApiEndpoints.attendance, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _attendance = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchAttendanceSummary() async {
    try {
      final response = await _apiService.get(ApiEndpoints.attendanceSummary);
      if (response.statusCode == 200) {
        _attendanceSummary = response.data;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching attendance summary: $e');
    }
  }
  
  Future<bool> addWorker(Map<String, dynamic> workerData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.workers, data: workerData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchWorkers();
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
  
  Future<bool> updateWorker(int workerId, Map<String, dynamic> workerData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.workerDetails.replaceAll('{id}', workerId.toString());
      final response = await _apiService.put(path, data: workerData);
      if (response.statusCode == 200) {
        await fetchWorkers();
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
  
  Future<bool> deleteWorker(int workerId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.workerDetails.replaceAll('{id}', workerId.toString());
      final response = await _apiService.delete(path);
      if (response.statusCode == 200) {
        await fetchWorkers();
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
  
  Future<bool> markAttendance(Map<String, dynamic> attendanceData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.attendance, data: attendanceData);
      if (response.statusCode == 200) {
        await fetchAttendance();
        await fetchAttendanceSummary();
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
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
