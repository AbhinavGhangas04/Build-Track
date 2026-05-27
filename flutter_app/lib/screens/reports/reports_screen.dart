import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/expense_provider.dart';
import '../../providers/project_provider.dart';
import '../../utils/theme.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Reports & Analytics'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Report Types
          _buildReportCard(
            'Expense Report',
            'View detailed expense breakdown',
            Icons.receipt_long,
            AppTheme.errorColor,
            () => _showExpenseReport(),
          ),
          const SizedBox(height: 12),
          _buildReportCard(
            'Income Report',
            'View income and client payments',
            Icons.account_balance_wallet,
            AppTheme.successColor,
            () => _showIncomeReport(),
          ),
          const SizedBox(height: 12),
          _buildReportCard(
            'Labour Report',
            'View labour costs and attendance',
            Icons.people,
            AppTheme.secondaryColor,
            () => _showLabourReport(),
          ),
          const SizedBox(height: 12),
          _buildReportCard(
            'Material Report',
            'View material usage and costs',
            Icons.inventory_2,
            AppTheme.accentColor,
            () => _showMaterialReport(),
          ),
          const SizedBox(height: 12),
          _buildReportCard(
            'Profit/Loss Report',
            'View overall project profitability',
            Icons.trending_up,
            AppTheme.primaryColor,
            () => _showProfitLossReport(),
          ),
          const SizedBox(height: 24),
          // Export Options
          const Text(
            'Export Reports',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildExportCard(
            'Export to Excel',
            'Download report as Excel file',
            Icons.table_chart,
            Colors.green,
            () => _exportToExcel(),
          ),
          const SizedBox(height: 12),
          _buildExportCard(
            'Export to PDF',
            'Download report as PDF file',
            Icons.picture_as_pdf,
            Colors.red,
            () => _exportToPDF(),
          ),
        ],
      ),
    );
  }

  Widget _buildReportCard(
    String title,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          child: Icon(icon, color: color),
        ),
        title: Text(title),
        subtitle: Text(description),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: onTap,
      ),
    );
  }

  Widget _buildExportCard(
    String title,
    String description,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.2),
          child: Icon(icon, color: color),
        ),
        title: Text(title),
        subtitle: Text(description),
        onTap: onTap,
      ),
    );
  }

  void _showExpenseReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Expense Report'),
        content: Consumer<ExpenseProvider>(
          builder: (context, expenseProvider, child) {
            final summary = expenseProvider.expenseSummary;
            return Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _reportRow('Total Expenses', '₹${(summary?['total_spent'] ?? 0).toStringAsFixed(2)}'),
                const SizedBox(height: 16),
                const Text('Expense by Category:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...expenseProvider.expenses
                    .where((e) => e['bill_type'] == 'expense')
                    .map((expense) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(expense['category'] ?? 'Other'),
                              Text('₹${(expense['amount'] ?? 0).toStringAsFixed(2)}'),
                            ],
                          ),
                        )),
              ],
            );
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showIncomeReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Income Report'),
        content: Consumer<ExpenseProvider>(
          builder: (context, expenseProvider, child) {
            final summary = expenseProvider.expenseSummary;
            return Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _reportRow('Total Income', '₹${(summary?['total_earned'] ?? 0).toStringAsFixed(2)}'),
                const SizedBox(height: 16),
                const Text('Income Sources:', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...expenseProvider.expenses
                    .where((e) => e['bill_type'] == 'income')
                    .map((expense) => Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(expense['description'] ?? 'Unknown'),
                              Text('₹${(expense['amount'] ?? 0).toStringAsFixed(2)}'),
                            ],
                          ),
                        )),
              ],
            );
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showLabourReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Labour Report'),
        content: const Text('Labour report feature coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showMaterialReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Material Report'),
        content: const Text('Material report feature coming soon!'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showProfitLossReport() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Profit/Loss Report'),
        content: Consumer<ExpenseProvider>(
          builder: (context, expenseProvider, child) {
            final summary = expenseProvider.expenseSummary;
            final income = summary?['total_earned']?.toDouble() ?? 0.0;
            final expense = summary?['total_spent']?.toDouble() ?? 0.0;
            final profit = income - expense;

            return Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _reportRow('Total Income', '₹${income.toStringAsFixed(2)}'),
                _reportRow('Total Expenses', '₹${expense.toStringAsFixed(2)}'),
                const Divider(),
                _reportRow(
                  'Profit/Loss',
                  '₹${profit.toStringAsFixed(2)}',
                  profit >= 0 ? Colors.green : Colors.red,
                ),
                _reportRow(
                  'Profit Margin',
                  '${income > 0 ? (profit / income * 100).toStringAsFixed(1) : 0}%',
                  profit >= 0 ? Colors.green : Colors.red,
                ),
              ],
            );
          },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _exportToExcel() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Excel export feature coming soon!')),
    );
  }

  void _exportToPDF() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('PDF export feature coming soon!')),
    );
  }

  Widget _reportRow(String label, String value, [Color? color]) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
