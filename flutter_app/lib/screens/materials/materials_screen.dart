import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/material_provider.dart';
import '../../utils/theme.dart';
import '../../utils/constants.dart';

class MaterialsScreen extends StatefulWidget {
  const MaterialsScreen({super.key});

  @override
  State<MaterialsScreen> createState() => _MaterialsScreenState();
}

class _MaterialsScreenState extends State<MaterialsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      Provider.of<MaterialProvider>(context, listen: false).fetchMaterials();
      Provider.of<MaterialProvider>(context, listen: false).fetchMaterialSummary();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Materials'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddMaterialDialog(),
          ),
        ],
      ),
      body: Column(
        children: [
          // Summary Card
          Consumer<MaterialProvider>(
            builder: (context, materialProvider, child) {
              final summary = materialProvider.materialSummary;
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        const Text(
                          'Material Summary',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            _buildSummaryItem('Total', '${summary?['total_materials'] ?? 0}'),
                            _buildSummaryItem('Value', '₹${(summary?['total_value'] ?? 0).toStringAsFixed(0)}'),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
          // Materials List
          Expanded(
            child: Consumer<MaterialProvider>(
              builder: (context, materialProvider, child) {
                if (materialProvider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (materialProvider.materials.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.inventory_2, size: 64, color: Colors.grey[400]),
                        const SizedBox(height: 16),
                        Text(
                          'No materials yet',
                          style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: materialProvider.materials.length,
                  itemBuilder: (context, index) {
                    final material = materialProvider.materials[index];
                    final remaining = (material['remaining_quantity'] ?? 0).toDouble();
                    final total = (material['total_quantity'] ?? 0).toDouble();
                    final percentage = total > 0 ? (remaining / total * 100) : 0;

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: AppTheme.accentColor,
                          child: const Icon(Icons.inventory, color: Colors.white),
                        ),
                        title: Text(material['name'] ?? 'Unknown Material'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Category: ${material['category'] ?? 'N/A'}'),
                            const SizedBox(height: 4),
                            LinearProgressIndicator(
                              value: percentage / 100,
                              backgroundColor: Colors.grey[300],
                              color: percentage < 20 ? Colors.red : AppTheme.accentColor,
                            ),
                            Text('$remaining of $total ${material['unit'] ?? 'units'} remaining ($percentage.toStringAsFixed(0)%)'),
                          ],
                        ),
                        trailing: IconButton(
                          icon: const Icon(Icons.delete, color: Colors.red),
                          onPressed: () => _deleteMaterial(context, material['id']),
                        ),
                        onTap: () => _showMaterialDetails(material),
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

  Widget _buildSummaryItem(String label, String value) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.grey),
        ),
      ],
    );
  }

  void _showAddMaterialDialog() {
    final nameController = TextEditingController();
    final categoryController = TextEditingController();
    final quantityController = TextEditingController();
    final unitController = TextEditingController();
    final priceController = TextEditingController();
    final supplierController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Material'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Material Name',
                  hintText: 'Enter material name',
                ),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: 'Cement',
                decoration: const InputDecoration(labelText: 'Category'),
                items: AppConstants.materialCategories
                    .map((cat) => DropdownMenuItem(value: cat, child: Text(cat)))
                    .toList(),
                onChanged: (value) => categoryController.text = value!,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: quantityController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Total Quantity',
                  hintText: 'Enter total quantity',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: unitController,
                decoration: const InputDecoration(
                  labelText: 'Unit',
                  hintText: 'e.g., bags, kg, pieces',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: priceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Unit Price (₹)',
                  hintText: 'Enter unit price',
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: supplierController,
                decoration: const InputDecoration(
                  labelText: 'Supplier Name',
                  hintText: 'Enter supplier name',
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
              if (nameController.text.isNotEmpty && quantityController.text.isNotEmpty) {
                final materialProvider = Provider.of<MaterialProvider>(context, listen: false);
                await materialProvider.createMaterial({
                  'name': nameController.text,
                  'category': categoryController.text,
                  'total_quantity': double.tryParse(quantityController.text) ?? 0,
                  'unit': unitController.text,
                  'unit_price': double.tryParse(priceController.text) ?? 0,
                  'supplier_name': supplierController.text,
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

  void _showMaterialDetails(Map<String, dynamic> material) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(material['name'] ?? 'Material Details'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _detailRow('Category', material['category']),
              _detailRow('Total Quantity', '${material['total_quantity']} ${material['unit']}'),
              _detailRow('Used Quantity', '${material['used_quantity']} ${material['unit']}'),
              _detailRow('Remaining', '${material['remaining_quantity']} ${material['unit']}'),
              _detailRow('Unit Price', '₹${material['unit_price']}'),
              _detailRow('Supplier', material['supplier_name']),
            ],
          ),
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

  void _deleteMaterial(BuildContext context, int? materialId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Material'),
        content: const Text('Are you sure you want to delete this material?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (materialId != null) {
                final materialProvider = Provider.of<MaterialProvider>(context, listen: false);
                await materialProvider.deleteMaterial(materialId);
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
