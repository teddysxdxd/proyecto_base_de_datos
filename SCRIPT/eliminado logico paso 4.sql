-- ######################################################################
-- ## SCRIPT DE MODIFICACIÓN: AÑADIR COLUMNA ESTADO_REGISTRO           ##
-- ######################################################################

-- Nota: El valor 'A' es Activo, 'I' es Inactivo (eliminado lógicamente).

ALTER TABLE Turista ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Correo ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Telefono ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Sucursal ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Hotel ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Avion ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Vuelo ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Categoria_Plaza ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Categoria_Plaza_Ocupada ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL);
ALTER TABLE Flag_Bitacora ADD (estado_registro CHAR(1) DEFAULT 'A' NOT NULL); -- Opcional, pero consistente.

-- Las tablas de unión (Turista_Sucursal, Turista_Hotel, Turista_Vuelo)
-- generalmente no requieren columna de estado, ya que su "eliminación lógica"
-- es simplemente eliminar el registro de la tabla de unión.

COMMIT;

SELECT 'Columna estado_registro añadida a las tablas principales para eliminado lógico.' AS Mensaje FROM DUAL;