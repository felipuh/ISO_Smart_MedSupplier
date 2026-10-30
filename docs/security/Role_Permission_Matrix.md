# Role Permission Matrix

| Role | Side | Private Cockpit | Private Financials | Quality | Logistics | Mutate |
| --- | --- | --- | --- | --- | --- | --- |
| Supplier Admin | Supplier | Yes | Yes | Yes | Yes | Yes |
| Supplier Finance | Supplier | Yes | Yes | No | No | Yes |
| Supplier Sales | Supplier | Yes | No | No | No | Yes |
| Supplier Quality | Supplier | No | No | Yes | No | Yes |
| Supplier Logistics | Supplier | No | No | No | Yes | Yes |
| Supplier Viewer | Supplier | No | No | Read | Read | No |
| Customer Admin | Customer | No | No | Shared | Shared | No |
| Customer Buyer | Customer | No | No | No | Shared | No |
| Customer Quality | Customer | No | No | Shared | No | No |
| Customer Logistics | Customer | No | No | No | Shared | No |
| Customer Auditor | Customer | No | No | Exportable shared | Exportable shared | No |
| Customer Viewer | Customer | No | No | Read shared | Read shared | No |
