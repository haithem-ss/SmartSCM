# Final Data

Synthetic order dataset for demonstration and testing.

## Structure

### `merged_data.csv`
Combined dataset with 24 orders from January 15-29, 2025. Contains all customers, products, and order types.

### `data_documentation.yaml`
Complete schema documentation including:
- Column descriptions
- Data types
- Business rules and constraints
- Sample values

### `data/`
Daily CSV files for date-range queries:
- `2025-01-15.csv` through `2025-01-29.csv`
- 3-5 orders per day
- Used by `data_loader_tool` for date-filtered analysis

## Dataset Schema

13 columns:
- `OrderID` - Unique order identifier
- `OrderDate` - Order placement date
- `DeliveryDate` - Expected delivery date
- `OrderType` - Standard or Express
- `Status` - Pending, In Transit, or Completed
- `CustomerName` - Business customer name
- `ProductName` - Product description
- `Quantity` - Order quantity
- `UnitPrice` - Price per unit
- `TotalAmount` - Total order value
- `ShippingAddress` - Delivery address
- `City` - Delivery city
- `Region` - US region (Northeast, West, Midwest, South)

## Note

This is **synthetic data** for demonstration. The original company dataset has been replaced to protect confidentiality.
