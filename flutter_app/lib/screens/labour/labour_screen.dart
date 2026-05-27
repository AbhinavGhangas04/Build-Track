import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/labour_provider.dart';
import '../../utils/theme.dart';

class LabourScreen extends StatefulWidget {
  const LabourScreen({super.key});

  @override
  State<LabourScreen> createState() => _LabourScreenState();
}

class _LabourScreenState extends State<LabourScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      Provider.of<LabourProvider>(context, listen: false).fetchWorkers();
      Provider.of<LabourProvider>(context, listen: false).fetchAttendanceSummary();
    });
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Labour Management'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Workers'),
              Tab(text: 'Attendance'),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () => _showAddWorkerDialog(),
            ),
          ],
        ),
        body: const TabBarView(
          children: [
            WorkersTab(),
            AttendanceTab(),
          ],
        ),
      ),
    );
  }

  void _showAddWorkerDialog() {
    final nameController = TextEditingController();
    final roleController = TextEditingController();
    final wageController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Worker'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Worker Name',
                  hintText: 'Enter worker name',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: roleController,
                decoration: const InputDecoration(
                  labelText: 'Role',
                  hintText: 'e.g., Mason, Carpenter',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: wageController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Daily Wage (₹)',
                  hintText: 'Enter daily wage',
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.isNotEmpty) {
                final labourProvider = Provider.of<LabourProvider>(context, listen: false);
                await labourProvider.addWorker({
                  'name': nameController.text,
                  'role': roleController.text,
                  'daily_wage': double.tryParse(wageController.text) ?? 0,
                });
                if (mounted) {
                  Navigator.pop(context);
                }
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}

class WorkersTab extends StatelessWidget {
  const WorkersTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<LabourProvider>(
      builder: (context, labourProvider, child) {
        if (labourProvider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        if (labourProvider.workers.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.people, size: 64, color: Colors.grey[400]),
                const SizedBox(height: 16),
                Text(
                  'No workers yet',
                  style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: labourProvider.workers.length,
          itemBuilder: (context, index) {
            final worker = labourProvider.workers[index];
            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: AppTheme.secondaryColor,
                  child: Text(
                    worker['name']?.toString().substring(0, 1).toUpperCase() ?? 'W',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
                title: Text(worker['name'] ?? 'Unknown'),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Role: ${worker['role'] ?? 'N/A'}'),
                    Text('Daily Wage: ₹${worker['daily_wage'] ?? 0}'),
                  ],
                ),
                trailing: IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => _deleteWorker(context, worker['id']),
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _deleteWorker(BuildContext context, int? workerId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Worker'),
        content: const Text('Are you sure you want to delete this worker?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (workerId != null) {
                final labourProvider = Provider.of<LabourProvider>(context, listen: false);
                await labourProvider.deleteWorker(workerId);
                if (context.mounted) {
                  Navigator.pop(context);
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class AttendanceTab extends StatelessWidget {
  const AttendanceTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<LabourProvider>(
      builder: (context, labourProvider, child) {
        final summary = labourProvider.attendanceSummary;

        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Attendance Summary
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      const Text(
                        'Today\'s Attendance',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildAttendanceStat('Present', summary?['present_today'] ?? 0, Colors.green),
                          _buildAttendanceStat('Absent', summary?['absent_today'] ?? 0, Colors.red),
                          _buildAttendanceStat('Holiday', summary?['on_leave_today'] ?? 0, Colors.orange),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Mark Attendance Button
              ElevatedButton.icon(
                onPressed: () => _showMarkAttendanceDialog(context),
                icon: const Icon(Icons.check_circle),
                label: const Text('Mark Attendance'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAttendanceStat(String label, int count, Color color) {
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$count',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(label),
      ],
    );
  }

  void _showMarkAttendanceDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Mark Attendance'),
        content: const Text('Attendance marking feature coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
