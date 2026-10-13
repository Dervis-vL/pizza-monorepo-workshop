# pizza-client 🔌

Two adapters for one port (`pizza_shared.ports.PizzeriaSource`):

| Adapter | Reads from | When |
|---|---|---|
| `FixturePizzeriaSource` | `data/pizzerias.json` | default, works offline |
| `HttpPizzeriaSource` | the live pizza platform API | `PIZZA_SOURCE=http` |

Both go through the same `mapping.parse_api_payload`, so the app never sees the
API's wire format. Pick one with `pizzeria_source(ClientSettings())`.
