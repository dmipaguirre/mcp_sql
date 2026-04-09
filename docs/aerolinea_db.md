# Base de Datos - Aerolínea

---

## Entidades y Atributos

---

### 1. Pasajero

| Atributo           | Tipo          | Restricciones                          |
| ------------------- | ------------- | -------------------------------------- |
| `id_pasajero`       | INT           | PK, AUTO_INCREMENT                     |
| `nombre`            | VARCHAR(100)  | NOT NULL                               |
| `apellido`          | VARCHAR(100)  | NOT NULL                               |
| `tipo_documento`    | VARCHAR(20)   | NOT NULL (DNI, PASAPORTE)              |
| `numero_documento`  | VARCHAR(50)   | NOT NULL, UNIQUE                       |
| `email`             | VARCHAR(100)  | NOT NULL, UNIQUE                       |
| `telefono`          | VARCHAR(20)   |                                        |
| `fecha_nacimiento`  | DATE          |                                        |
| `pais`              | VARCHAR(50)   |                                        |

---

### 2. Empleado

| Atributo             | Tipo          | Restricciones              |
| --------------------- | ------------- | -------------------------- |
| `id_empleado`         | INT           | PK, AUTO_INCREMENT         |
| `nombre`              | VARCHAR(100)  | NOT NULL                   |
| `apellido`            | VARCHAR(100)  | NOT NULL                   |
| `cargo`               | VARCHAR(50)   | NOT NULL                   |
| `departamento`        | VARCHAR(50)   | NOT NULL                   |
| `fecha_contratacion`  | DATE          | NOT NULL                   |
| `licencia`            | VARCHAR(50)   | (para pilotos)             |
| `email`               | VARCHAR(100)  | NOT NULL, UNIQUE           |
| `estado`              | VARCHAR(20)   | DEFAULT 'ACTIVO'           |

---

### 3. Aeronave

| Atributo              | Tipo          | Restricciones              |
| ---------------------- | ------------- | -------------------------- |
| `id_aeronave`          | INT           | PK, AUTO_INCREMENT         |
| `matricula`            | VARCHAR(20)   | NOT NULL, UNIQUE           |
| `modelo`               | VARCHAR(50)   | NOT NULL                   |
| `fabricante`           | VARCHAR(50)   |                            |
| `capacidad_primera`    | INT           | DEFAULT 0                  |
| `capacidad_economica`  | INT           | NOT NULL                   |
| `capacidad_total`      | INT           | NOT NULL                   |
| `año_fabricacion`      | YEAR          |                            |
| `estado`               | VARCHAR(20)   | DEFAULT 'ACTIVA'           |

---

### 4. Aeropuerto

| Atributo        | Tipo          | Restricciones              |
| ---------------- | ------------- | -------------------------- |
| `id_aeropuerto`  | INT           | PK, AUTO_INCREMENT         |
| `codigo_iata`    | VARCHAR(3)    | NOT NULL, UNIQUE           |
| `nombre`         | VARCHAR(100)  | NOT NULL                   |
| `ciudad`         | VARCHAR(50)   | NOT NULL                   |
| `pais`           | VARCHAR(50)   | NOT NULL                   |
| `timezone`       | VARCHAR(50)   |                            |

---

### 5. Ruta

| Atributo                 | Tipo          | Restricciones              |
| ------------------------- | ------------- | -------------------------- |
| `id_ruta`                 | INT           | PK, AUTO_INCREMENT         |
| `id_aeropuerto_origen`    | INT           | FK → Aeropuerto, NOT NULL  |
| `id_aeropuerto_destino`   | INT           | FK → Aeropuerto, NOT NULL  |
| `distancia_km`            | DECIMAL(10,2) |                            |
| `tiempo_estimado`         | TIME          |                            |
| `estado`                  | VARCHAR(20)   | DEFAULT 'ACTIVA'           |

---

### 6. Vuelo

| Atributo          | Tipo          | Restricciones              |
| ------------------ | ------------- | -------------------------- |
| `id_vuelo`         | INT           | PK, AUTO_INCREMENT         |
| `numero_vuelo`     | VARCHAR(10)   | NOT NULL                   |
| `id_ruta`          | INT           | FK → Ruta, NOT NULL        |
| `id_aeronave`      | INT           | FK → Aeronave, NOT NULL    |
| `fecha_salida`     | DATE          | NOT NULL                   |
| `hora_salida`      | TIME          | NOT NULL                   |
| `fecha_llegada`    | DATE          | NOT NULL                   |
| `hora_llegada`     | TIME          | NOT NULL                   |
| `estado`           | VARCHAR(20)   | DEFAULT 'PROGRAMADO'       |
| `precio_base`      | DECIMAL(10,2) |                            |

---

### 7. Reserva

| Atributo          | Tipo          | Restricciones              |
| ------------------ | ------------- | -------------------------- |
| `id_reserva`       | INT           | PK, AUTO_INCREMENT         |
| `id_pasajero`      | INT           | FK → Pasajero, NOT NULL    |
| `id_vuelo`         | INT           | FK → Vuelo, NOT NULL       |
| `codigo_reserva`   | VARCHAR(10)   | NOT NULL, UNIQUE           |
| `fecha_reserva`    | DATETIME      | NOT NULL                   |
| `estado_reserva`   | VARCHAR(20)   | DEFAULT 'PENDIENTE'        |
| `total`            | DECIMAL(10,2) |                            |
| `observaciones`    | TEXT          |                            |

---

### 8. Boleto

| Atributo          | Tipo          | Restricciones              |
| ------------------ | ------------- | -------------------------- |
| `id_boleto`        | INT           | PK, AUTO_INCREMENT         |
| `id_reserva`       | INT           | FK → Reserva, NOT NULL     |
| `id_vuelo`         | INT           | FK → Vuelo, NOT NULL       |
| `numero_boleto`    | VARCHAR(20)   | NOT NULL, UNIQUE           |
| `numero_asiento`   | VARCHAR(5)    |                            |
| `clase`            | VARCHAR(20)   | PRIMERA / ECONOMY / BUSINESS |
| `precio`           | DECIMAL(10,2) | NOT NULL                   |
| `estado_boleto`    | VARCHAR(20)   | DEFAULT 'EMITIDO'          |
| `fecha_emision`    | DATETIME      |                            |

---

### 9. Equipaje

| Atributo          | Tipo          | Restricciones              |
| ------------------ | ------------- | -------------------------- |
| `id_equipaje`      | INT           | PK, AUTO_INCREMENT         |
| `id_boleto`        | INT           | FK → Boleto, NOT NULL      |
| `peso_kg`          | DECIMAL(5,2)  | NOT NULL                   |
| `tag_equipaje`     | VARCHAR(20)   | NOT NULL, UNIQUE           |
| `tipo`             | VARCHAR(20)   | DOCUMENTADO / MANO         |
| `descripcion`      | VARCHAR(100)  |                            |
| `estado`           | VARCHAR(20)   | DEFAULT 'REGISTRADO'       |

---

### 10. Tripulacion

| Atributo           | Tipo        | Restricciones              |
| ------------------- | ----------- | -------------------------- |
| `id_tripulacion`    | INT         | PK, AUTO_INCREMENT         |
| `id_vuelo`          | INT         | FK → Vuelo, NOT NULL       |
| `id_empleado`       | INT         | FK → Empleado, NOT NULL    |
| `rol`               | VARCHAR(20) | PILOTO / COPILOTO / SOBRECARGO |

---

### 11. Mantenimiento

| Atributo                  | Tipo          | Restricciones              |
| -------------------------- | ------------- | -------------------------- |
| `id_mantenimiento`         | INT           | PK, AUTO_INCREMENT         |
| `id_aeronave`              | INT           | FK → Aeronave, NOT NULL    |
| `tipo_mantenimiento`       | VARCHAR(50)   | NOT NULL                   |
| `fecha_inicio`             | DATE          | NOT NULL                   |
| `fecha_fin`                | DATE          |                            |
| `descripcion`              | TEXT          |                            |
| `costo`                    | DECIMAL(10,2) |                            |
| `estado`                   | VARCHAR(20)   | DEFAULT 'EN_PROCESO'       |
| `id_empleado_responsable`  | INT           | FK → Empleado              |

---

### 12. Pago

| Atributo       | Tipo          | Restricciones              |
| --------------- | ------------- | -------------------------- |
| `id_pago`       | INT           | PK, AUTO_INCREMENT         |
| `id_reserva`    | INT           | FK → Reserva, NOT NULL     |
| `monto`         | DECIMAL(10,2) | NOT NULL                   |
| `metodo_pago`   | VARCHAR(30)   | TARJETA / EFECTIVO / TRANSFERENCIA |
| `fecha_pago`    | DATETIME      | NOT NULL                   |
| `estado`        | VARCHAR(20)   | DEFAULT 'PENDIENTE'        |
| `referencia`    | VARCHAR(50)   |                            |

---

### Detalle de Relaciones

| Relación       | Origen        | Destino       | Cardinalidad | Descripción                              |
| -------------- | ------------- | ------------- | ------------ | ---------------------------------------- |
| Realiza        | Pasajero      | Reserva       | 1:N          | Un pasajero puede tener varias reservas  |
| Pertenece      | Reserva       | Vuelo         | N:1          | Cada reserva es para un vuelo específico |
| Genera         | Reserva       | Boleto        | 1:N          | Una reserva puede generar varios boletos |
| Corresponde    | Boleto        | Vuelo         | N:1          | Un boleto es para un vuelo específico    |
| Incluye        | Equipaje      | Boleto        | N:1          | Un boleto puede tener varios equipajes   |
| Registra       | Pago          | Reserva       | N:1          | Una reserva puede tener varios pagos     |
| Asigna         | Tripulación   | Vuelo         | N:M          | Varios empleados por vuelo               |
| Es             | Tripulación   | Empleado      | N:1          | Cada miembro de tripulación es un empleado |
| Opera          | Vuelo         | Ruta          | N:1          | Un vuelo sigue una ruta                  |
| Usa            | Vuelo         | Aeronave      | N:1          | Un vuelo usa una aeronave                |
| Tiene origen   | Ruta          | Aeropuerto    | N:1          | Una ruta parte de un aeropuerto          |
| Tiene destino  | Ruta          | Aeropuerto    | N:1          | Una ruta llega a un aeropuerto           |
| Requiere       | Mantenimiento | Aeronave      | N:1          | Una aeronave tiene varios mantenimientos |
| Ejecuta        | Mantenimiento | Empleado      | N:1          | Un empleado puede ejecutar varios mantenimientos |
