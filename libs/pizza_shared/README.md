# pizza-shared 🧱

The one package everyone imports. It holds the vocabulary of the platform:

- `schemas`: `Pizzeria` and `Ranking`, the pydantic models every member speaks.
- `ports`: `PizzeriaSource`, the Protocol an adapter implements to supply pizzerias.

It has one dependency (pydantic) on purpose. Keep it that way: everything that
depends on this package inherits its dependency tree.
