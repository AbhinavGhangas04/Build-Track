import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class MaterialProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _materials = [];
  List<Map<String, dynamic>> _materialUsage = [];
  Map<String, dynamic>? _materialSummary;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get materials => _materials;
  List<Map<String, dynamic>> get materialUsage => _materialUsage;
  Map<String, dynamic>? get materialSummary => _materialSummary;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchMaterials({int? projectId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = projectId != null ? {'project_id': projectId} : null;
      final response = await _apiService.get(ApiEndpoints.materials, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _materials = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchMaterialUsage({int? materialId, int? projectId}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final queryParams = {};
      if (materialId != null) queryParams['material_id'] = materialId;
      if (projectId != null) queryParams['project_id'] = projectId;
      
      final response = await _apiService.get(ApiEndpoints.materialUsage, queryParameters: queryParams);
      if (response.statusCode == 200) {
        _materialUsage = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchMaterialSummary() async {
    try {
      final response = await _apiService.get(ApiEndpoints.materialSummary);
      if (response.statusCode == 200) {
        _materialSummary = response.data;
        notifyListeners();
      }
    } catch (e) {
      print('Error fetching material summary: $e');
    }
  }
  
  Future<bool> createMaterial(Map<String, dynamic> materialData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.materials, data: materialData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchMaterials();
        await fetchMaterialSummary();
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
  
  Future<bool> updateMaterial(int materialId, Map<String, dynamic> materialData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.materialDetails.replaceAll('{id}', materialId.toString());
      final response = await _apiService.put(path, data: materialData);
      if (response.statusCode == 200) {
        await fetchMaterials();
        await fetchMaterialSummary();
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
  
  Future<bool> deleteMaterial(int materialId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.materialDetails.replaceAll('{id}', materialId.toString());
      final response = await _apiService.delete(path);
      if (response.statusCode == 200) {
        await fetchMaterials();
        await fetchMaterialSummary();
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
  
  Future<bool> recordMaterialUsage(Map<String, dynamic> usageData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.materialUsage, data: usageData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchMaterials();
        await fetchMaterialUsage();
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
