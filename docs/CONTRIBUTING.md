# Guía de Contribución

## Flujo de trabajo en parejas

1. **Crear ramas por feature**
   ```bash
   git checkout -b feature/nombre-feature
   ```

2. **Hacer commits descriptivos**
   ```bash
   git commit -m "feat: descripción clara del cambio"
   ```

3. **Hacer pull request para revisión**
   - Describe los cambios
   - Referencia issues si aplica

## Estándares de código

- Usar snake_case para variables y funciones
- Agregar docstrings en todas las funciones
- Máximo 100 caracteres por línea
- Usar type hints cuando sea posible

## Testing

- Escribir tests para nuevas funcionalidades
- Ejecutar: `pytest tests/`

