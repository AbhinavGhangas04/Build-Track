import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class ExpenseProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _expenses = [];
  Map<String, dynamic>? _expenseSummary;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get expenses => _expenses;
  Map<String, dynamic>? get expenseSummary => _expenseSummary;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchExpenses({int? projectId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = projectId != null ? {'project_id': projectId} : null;
      final response = await _apiService.get(ApiEndpoints.bills, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _expenses = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchExpenseSummary() async {
    try {
      final response = await _apiService.get(ApiEndpoints.billSummary);
      if (response.statusCode == 200) {
        _expenseSummary = response.data;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching expense summary: $e');
    }
  }
  
  Future<bool> createExpense(Map<String, dynamic> expenseData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.bills, data: expenseData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchExpenses();
        await fetchExpenseSummary();
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
  
  Future<bool> updateExpense(int expenseId, Map<String, dynamic> expenseData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.billDetails.replaceAll('{id}', expenseId.toString());
      final response = await _apiService.put(path, data: expenseData);
      if (response.statusCode == 200) {
        await fetchExpenses();
        await fetchExpenseSummary();
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
  
  Future<bool> deleteExpense(int expenseId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.billDetails.replaceAll('{id}', expenseId.toString());
      final response = await _apiService.delete(path);
      if (response.statusCode == 200) {
        await fetchExpenses();
        await fetchExpenseSummary();
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
