# 🚀 Backend SI2 - Quick Start

## Instalación Rápida

### 1. Crear ambiente virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Aplicar migraciones
```powershell
python manage.py migrate
```

### 4. Setup automático (crea datos de prueba)
```powershell
python setup_sistema.py
```

Este comando crea:
- ✅ Empresa de prueba
- ✅ Superusuario (admin/admin123)
- ✅ Usuario normal (usuario1/usuario123)
- ✅ 4 tipos de crédito

### 5. Iniciar servidor
```powershell
python manage.py runserver 8000
```

---

## URLs Importantes

- 🌐 **API Base:** http://127.0.0.1:8000/api/
- 👨‍💼 **Admin:** http://127.0.0.1:8000/admin/
- 📝 **Documentación API:** http://127.0.0.1:8000/api/docs/
- 🧪 **Test Tipos Crédito:** http://127.0.0.1:8000/api/Creditos/test/tipos/

---

## API Endpoints Principales

### Tipos de Crédito
- `GET /api/Creditos/tipo-creditos/` - Listar tipos
- `POST /api/Creditos/tipo-creditos/` - Crear tipo
- `PATCH /api/Creditos/tipo-creditos/{id}/` - Editar tipo
- `DELETE /api/Creditos/tipo-creditos/{id}/` - Eliminar tipo

### Créditos
- `GET /api/Creditos/creditos/` - Listar créditos
- `POST /api/Creditos/creditos/` - Crear crédito
- `GET /api/Creditos/creditos/{id}/` - Ver crédito
- `GET /api/Creditos/creditos/{id}/estado-actual/` - Ver estado actual
- `GET /api/Creditos/creditos/{id}/linea-tiempo/` - Ver historial

### Workflow de Fases
- `PATCH /api/Creditos/creditos/{id}/agregar-documentacion/` - Pasar a FASE_2
- `PATCH /api/Creditos/creditos/{id}/agregar-laboral/` - Pasar a FASE_3
- `PATCH /api/Creditos/creditos/{id}/agregar-domicilio/` - Pasar a FASE_4
- `PATCH /api/Creditos/creditos/{id}/agregar-garante/` - Pasar a FASE_5
- `PATCH /api/Creditos/creditos/{id}/enviar-revision/` - Pasar a FASE_6
- `PATCH /api/Creditos/creditos/{id}/revisar/` - Pasar a FASE_7/RECHAZADO
- `PATCH /api/Creditos/creditos/{id}/desembolsar/` - Pasar a FASE_8

---

## Características

✅ **Multitenancy:** Cada empresa ve solo sus propios datos  
✅ **Workflow de Fases:** 8 fases de solicitud a finalización  
✅ **Auditoría:** Historial completo de cambios (HistoricoCredito)  
✅ **Validaciones:** Validaciones en cada fase  
✅ **Token Auth:** Autenticación por token  

---

## Troubleshooting

**Q: "Address already in use"**
```powershell
python manage.py runserver 8001  # Usa otro puerto
```

**Q: Errores de migración**
```powershell
python manage.py showmigrations
python manage.py migrate --fake-initial  # Si es necesario
```

**Q: Reset completo de la BD**
```powershell
rm db.sqlite3
python manage.py migrate
python setup_sistema.py
```

---

## Estructura de Modelos

```
Tipo_Credito
  - nombre
  - descripcion
  - monto_minimo
  - monto_maximo
  - empresa (FK)

Credito
  - Monto_Solicitado
  - enum_estado
  - fase_actual (FASE_1 -> FASE_8)
  - Numero_Cuotas
  - Monto_Cuota
  - Tasa_Interes
  - Moneda
  - cliente (FK)
  - tipo_credito (FK)
  - empresa (FK)
  - usuario (FK)
  - fecha_creacion
  - fecha_actualizacion

HistoricoCredito
  - credito (FK)
  - fase_anterior
  - fase_nueva
  - fecha_cambio
  - usuario_cambio
  - datos_agregados (JSON)
  
Ganancia_Credito
  - monto_prestado
  - tasa_interes
  - duracion_meses
  - ganancia_esperada
```

---

¡Listo para probar! 🎉
