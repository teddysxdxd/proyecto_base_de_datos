-- ##########################################################################
-- ## TRIGGERS DE AUDITORÍA PARA TABLAS PRINCIPALES Y RELACIONES (BITACORA)##
-- ##########################################################################

-- =========================================================================
-- PASO PREVIO: ASEGURAR COLUMNA ESTADO_REGISTRO EN TURISTA PARA EVITAR PLS-00049
-- Nota: Esta columna debe existir antes de crear el trigger que la usa.
-- Si la columna ya existe de una ejecución previa, este ALTER TABLE generará un error 
-- que se puede ignorar (usando PL/SQL) o simplemente se asume que se ejecutará sin 
-- problema si se ejecuta después del paso 1 de creación de tablas.
-- =========================================================================
DECLARE
    col_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO col_exists
    FROM all_tab_columns
    WHERE owner = USER
    AND table_name = 'TURISTA'
    AND column_name = 'ESTADO_REGISTRO';
    
    IF col_exists = 0 THEN
        EXECUTE IMMEDIATE 'ALTER TABLE Turista ADD (estado_registro CHAR(1) DEFAULT ''A'' NOT NULL)';
    END IF;
END;
/

-- =========================================================================
-- 1. TRG_AUD_TURISTA
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_TURISTA
AFTER INSERT OR UPDATE OR DELETE ON Turista
FOR EACH ROW
DECLARE
    v_tipo_accion VARCHAR2(10);
    v_id_registro NUMBER;
BEGIN
    IF INSERTING THEN
        v_tipo_accion := 'INSERT';
        v_id_registro := :NEW.id_turista;
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES (v_tipo_accion, 'TURISTA', 'ID: ' || v_id_registro || ' - Creado: ' || :NEW.nombre1 || ' ' || :NEW.apellido1, 1);
        
    ELSIF UPDATING THEN
        v_tipo_accion := 'UPDATE';
        v_id_registro := :OLD.id_turista;
        
        -- ⭐⭐ PARTE CLAVE AÑADIDA PARA ELIMINADO LÓGICO ⭐⭐
        -- Si el estado cambia de 'A' (Activo) a 'I' (Inactivo), lo logueamos como DELETE (Lógico)
        IF :OLD.estado_registro = 'A' AND :NEW.estado_registro = 'I' THEN
             INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
             VALUES ('DELETE (L)', 'TURISTA', 'ESTADO_REGISTRO', 'Activo', 'Inactivo', 3); -- Usando 3 para Eliminado
        END IF;
        -- ⭐⭐ FIN PARTE CLAVE ⭐⭐
        
        -- Auditoría detallada para otros campos clave (se mantiene la lógica original)
        IF :OLD.nombre1 <> :NEW.nombre1 OR :OLD.apellido1 <> :NEW.apellido1 OR :OLD.direccion <> :NEW.direccion THEN
            
            -- Auditoría de Nombre 1
            IF :OLD.nombre1 <> :NEW.nombre1 THEN
                INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
                VALUES (v_tipo_accion, 'TURISTA', 'NOMBRE1', :OLD.nombre1, :NEW.nombre1, 2);
            END IF;
            
            -- Auditoría de Apellido 1
            IF :OLD.apellido1 <> :NEW.apellido1 THEN
                INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
                VALUES (v_tipo_accion, 'TURISTA', 'APELLIDO1', :OLD.apellido1, :NEW.apellido1, 2);
            END IF;
            
            -- Auditoría de Dirección
            IF :OLD.direccion <> :NEW.direccion THEN
                INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
                VALUES (v_tipo_accion, 'TURISTA', 'DIRECCION', :OLD.direccion, :NEW.direccion, 2);
            END IF;
            
        END IF;

    ELSIF DELETING THEN
        v_id_registro := :OLD.id_turista;
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE (F)', 'TURISTA', 'ID: ' || v_id_registro || ' - Eliminado: ' || :OLD.nombre1 || ' ' || :OLD.apellido1, 3);
    END IF;
END;
/
-- =========================================================================
-- 2. TRG_AUD_CORREO
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_CORREO
AFTER INSERT OR UPDATE OR DELETE ON Correo
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'CORREO', 'Turista ID: ' || :NEW.id_turista || ' - Correo Añadido: ' || :NEW.correo, 1);
    ELSIF UPDATING THEN
        IF :OLD.correo <> :NEW.correo THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'CORREO', 'correo', :OLD.correo, :NEW.correo, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'CORREO', 'Turista ID: ' || :OLD.id_turista || ' - Correo Eliminado: ' || :OLD.correo, 3);
    END IF;
END;
/

-- =========================================================================
-- 3. TRG_AUD_TELEFONO
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_TELEFONO
AFTER INSERT OR UPDATE OR DELETE ON Telefono
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'TELEFONO', 'Turista ID: ' || :NEW.id_turista || ' - Teléfono Añadido: ' || :NEW.telefono, 1);
    ELSIF UPDATING THEN
        IF :OLD.telefono <> :NEW.telefono THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'TELEFONO', 'telefono', :OLD.telefono, :NEW.telefono, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'TELEFONO', 'Turista ID: ' || :OLD.id_turista || ' - Teléfono Eliminado: ' || :OLD.telefono, 3);
    END IF;
END;
/

-- =========================================================================
-- 4. TRG_AUD_SUCURSAL
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_SUCURSAL
AFTER INSERT OR UPDATE OR DELETE ON Sucursal
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'SUCURSAL', 'ID: ' || :NEW.id_sucursal || ' - Nueva en ' || :NEW.ciudad, 1);
    ELSIF UPDATING THEN
        IF :OLD.ciudad <> :NEW.ciudad OR :OLD.direccion <> :NEW.direccion THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'SUCURSAL', 'Ubicación', 'Antigua: ' || :OLD.ciudad, 'Nueva: ' || :NEW.ciudad, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'SUCURSAL', 'ID: ' || :OLD.id_sucursal || ' - Eliminada en ' || :OLD.ciudad, 3);
    END IF;
END;
/

-- =========================================================================
-- 5. TRG_AUD_HOTEL
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_HOTEL
AFTER INSERT OR UPDATE OR DELETE ON Hotel
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'HOTEL', 'ID: ' || :NEW.id_hotel || ' - Creado: ' || :NEW.nombre || ' en ' || :NEW.ciudad, 1);
    ELSIF UPDATING THEN
        IF :OLD.no_plaza_total <> :NEW.no_plaza_total OR :OLD.no_plaza_ocupada <> :NEW.no_plaza_ocupada THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'HOTEL', 'Plazas', 'Total/Ocupadas: ' || :OLD.no_plaza_total || '/' || :OLD.no_plaza_ocupada, 'Total/Ocupadas: ' || :NEW.no_plaza_total || '/' || :NEW.no_plaza_ocupada, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'HOTEL', 'ID: ' || :OLD.id_hotel || ' - Eliminado: ' || :OLD.nombre, 3);
    END IF;
END;
/

-- =========================================================================
-- 6. TRG_AUD_AVION (CATÁLOGO)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_AVION
AFTER INSERT OR UPDATE OR DELETE ON Avion
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'AVION', 'ID: ' || :NEW.id_avion || ' - Nuevo tipo: ' || :NEW.tipo_avion, 1);
    ELSIF UPDATING THEN
        IF :OLD.tipo_avion <> :NEW.tipo_avion THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'AVION', 'tipo_avion', :OLD.tipo_avion, :NEW.tipo_avion, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'AVION', 'ID: ' || :OLD.id_avion || ' - Eliminado: ' || :OLD.tipo_avion, 3);
    END IF;
END;
/

-- =========================================================================
-- 7. TRG_AUD_VUELO
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_VUELO
AFTER INSERT OR UPDATE OR DELETE ON Vuelo
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'VUELO', 'ID: ' || :NEW.id_vuelo || ' - Nuevo Vuelo: ' || :NEW.origen || ' a ' || :NEW.destino, 1);
    ELSIF UPDATING THEN
        IF :OLD.fecha_hora <> :NEW.fecha_hora OR :OLD.destino <> :NEW.destino THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'VUELO', 'Fecha/Ruta', 'Antigua Ruta: ' || :OLD.origen || ' a ' || :OLD.destino, 'Nueva Ruta: ' || :NEW.origen || ' a ' || :NEW.destino, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'VUELO', 'ID: ' || :OLD.id_vuelo || ' - Eliminado: ' || :OLD.origen || ' a ' || :OLD.destino, 3);
    END IF;
END;
/

-- =========================================================================
-- 8. TRG_AUD_CATEGORIA_PLAZA (CATÁLOGO)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_CAT_PLAZA
AFTER INSERT OR UPDATE OR DELETE ON Categoria_Plaza
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'CATEGORIA_PLAZA', 'ID: ' || :NEW.id_categoria || ' - Nueva Categoría: ' || :NEW.nombre, 1);
    ELSIF UPDATING THEN
        IF :OLD.nombre <> :NEW.nombre THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'CATEGORIA_PLAZA', 'nombre', :OLD.nombre, :NEW.nombre, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'CATEGORIA_PLAZA', 'ID: ' || :OLD.id_categoria || ' - Eliminada: ' || :OLD.nombre, 3);
    END IF;
END;
/

-- =========================================================================
-- 9. TRG_AUD_CPO (Categoria_Plaza_Ocupada)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_CPO
AFTER INSERT OR UPDATE OR DELETE ON Categoria_Plaza_Ocupada
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'CPO', 'ID: ' || :NEW.id_categoria_plaza_ocupada || ' - Asiento Creado: ' || :NEW.codigo_asiento, 1);
    ELSIF UPDATING THEN
        IF :OLD.codigo_asiento <> :NEW.codigo_asiento THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'CPO', 'codigo_asiento', :OLD.codigo_asiento, :NEW.codigo_asiento, 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'CPO', 'ID: ' || :OLD.id_categoria_plaza_ocupada || ' - Asiento Eliminado: ' || :OLD.codigo_asiento, 3);
    END IF;
END;
/

-- =========================================================================
-- 10. TRG_AUD_TURISTA_SUCURSAL (N:M)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_TURISTA_SUCURSAL
AFTER INSERT OR DELETE ON Turista_Sucursal
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'TURISTA_SUCURSAL', 'Turista ID: ' || :NEW.id_turista || ' asociado a Sucursal ID: ' || :NEW.id_sucursal, 1);
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'TURISTA_SUCURSAL', 'Turista ID: ' || :OLD.id_turista || ' desasociado de Sucursal ID: ' || :OLD.id_sucursal, 3);
    END IF;
END;
/

-- =========================================================================
-- 11. TRG_AUD_TURISTA_HOTEL (N:M)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_TURISTA_HOTEL
AFTER INSERT OR UPDATE OR DELETE ON Turista_Hotel
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'TURISTA_HOTEL', 'Turista ID: ' || :NEW.id_turista || ' se aloja en Hotel ID: ' || :NEW.id_hotel, 1);
    ELSIF UPDATING THEN
        IF :OLD.fecha_llegada <> :NEW.fecha_llegada OR :OLD.fecha_salida <> :NEW.fecha_salida THEN
            INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, campo_modificado, valor_anterior, valor_actual, id_flag_bitacora)
            VALUES ('UPDATE', 'TURISTA_HOTEL', 'Fechas Alojamiento', 'Anterior: ' || TO_CHAR(:OLD.fecha_llegada, 'YYYY-MM-DD'), 'Nueva: ' || TO_CHAR(:NEW.fecha_salida, 'YYYY-MM-DD'), 2);
        END IF;
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'TURISTA_HOTEL', 'Turista ID: ' || :OLD.id_turista || ' dejó Hotel ID: ' || :OLD.id_hotel, 3);
    END IF;
END;
/

-- =========================================================================
-- 12. TRG_AUD_TURISTA_VUELO (N:M)
-- =========================================================================
CREATE OR REPLACE TRIGGER TRG_AUD_TURISTA_VUELO
AFTER INSERT OR DELETE ON Turista_Vuelo
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_actual, id_flag_bitacora)
        VALUES ('INSERT', 'TURISTA_VUELO', 'Turista ID: ' || :NEW.id_turista || ' reservó Vuelo ID: ' || :NEW.id_vuelo || ' (Plaza: ' || :NEW.id_categoria_plaza_ocupada || ')', 1);
    ELSIF DELETING THEN
        INSERT INTO Bitacora (tipo_accion, nombre_tabla_modificada, valor_anterior, id_flag_bitacora)
        VALUES ('DELETE', 'TURISTA_VUELO', 'Turista ID: ' || :OLD.id_turista || ' canceló Vuelo ID: ' || :OLD.id_vuelo, 3);
    END IF;
END;
/
-----
DECLARE
    v_index_name VARCHAR2(128);
BEGIN
    SELECT index_name INTO v_index_name 
    FROM all_ind_columns 
    WHERE table_name = 'CORREO' AND column_name = 'CORREO' AND index_owner = USER AND rownum = 1;

    EXECUTE IMMEDIATE 'DROP INDEX ' || v_index_name;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        NULL; -- No había un índice explícito.
    WHEN OTHERS THEN
        NULL; -- Manejar otros errores si es necesario.
END;
/

-- Confirmación
SELECT 'Todos los triggers de auditoría se han creado exitosamente.' AS Mensaje FROM DUAL;