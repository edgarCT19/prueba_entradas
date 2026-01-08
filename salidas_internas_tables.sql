-- Crear tabla para salidas internas
CREATE TABLE IF NOT EXISTS `salidas_internas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_sucursal` int(11) NOT NULL,
  `folio_sucursal` int(11) NOT NULL,
  `fecha_salida` datetime NOT NULL,
  `responsable_entrega` varchar(255) NOT NULL COMMENT 'Nombre del chofer o persona que se lleva el equipo',
  `observaciones` text,
  `estado` enum('activa','finalizada_regreso','finalizada_no_regreso','cancelada') NOT NULL DEFAULT 'activa',
  `fecha_finalizacion` datetime NULL,
  `observaciones_finalizacion` text NULL,
  `usuario_creacion` int(11) NOT NULL,
  `usuario_finalizacion` int(11) NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sucursal` (`id_sucursal`),
  KEY `idx_folio_sucursal` (`folio_sucursal`),
  KEY `idx_estado` (`estado`),
  KEY `idx_fecha_salida` (`fecha_salida`),
  CONSTRAINT `fk_salidas_internas_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `fk_salidas_internas_usuario_creacion` FOREIGN KEY (`usuario_creacion`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `fk_salidas_internas_usuario_finalizacion` FOREIGN KEY (`usuario_finalizacion`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear tabla para el detalle de salidas internas
CREATE TABLE IF NOT EXISTS `salidas_internas_detalle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `salida_interna_id` int(11) NOT NULL,
  `id_pieza` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_salida_interna` (`salida_interna_id`),
  KEY `idx_pieza` (`id_pieza`),
  CONSTRAINT `fk_salidas_internas_detalle_salida` FOREIGN KEY (`salida_interna_id`) REFERENCES `salidas_internas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_salidas_internas_detalle_pieza` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crear índice único para evitar folios duplicados por sucursal
ALTER TABLE `salidas_internas` ADD UNIQUE KEY `unique_folio_sucursal` (`id_sucursal`, `folio_sucursal`);

-- Agregar comentarios a las tablas
ALTER TABLE `salidas_internas` COMMENT = 'Tabla para registrar salidas internas de equipo (préstamos sin pago)';
ALTER TABLE `salidas_internas_detalle` COMMENT = 'Detalle de productos en cada salida interna';