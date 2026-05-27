import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class PaymentProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _payments = [];
  Map<String, dynamic>? _paymentSummary;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get payments => _payments;
  Map<String, dynamic>? get paymentSummary => _paymentSummary;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchPayments({int? projectId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = projectId != null ? {'project_id': projectId} : null;
      final response = await _apiService.get(ApiEndpoints.payments, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _payments = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchPaymentSummary() async {
    try {
      final response = await _apiService.get(ApiEndpoints.paymentSummary);
      if (response.statusCode == 200) {
        _paymentSummary = response.data;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching payment summary: $e');
    }
  }
  
  Future<bool> createPayment(Map<String, dynamic> paymentData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.payments, data: paymentData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchPayments();
        await fetchPaymentSummary();
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
  
  Future<bool> updatePayment(int paymentId, Map<String, dynamic> paymentData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.paymentDetails.replaceAll('{id}', paymentId.toString());
      final response = await _apiService.put(path, data: paymentData);
      if (response.statusCode == 200) {
        await fetchPayments();
        await fetchPaymentSummary();
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
  
  Future<bool> deletePayment(int paymentId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.paymentDetails.replaceAll('{id}', paymentId.toString());
      final response = await _apiService.delete(path);
      if (response.statusCode == 200) {
        await fetchPayments();
        await fetchPaymentSummary();
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
  
  Future<bool> updatePaymentStatus(int paymentId, String status) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = '${ApiEndpoints.paymentDetails.replaceAll('{id}', paymentId.toString())}/status';
      final response = await _apiService.patch(path, data: {'status': status});
      if (response.statusCode == 200) {
        await fetchPayments();
        await fetchPaymentSummary();
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
