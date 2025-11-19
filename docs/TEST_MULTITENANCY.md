# 🧪 Guía de Prueba - Multitenancy Backend

## ✅ Backend está corriendo en: `http://localhost:8000`

---

## 📋 Pasos para Probar Multitenancy

### 1️⃣ **Registra DOS empresas diferentes**

**Empresa 1: Petrodrill**
```bash
POST http://localhost:8000/api/register/empresa-user/

{
  "razon_social": "Petrodrill",
  "email_contacto": "admin@petrodrill.com",
  "nombre_comercial": "Petrodrill S.A.",
  "username": "admin_petrodrill",
  "password": "petro123456",
  "email": "admin@petrodrill.com",
  "first_name": "Admin",
  "last_name": "Petrodrill"
}
```

**Empresa 2: Minería Plus**
```bash
POST http://localhost:8000/api/register/empresa-user/

{
  "razon_social": "Minería Plus",
  "email_contacto": "admin@mineriapluss.com",
  "nombre_comercial": "Minería Plus S.A.",
  "username": "admin_mineria",
  "password": "mineria123456",
  "email": "admin@mineria@plus.com",
  "first_name": "Admin",
  "last_name": "Minería"
}
```

---

### 2️⃣ **Login con cada empresa**

**Login Petrodrill:**
```bash
POST http://localhost:8000/api/auth/login/

{
  "username": "admin_petrodrill",
  "password": "petro123456"
}
```
✅ **Guarda el token de Petrodrill**

**Login Minería Plus:**
```bash
POST http://localhost:8000/api/auth/login/

{
  "username": "admin_mineria",
  "password": "mineria123456"
}
```
✅ **Guarda el token de Minería Plus**

---

### 3️⃣ **Crea clientes en cada empresa**

**Crear Cliente en Petrodrill:**
```bash
POST http://localhost:8000/api/cliente/

Authorization: Token <TOKEN_PETRODRILL>

{
  "nombre": "Juan",
  "apellido": "Pérez",
  "fecha_nacimiento": "1990-01-15"
}
```

**Crear Cliente en Minería Plus:**
```bash
POST http://localhost:8000/api/cliente/

Authorization: Token <TOKEN_MINERIA>

{
  "nombre": "Carlos",
  "apellido": "López",
  "fecha_nacimiento": "1985-05-20"
}
```

---

### 4️⃣ **⚠️ PRUEBA CRITICA: Multitenancy**

**Ahora PRUEBA LO IMPORTANTE:**

Con el **token de Petrodrill**, haz:
```bash
GET http://localhost:8000/api/cliente/

Authorization: Token <TOKEN_PETRODRILL>
```

✅ **DEBE mostrar SOLO el cliente de Petrodrill (Juan Pérez)**
❌ **NO debe mostrar el cliente de Minería Plus (Carlos López)**

---

Con el **token de Minería Plus**, haz:
```bash
GET http://localhost:8000/api/cliente/

Authorization: Token <TOKEN_MINERIA>
```

✅ **DEBE mostrar SOLO el cliente de Minería Plus (Carlos López)**
❌ **NO debe mostrar el cliente de Petrodrill (Juan Pérez)**

---

## 🔐 Endpoints con Multitenancy

Estos endpoints **FILTRAN AUTOMÁTICAMENTE** por empresa:

- ✅ `GET/POST /api/cliente/` - Clientes
- ✅ `GET/POST /api/creditos/` - Créditos
- ✅ `GET/POST /api/user/` - Usuarios
- ✅ `GET/POST /api/grupo/` - Grupos
- ✅ `GET/POST /api/suscripcion/` - Suscripciones
- ✅ `GET/POST /api/configuracion/` - Configuración
- ✅ `GET /api/historial/` - Historial de créditos
- ✅ `GET /api/historial/<ci>/` - Historial por CI

---

## 🛠️ Herramientas Recomendadas para Probar

### **Postman** (Recomendado)
1. Descarga: https://www.postman.com/downloads/
2. Crea una colección con los requests
3. Usa variables para guardar tokens

### **Insomnia**
1. Descarga: https://insomnia.rest/
2. Interfaz similar a Postman

### **cURL** (Línea de comandos)
```bash
curl -X GET http://localhost:8000/api/cliente/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json"
```

---

## 🎯 Checklist de Prueba

- [ ] Empresa 1 se registra exitosamente
- [ ] Empresa 2 se registra exitosamente
- [ ] Login de Empresa 1 genera token
- [ ] Login de Empresa 2 genera token
- [ ] Cliente creado en Empresa 1 aparece en lista de Empresa 1
- [ ] Cliente creado en Empresa 2 aparece en lista de Empresa 2
- [ ] Cliente de Empresa 1 **NO aparece** en lista de Empresa 2
- [ ] Cliente de Empresa 2 **NO aparece** en lista de Empresa 1
- [ ] Crédito creado en Empresa 1 solo visible en Empresa 1
- [ ] Usuario creado en Empresa 1 solo visible en Empresa 1

---

## 📞 Si hay errores:

1. **Error 403 Forbidden** → Token expirado o inválido
2. **Error 400 Bad Request** → Datos incompletos o inválidos
3. **Error 404 Not Found** → Endpoint no existe
4. **Error 500 Internal Server Error** → Revisar logs del servidor

---

**¡Listo para probar! El backend está corriendo en http://localhost:8000**
