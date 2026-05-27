import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/payment_provider.dart';
import '../../utils/theme.dart';
import '../../utils/constants.dart';

class PaymentsScreen extends StatefulWidget {
  const PaymentsScreen({super.key});

  @override
  State<PaymentsScreen> createState() => _PaymentsScreenState();
}

class _PaymentsScreenState extends State<PaymentsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      Provider.of<PaymentProvider>(context, listen: false).fetchPayments();
      Provider.of<PaymentProvider>(context, listen: false).fetchPaymentSummary();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Client Payments'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddPaymentDialog(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Summary Cards
          Consumer<PaymentProvider>(
            builder: (context, paymentProvider, child) {
              final summary = paymentProvider.paymentSummary;
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: _buildSummaryCard(
                        'Received',
                        '₹${(summary?['total_received'] ?? 0).toStringAsFixed(2)}',
                        AppTheme.successColor,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _buildSummaryCard(
                        'Pending',
                        '₹${(summary?['pending_amount'] ?? 0).toStringAsFixed(2)}',
                        AppTheme.warningColor,
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
          // Payments List
          Expanded(
            child: Consumer<PaymentProvider>(
              builder: (context, paymentProvider, child) {
                if (paymentProvider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (paymentProvider.payments.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.payments, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          'No payments yet',
                          style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: paymentProvider.payments.length,
                  itemBuilder: (context, index) {
                    final payment = paymentProvider.payments[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: payment['status'] == 'paid'
                              ? AppTheme.successColor
                              : AppTheme.warningColor,
                          child: Icon(
                            payment['status'] == 'paid' ? Icons.check : Icons.pending,
                            color: Colors.white,
                          ),
                        ),
                        title: Text('${payment['payment_type']?.toString().toUpperCase() ?? 'PAYMENT'}'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Amount: ₹${(payment['amount'] ?? 0).toStringAsFixed(2)}'),
                            Text('Date: ${payment['payment_date'] ?? ''}'),
                            if (payment['due_date'] != null)
                              Text('Due: ${payment['due_date']}'),
                          ],
                        ),
                        trailing: Chip(
                          label: Text(payment['status'] ?? 'Pending'),
                          backgroundColor: payment['status'] == 'paid'
                              ? Colors.green.withOpacity(0.2)
                              : Colors.orange.withOpacity(0.2),
                        ),
                        onTap: () => _showPaymentDetails(payment),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(String title, String value, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAddPaymentDialog() {
    final amountController = TextEditingController();
    String selectedType = 'advance';
    final descriptionController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Payment'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: amountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Amount (₹)',
                  hintText: 'Enter amount',
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: selectedType,
                decoration: const InputDecoration(labelText: 'Payment Type'),
                items: AppConstants.paymentTypes
                    .map((type) => DropdownMenuItem(value: type.toLowerCase(), child: Text(type)))
                    .toList(),
                onChanged: (value) => selectedType = value!,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  hintText: 'Enter description',
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
              if (amountController.text.isNotEmpty) {
                final paymentProvider = Provider.of<PaymentProvider>(context, listen: false);
                await paymentProvider.createPayment({
                  'amount': double.tryParse(amountController.text) ?? 0,
                  'payment_type': selectedType,
                  'description': descriptionController.text,
                  'status': 'pending',
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

  void _showPaymentDetails(Map<String, dynamic> payment) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${payment['payment_type']?.toString().toUpperCase() ?? 'PAYMENT'} Details'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _detailRow('Amount', '₹${(payment['amount'] ?? 0).toStringAsFixed(2)}'),
              _detailRow('Type', payment['payment_type']),
              _detailRow('Status', payment['status']),
              _detailRow('Payment Date', payment['payment_date']),
              _detailRow('Due Date', payment['due_date']),
              _detailRow('Description', payment['description']),
            ],
          ),
        ),
        actions: [
          if (payment['status'] != 'paid')
            ElevatedButton(
              onPressed: () async {
                final paymentProvider = Provider.of<PaymentProvider>(context, listen: false);
                await paymentProvider.updatePaymentStatus(payment['id'], 'paid');
                if (context.mounted) {
                  Navigator.pop(context);
                }
              },
              child: const Text('Mark as Paid'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _detailRow(String label, dynamic value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value?.toString() ?? 'N/A')),
        ],
      ),
    );
  }
}
