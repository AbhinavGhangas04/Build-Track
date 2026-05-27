import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../providers/auth_provider.dart';
import '../../providers/project_provider.dart';
import '../../providers/expense_provider.dart';
import '../../providers/labour_provider.dart';
import '../../providers/material_provider.dart';
import '../../providers/payment_provider.dart';
import '../../providers/notification_provider.dart';
import '../../utils/theme.dart';
import '../../utils/constants.dart';
import '../projects/projects_screen.dart';
import '../expenses/expenses_screen.dart';
import '../labour/labour_screen.dart';
import '../materials/materials_screen.dart';
import '../payments/payments_screen.dart';
import '../reports/reports_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardHome(),
    const ProjectsScreen(),
    const ExpensesScreen(),
    const LabourScreen(),
    const MaterialsScreen(),
    const PaymentsScreen(),
    const ReportsScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final expenseProvider = Provider.of<ExpenseProvider>(context, listen: false);
    final labourProvider = Provider.of<LabourProvider>(context, listen: false);
    final materialProvider = Provider.of<MaterialProvider>(context, listen: false);
    final paymentProvider = Provider.of<PaymentProvider>(context, listen: false);
    final notificationProvider = Provider.of<NotificationProvider>(context, listen: false);

    await Future.wait([
      projectProvider.fetchProjects(),
      expenseProvider.fetchExpenses(),
      expenseProvider.fetchExpenseSummary(),
      labourProvider.fetchWorkers(),
      labourProvider.fetchAttendanceSummary(),
      materialProvider.fetchMaterials(),
      materialProvider.fetchMaterialSummary(),
      paymentProvider.fetchPayments(),
      paymentProvider.fetchPaymentSummary(),
      notificationProvider.fetchUnreadCount(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.location_city),
            label: 'Sites',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long),
            label: 'Expenses',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: 'Labour',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.inventory_2),
            label: 'Materials',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.payments),
            label: 'Payments',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assessment),
            label: 'Reports',
          ),
        ],
      ),
    );
  }
}

class DashboardHome extends StatelessWidget {
  const DashboardHome({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          Consumer<NotificationProvider>(
            builder: (context, notificationProvider, child) {
              return Stack(
                children: [
                  IconButton(
                    icon: const Icon(Icons.notifications),
                    onPressed: () {
                      // TODO: Navigate to notifications screen
                    },
                  ),
                  if (notificationProvider.unreadCount > 0)
                    Positioned(
                      right: 8,
                      top: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.red,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 18,
                          minHeight: 18,
                        ),
                        child: Text(
                          '${notificationProvider.unreadCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Provider.of<AuthProvider>(context, listen: false).logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
          final expenseProvider = Provider.of<ExpenseProvider>(context, listen: false);
          final labourProvider = Provider.of<LabourProvider>(context, listen: false);
          final materialProvider = Provider.of<MaterialProvider>(context, listen: false);
          final paymentProvider = Provider.of<PaymentProvider>(context, listen: false);

          await Future.wait([
            projectProvider.fetchProjects(),
            expenseProvider.fetchExpenses(),
            expenseProvider.fetchExpenseSummary(),
            labourProvider.fetchWorkers(),
            materialProvider.fetchMaterials(),
            paymentProvider.fetchPayments(),
          ]);
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
              Consumer<AuthProvider>(
                builder: (context, authProvider, child) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome, ${authProvider.user?['company_name'] ?? 'Contractor'}!',
                        style: Theme.of(context).textTheme.displaySmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Here\'s your project overview',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 24),

              // Financial Summary Cards
              Consumer<ExpenseProvider>(
                builder: (context, expenseProvider, child) {
                  final summary = expenseProvider.expenseSummary;
                  final totalIncome = summary?['total_earned']?.toDouble() ?? 0.0;
                  final totalExpense = summary?['total_spent']?.toDouble() ?? 0.0;
                  final profit = totalIncome - totalExpense;

                  return Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Total Income',
                          '₹${totalIncome.toStringAsFixed(2)}',
                          Icons.arrow_upward,
                          AppTheme.successColor,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Total Expense',
                          '₹${totalExpense.toStringAsFixed(2)}',
                          Icons.arrow_downward,
                          AppTheme.errorColor,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Profit/Loss',
                          '₹${profit.toStringAsFixed(2)}',
                          profit >= 0 ? Icons.trending_up : Icons.trending_down,
                          profit >= 0 ? AppTheme.successColor : AppTheme.errorColor,
                        ),
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 24),

              // Project Stats
              Consumer3<ProjectProvider, LabourProvider, MaterialProvider>(
                builder: (context, projectProvider, labourProvider, materialProvider, child) {
                  return Row(
                    children: [
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Active Sites',
                          '${projectProvider.projects.length}',
                          Icons.location_city,
                          AppTheme.primaryColor,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Workers',
                          '${labourProvider.workers.length}',
                          Icons.people,
                          AppTheme.secondaryColor,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _buildStatCard(
                          context,
                          'Materials',
                          '${materialProvider.materials.length}',
                          Icons.inventory_2,
                          AppTheme.accentColor,
                        ),
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 24),

              // Expense Chart
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Expense Breakdown',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 200,
                        child: Consumer<ExpenseProvider>(
                          builder: (context, expenseProvider, child) {
                            return PieChart(
                              PieChartData(
                                sections: _getExpenseSections(expenseProvider.expenses),
                                sectionsSpace: 2,
                                centerSpaceRadius: 40,
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Recent Activity
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Recent Activity',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 16),
                      Consumer<ExpenseProvider>(
                        builder: (context, expenseProvider, child) {
                          final recentExpenses = expenseProvider.expenses.take(5).toList();
                          if (recentExpenses.isEmpty) {
                            return const Center(
                              child: Padding(
                                padding: EdgeInsets.all(24),
                                child: Text('No recent activity'),
                              ),
                            );
                          }
                          return ListView.builder(
                            shrinkWrap: true,
                            physics: const NeverScrollableScrollPhysics(),
                            itemCount: recentExpenses.length,
                            itemBuilder: (context, index) {
                              final expense = recentExpenses[index];
                              return ListTile(
                                leading: Icon(
                                  expense['bill_type'] == 'income'
                                      ? Icons.arrow_upward
                                      : Icons.arrow_downward,
                                  color: expense['bill_type'] == 'income'
                                      ? AppTheme.successColor
                                      : AppTheme.errorColor,
                                ),
                                title: Text(expense['description'] ?? 'Unknown'),
                                subtitle: Text(expense['bill_date'] ?? ''),
                                trailing: Text(
                                  '₹${(expense['amount'] ?? 0).toStringAsFixed(2)}',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: expense['bill_type'] == 'income'
                                        ? AppTheme.successColor
                                        : AppTheme.errorColor,
                                  ),
                                ),
                              );
                            },
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  List<PieChartSectionData> _getExpenseSections(List<Map<String, dynamic>> expenses) {
    final categoryTotals = <String, double>{};
    for (final expense in expenses) {
      if (expense['bill_type'] == 'expense') {
        final category = expense['category'] ?? 'Other';
        categoryTotals[category] = (categoryTotals[category] ?? 0) + (expense['amount']?.toDouble() ?? 0);
      }
    }

    final sections = <PieChartSectionData>[];
    int colorIndex = 0;
    for (final entry in categoryTotals.entries) {
      sections.add(
        PieChartSectionData(
          value: entry.value,
          title: '${entry.key}\n₹${entry.value.toStringAsFixed(0)}',
          color: AppConstants.chartColors[colorIndex % AppConstants.chartColors.length],
          radius: 50,
          titleStyle: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      );
      colorIndex++;
    }

    return sections.isEmpty
        ? [
            PieChartSectionData(
              value: 1,
              title: 'No Data',
              color: Colors.grey,
              radius: 50,
            ),
          ]
        : sections;
  }
}
