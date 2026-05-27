import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../utils/constants.dart';

class ProjectProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isLoading = false;
  List<Map<String, dynamic>> _projects = [];
  Map<String, dynamic>? _selectedProject;
  String? _errorMessage;
  
  bool get isLoading => _isLoading;
  List<Map<String, dynamic>> get projects => _projects;
  Map<String, dynamic>? get selectedProject => _selectedProject;
  String? get errorMessage => _errorMessage;
  
  Future<void> fetchProjects() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.get(ApiEndpoints.projects);
      if (response.statusCode == 200) {
        _projects = List<Map<String, dynamic>>.from(response.data);
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<void> fetchProjectDetails(int projectId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.projectDetails.replaceAll('{id}', projectId.toString());
      final response = await _apiService.get(path);
      if (response.statusCode == 200) {
        _selectedProject = response.data;
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }
  
  Future<bool> createProject(Map<String, dynamic> projectData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final response = await _apiService.post(ApiEndpoints.projects, data: projectData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        await fetchProjects();
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
  
  Future<bool> updateProject(int projectId, Map<String, dynamic> projectData) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.projectDetails.replaceAll('{id}', projectId.toString());
      final response = await _apiService.put(path, data: projectData);
      if (response.statusCode == 200) {
        await fetchProjects();
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
  
  Future<bool> deleteProject(int projectId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      final path = ApiEndpoints.projectDetails.replaceAll('{id}', projectId.toString());
      final response = await _apiService.delete(path);
      if (response.statusCode == 200) {
        await fetchProjects();
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
  
  void selectProject(Map<String, dynamic> project) {
    _selectedProject = project;
    notifyListeners();
  }
  
  void clearSelectedProject() {
    _selectedProject = null;
    notifyListeners();
  }
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
