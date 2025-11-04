-- #################################################################
-- ## INSERTS PARA POBLAR EL ESQUEMA_TURISMO (Datos de Ejemplo)  ##
-- #################################################################

-- NOTA: Como los IDs son IDENTITY, no es necesario especificarlos.

-- 1. Catálogo: Avion
INSERT INTO Avion (tipo_avion) VALUES ('Boeing 737');
INSERT INTO Avion (tipo_avion) VALUES ('Airbus A320');

-- 2. Catálogo: Categoria_Plaza
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Economica', 150);
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Ejecutiva', 30);

-- 3. Entidad Principal: Turista
INSERT INTO Turista (nombre1, apellido1, direccion) VALUES ('Juan', 'Perez', 'Avenida Central 123, Ciudad Guatemala');
INSERT INTO Turista (nombre1, apellido1, nombre2, apellido2, direccion) VALUES ('Maria', 'Lopez', 'Gabriela', 'Hernandez', 'Calle de las Rosas 45, Antigua');

-- 4. Entidad Principal: Sucursal
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('7ma Avenida Zona 9, Local 10', '2412-1000', 'Ciudad de Guatemala');
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('Calle Santander, Edif. A', '7762-2000', 'Panajachel, Sololá');

-- 5. Entidad Principal: Hotel
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Hotel Colonial', '10a Calle, Zona 1', 'Quetzaltenango', '7761-3000', 80, 15);
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Resort del Lago', 'Orilla del Lago Atitlán', 'San Pedro La Laguna', '7762-4000', 120, 50);

-- 6. Relación 1:N: Correo (Para Juan Perez - id_turista=1)
INSERT INTO Correo (id_turista, tipo_correo, correo) VALUES (1, 'Personal', 'juan.perez@email.com');

-- 7. Relación 1:N: Telefono (Para Maria Lopez - id_turista=2)
INSERT INTO Telefono (id_turista, tipo_telefono, telefono) VALUES (2, 'Móvil', '5555-1234');

-- 8. Vuelo (Usa el avión 'Boeing 737' - asumiendo id_avion=1)
INSERT INTO Vuelo (id_avion, fecha_hora, origen, destino) VALUES (1, TIMESTAMP '2025-12-20 08:00:00', 'GUA', 'MIA');

-- 9. Catálogo: Categoria_Plaza_Ocupada (Usa 'Economica' - asumiendo id_categoria=1)
INSERT INTO Categoria_Plaza_Ocupada (id_categoria, codigo_asiento) VALUES (1, '15A');

-- 10. Relación N:M: Turista_Hotel (Juan Perez se aloja en Hotel Colonial)
-- Asumiendo id_turista=1, id_hotel=1
INSERT INTO Turista_Hotel (id_turista, id_hotel, regimen, fecha_llegada, fecha_salida)
VALUES (1, 1, 'Todo Incluido', DATE '2025-07-15', DATE '2025-07-22');

COMMIT;

SELECT '10 Registros iniciales insertados en las tablas.' AS Mensaje FROM DUAL;

--- aquiii
-- ######################################################################
-- ## INSERTS ADICIONALES (4 REGISTROS POR TABLA CLAVE)                ##
-- ######################################################################

-- ======================================================================
-- A. ENTIDADES PRINCIPALES (4 INSERTS CADA UNA)
-- ======================================================================

-- 1. Turista (Registros 3 al 6)
INSERT INTO Turista (nombre1, apellido1, direccion) VALUES ('Carlos', 'Gomez', '12 Calle, Zona 10, Edificio Torre Azul');
INSERT INTO Turista (nombre1, apellido1, direccion) VALUES ('Laura', 'Ramirez', 'Residencial Los Cerezos, Casa 5');
INSERT INTO Turista (nombre1, apellido1, nombre2, apellido2, direccion) VALUES ('Roberto', 'Fuentes', 'Alexander', 'Mendez', '2a Avenida, 3-21, Zona 1');
INSERT INTO Turista (nombre1, apellido1, direccion) VALUES ('Silvia', 'Cruz', 'Apartamento 301, San Cristobal');

-- 2. Sucursal (Registros 3 al 6)
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('Centro Comercial Pradera Xela, Local 5', '7761-4500', 'Quetzaltenango');
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('Km 16.5 Carretera a El Salvador, CC', '6634-1100', 'Santa Catarina Pinula');
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('1ra Calle, Edificio La Ceiba, Local B', '7832-7000', 'Antigua Guatemala');
INSERT INTO Sucursal (direccion, telefono, ciudad) VALUES ('Aeropuerto Internacional La Aurora, Mód. C', '2384-5000', 'Ciudad de Guatemala');

-- 3. Hotel (Registros 3 al 6)
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Hotel Maya', '3a Avenida, 5-00, Zona 1', 'Flores, Petén', '7924-8000', 60, 10);
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Montaña Spa', 'Finca El Paraiso, Aldea Seca', 'Cobán, Alta Verapaz', '7952-9000', 45, 5);
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Capital Business', 'Zona Viva, Torre 4', 'Ciudad de Guatemala', '2333-1500', 180, 100);
INSERT INTO Hotel (nombre, direccion, ciudad, telefono, no_plaza_total, no_plaza_ocupada) VALUES ('Hostal Sol', '4a Calle Poniente #12', 'Antigua Guatemala', '7832-1200', 25, 20);

-- ======================================================================
-- B. CATÁLOGOS Y ENTIDADES RELACIONADAS
-- ======================================================================

-- 4. Avion (Registros 3 al 6)
INSERT INTO Avion (tipo_avion) VALUES ('Embraer E190');
INSERT INTO Avion (tipo_avion) VALUES ('Cessna Caravan');
INSERT INTO Avion (tipo_avion) VALUES ('Bombardier CRJ200');
INSERT INTO Avion (tipo_avion) VALUES ('Tupolev Tu-154');

-- 5. Categoria_Plaza (Registros 3 al 6)
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Primera Clase', 10);
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Premium Economy', 40);
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Business Plus', 12);
INSERT INTO Categoria_Plaza (nombre, cantidad_plaza) VALUES ('Cabina VIP', 8);

-- 6. Vuelo (Registros 2 al 5) - Usa id_avion 2, 3, 4, 5
INSERT INTO Vuelo (id_avion, fecha_hora, origen, destino) VALUES (2, TIMESTAMP '2025-12-25 14:30:00', 'LAX', 'GUA'); -- Avion A320
INSERT INTO Vuelo (id_avion, fecha_hora, origen, destino) VALUES (3, TIMESTAMP '2025-11-05 07:00:00', 'GUA', 'SAP'); -- Avion E190
INSERT INTO Vuelo (id_avion, fecha_hora, origen, destino) VALUES (4, TIMESTAMP '2026-01-01 19:00:00', 'PET', 'GUA'); -- Avion Cessna
INSERT INTO Vuelo (id_avion, fecha_hora, origen, destino) VALUES (5, TIMESTAMP '2026-02-10 10:00:00', 'PTY', 'GUA'); -- Avion CRJ200

-- 7. Categoria_Plaza_Ocupada (Registros 2 al 5) - Asientos de diferentes categorías
INSERT INTO Categoria_Plaza_Ocupada (id_categoria, codigo_asiento) VALUES (1, '16B'); -- Económica (ID 1)
INSERT INTO Categoria_Plaza_Ocupada (id_categoria, codigo_asiento) VALUES (2, '2C');  -- Ejecutiva (ID 2)
INSERT INTO Categoria_Plaza_Ocupada (id_categoria, codigo_asiento) VALUES (3, '1F');  -- Primera (ID 3)
INSERT INTO Categoria_Plaza_Ocupada (id_categoria, codigo_asiento) VALUES (4, '10A'); -- Premium (ID 4)

-- ======================================================================
-- C. RELACIONES N:M ADICIONALES
-- ======================================================================

-- 8. Turista_Sucursal (Carlos y Laura registrados en diferentes sucursales)
-- Turista ID 3 (Carlos), Sucursal ID 3 (Xela)
INSERT INTO Turista_Sucursal (id_turista, id_sucursal) VALUES (3, 3);
-- Turista ID 4 (Laura), Sucursal ID 4 (Carretera a El Salvador)
INSERT INTO Turista_Sucursal (id_turista, id_sucursal) VALUES (4, 4);

-- 9. Turista_Hotel (Roberto y Silvia en diferentes hoteles)
-- Turista ID 5 (Roberto), Hotel ID 3 (Hotel Maya)
INSERT INTO Turista_Hotel (id_turista, id_hotel, regimen, fecha_llegada, fecha_salida)
VALUES (5, 3, 'Media Pensión', DATE '2025-12-01', DATE '2025-12-08');
-- Turista ID 6 (Silvia), Hotel ID 6 (Hostal Sol)
INSERT INTO Turista_Hotel (id_turista, id_hotel, regimen, fecha_llegada, fecha_salida)
VALUES (6, 6, 'Alojamiento', DATE '2026-01-10', DATE '2026-01-15');

-- 10. Turista_Vuelo (Asignación de turistas a vuelos y asientos)
-- Turista ID 3 (Carlos), Vuelo ID 2 (LAX->GUA), Asiento 16B (CPO ID 2)
INSERT INTO Turista_Vuelo (id_turista, id_vuelo, id_categoria_plaza_ocupada) VALUES (3, 2, 2);
-- Turista ID 4 (Laura), Vuelo ID 3 (GUA->SAP), Asiento 2C (CPO ID 3)
INSERT INTO Turista_Vuelo (id_turista, id_vuelo, id_categoria_plaza_ocupada) VALUES (4, 3, 3);

-- 11. Correo y Teléfono adicionales (para turistas nuevos)
INSERT INTO Correo (id_turista, tipo_correo, correo) VALUES (3, 'Negocios', 'carlos.gomez@empresa.com');
INSERT INTO Telefono (id_turista, tipo_telefono, telefono) VALUES (6, 'Móvil', '4444-5678');


COMMIT;

SELECT '16 Registros clave más sus relaciones han sido insertados exitosamente. Tu esquema está poblado.' AS Mensaje FROM DUAL;



--aquiiii
SELECT
    t.fecha,
    t.tipo_accion,
    t.nombre_tabla_modificada,
    f.nombre_flag AS categoria_flag,
    t.valor_actual
FROM
    Bitacora t
JOIN
    Flag_Bitacora f ON t.id_flag_bitacora = f.id_flag
ORDER BY
    t.fecha;