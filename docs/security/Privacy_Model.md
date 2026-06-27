# Privacy Model

Organization is the Supplier tenant boundary. Account is the Customer scope boundary. Customer users require an active `MedSupplierUserScope` with account assignment. Supplier private fields and private classifications are denied through backend querysets and serializer field filtering.

Private commercial fields include margin notes, supplier cost, margin, commission, advance, internal notes, forecast, and private cockpit data.
