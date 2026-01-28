CREATE DATABASE  IF NOT EXISTS `andamiosdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `andamiosdb`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: database-1.cf0ey64ia6yt.us-east-2.rds.amazonaws.com    Database: andamiosdb
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido1` varchar(100) NOT NULL,
  `apellido2` varchar(100) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `rfc` varchar(20) DEFAULT NULL,
  `tipo_cliente` varchar(20) NOT NULL,
  `sucursal_id` int DEFAULT NULL,
  `fecha_alta` datetime DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  `codigo_cliente` varchar(10) DEFAULT NULL,
  `rol_id` int DEFAULT NULL,
  `calle` varchar(255) DEFAULT NULL,
  `numero_exterior` varchar(10) DEFAULT NULL,
  `numero_interior` varchar(10) DEFAULT NULL,
  `colonia` varchar(100) DEFAULT NULL,
  `codigo_postal` varchar(5) DEFAULT NULL,
  `municipio` varchar(100) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `entre_calles` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_cliente` (`codigo_cliente`),
  UNIQUE KEY `codigo_cliente_2` (`codigo_cliente`),
  KEY `fk_cliente_sucursal` (`sucursal_id`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `fk_cliente_sucursal` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,'Eugenia','Fuentes','Caraveo','9821316654','eugenia2003fuentes@gmail.com','FUCE030917BC6','ocasional',1,'2025-06-25 00:00:00',1,'0100001',NULL,'Andador Rafael Velazco','2','','Bicentenario 1','24049','Campeche','Campeche','entre galeana y calle 26'),(2,'Pedro','Perez','Perez','9821316655','','','frecuente',1,'2025-06-25 00:00:00',1,'0100002',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,'Galilea','Vera','Delgado','9811049593','galivera@gmail.com','FUCE030917MC5','frecuente',1,'2025-07-07 00:00:00',1,'0100003',1,'C. 16','#69','','SAN ROMAN','24040','CAMPECHE','CAMPECHE','C. BRAVO Y C. ALLENDE'),(4,'Mario','Bernadette','Cuña','9811314378','mario@prueba.com','MARI983456B2','ocasional',1,'2025-10-06 00:00:00',1,'0100004',1,'andador rafael velazco','2','','bicentenario 1','24049','campeche','campeche','galeana y pedro moreno');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cotizacion_detalle`
--

DROP TABLE IF EXISTS `cotizacion_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cotizacion_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cotizacion_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `producto_id` (`producto_id`),
  KEY `idx_cotizacion_detalle_cotizacion` (`cotizacion_id`),
  CONSTRAINT `cotizacion_detalle_ibfk_1` FOREIGN KEY (`cotizacion_id`) REFERENCES `cotizaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cotizacion_detalle_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cotizacion_detalle`
--

LOCK TABLES `cotizacion_detalle` WRITE;
/*!40000 ALTER TABLE `cotizacion_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `cotizacion_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cotizacion_seguimiento`
--

DROP TABLE IF EXISTS `cotizacion_seguimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cotizacion_seguimiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cotizacion_id` int NOT NULL,
  `estado_anterior` varchar(50) DEFAULT NULL,
  `estado_nuevo` varchar(50) NOT NULL,
  `comentarios` text,
  `fecha_cambio` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cotizacion_id` (`cotizacion_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `cotizacion_seguimiento_ibfk_1` FOREIGN KEY (`cotizacion_id`) REFERENCES `cotizaciones` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cotizacion_seguimiento_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cotizacion_seguimiento`
--

LOCK TABLES `cotizacion_seguimiento` WRITE;
/*!40000 ALTER TABLE `cotizacion_seguimiento` DISABLE KEYS */;
/*!40000 ALTER TABLE `cotizacion_seguimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cotizaciones`
--

DROP TABLE IF EXISTS `cotizaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cotizaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero_cotizacion` varchar(20) NOT NULL,
  `cliente_nombre` varchar(100) NOT NULL,
  `cliente_telefono` varchar(20) NOT NULL,
  `cliente_email` varchar(100) DEFAULT NULL,
  `cliente_empresa` varchar(100) DEFAULT NULL,
  `dias_renta` int NOT NULL,
  `requiere_traslado` tinyint(1) DEFAULT '0',
  `tipo_traslado` enum('medio','redondo') DEFAULT NULL,
  `costo_traslado` decimal(10,2) DEFAULT '0.00',
  `subtotal` decimal(10,2) NOT NULL DEFAULT '0.00',
  `iva` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `estado` enum('enviada','vencida','renta') DEFAULT 'enviada',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_vigencia` date NOT NULL,
  `usuario_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero_cotizacion` (`numero_cotizacion`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_cotizaciones_numero` (`numero_cotizacion`),
  KEY `idx_cotizaciones_estado` (`estado`),
  KEY `idx_cotizaciones_fecha` (`fecha_creacion`),
  KEY `idx_cotizaciones_sucursal` (`sucursal_id`),
  CONSTRAINT `cotizaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `cotizaciones_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cotizaciones`
--

LOCK TABLES `cotizaciones` WRITE;
/*!40000 ALTER TABLE `cotizaciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `cotizaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentos_cliente`
--

DROP TABLE IF EXISTS `documentos_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documentos_cliente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `tipo_documento` varchar(30) NOT NULL,
  `archivo` varchar(255) NOT NULL,
  `fecha_subida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `documentos_cliente_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentos_cliente`
--

LOCK TABLES `documentos_cliente` WRITE;
/*!40000 ALTER TABLE `documentos_cliente` DISABLE KEYS */;
/*!40000 ALTER TABLE `documentos_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_rentas`
--

DROP TABLE IF EXISTS `historial_rentas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_rentas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `renta_id` int DEFAULT NULL,
  `accion` varchar(50) DEFAULT NULL,
  `descripcion` text,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `renta_id` (`renta_id`),
  CONSTRAINT `historial_rentas_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_rentas`
--

LOCK TABLES `historial_rentas` WRITE;
/*!40000 ALTER TABLE `historial_rentas` DISABLE KEYS */;
INSERT INTO `historial_rentas` VALUES (1,6,'cancelacion','Cancelación de renta. Motivo: no sirvieron | Reembolso: $70.0','2025-11-27 18:18:01'),(2,7,'cancelacion','Cancelación de renta. Motivo: dcrfrfe | Reembolso: $522','2025-11-27 18:37:16'),(3,37,'cancelacion','Cancelación de renta. Motivo: no funcionó | Reembolso: $1044','2025-12-11 14:32:47'),(4,37,'cancelacion','Cancelación de renta. Motivo: no funcionó | Reembolso: $1044','2025-12-11 14:32:47'),(5,37,'cancelacion','Cancelación de renta. Motivo: no funcionó | Reembolso: $1044','2025-12-11 14:32:48'),(6,37,'cancelacion','Cancelación de renta. Motivo: no funcionó | Reembolso: $1044','2025-12-11 14:32:48'),(7,51,'cancelacion','Cancelación de renta. Motivo: no laboraron | Reembolso: $35','2026-01-06 18:20:28');
/*!40000 ALTER TABLE `historial_rentas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_sucursal`
--

DROP TABLE IF EXISTS `inventario_sucursal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_sucursal` (
  `id_inventario` int NOT NULL AUTO_INCREMENT,
  `id_sucursal` int NOT NULL,
  `id_pieza` int NOT NULL,
  `total` int NOT NULL DEFAULT '0',
  `disponibles` int NOT NULL DEFAULT '0',
  `rentadas` int NOT NULL DEFAULT '0',
  `daniadas` int NOT NULL DEFAULT '0',
  `en_reparacion` int NOT NULL DEFAULT '0',
  `stock_minimo` int NOT NULL DEFAULT '0',
  `perdidas` int DEFAULT '0',
  PRIMARY KEY (`id_inventario`),
  UNIQUE KEY `id_sucursal_2` (`id_sucursal`,`id_pieza`),
  KEY `id_sucursal` (`id_sucursal`),
  KEY `id_pieza` (`id_pieza`),
  CONSTRAINT `inventario_sucursal_ibfk_1` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `inventario_sucursal_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_sucursal`
--

LOCK TABLES `inventario_sucursal` WRITE;
/*!40000 ALTER TABLE `inventario_sucursal` DISABLE KEYS */;
INSERT INTO `inventario_sucursal` VALUES (1,1,1,1126,1079,47,0,0,0,2),(2,1,2,1154,921,211,20,0,0,0),(3,2,2,27,27,0,0,0,0,0),(5,1,3,1044,946,88,10,0,0,0),(6,1,4,1103,1062,37,4,1,0,1),(7,1,5,1452,1294,155,3,0,0,1),(8,1,6,1164,965,198,1,0,0,0),(9,1,7,1198,482,706,9,1,0,2),(10,1,8,208,160,42,6,0,0,2),(11,1,9,59,50,8,1,0,0,0),(12,3,4,5,5,0,0,0,0,0),(13,1,10,403,383,12,8,0,0,2),(14,1,11,61,24,31,6,0,0,0),(15,1,12,33,9,23,1,0,0,1),(16,2,1,38,38,0,0,0,0,0),(17,1,13,23,22,1,0,0,0,0),(18,1,14,21,20,0,1,0,0,0),(19,1,15,22,22,0,0,0,0,0),(20,1,16,21,21,0,0,0,0,0),(21,1,17,98,52,44,2,0,0,1),(34,3,2,49,49,0,0,0,0,0),(35,3,1,50,50,0,0,0,0,0),(36,3,7,40,40,0,0,0,0,0),(37,3,5,50,50,0,0,0,0,0),(38,3,3,1,1,0,0,0,0,0),(39,3,10,1,1,0,0,0,0,0),(40,3,6,1,1,0,0,0,0,0),(41,2,7,80,80,0,0,0,0,0),(44,2,12,1,1,0,0,0,0,0),(45,2,10,1,1,0,0,0,0,0);
/*!40000 ALTER TABLE `inventario_sucursal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_caja`
--

DROP TABLE IF EXISTS `movimientos_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_caja` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo` enum('ingreso','egreso') NOT NULL,
  `concepto` varchar(255) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `metodo_pago` enum('EFECTIVO','T.DÉBITO','T.CRÉDITO','TRANSFERENCIA') NOT NULL,
  `numero_seguimiento` varchar(100) DEFAULT NULL,
  `observaciones` text,
  `tipo_movimiento` enum('manual','automatico') NOT NULL DEFAULT 'manual',
  `referencia_tabla` varchar(50) DEFAULT NULL COMMENT 'prefacturas, notas_cobro_extra, notas_cobro_retraso',
  `referencia_id` int DEFAULT NULL COMMENT 'ID del registro que generó este movimiento',
  `usuario_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tipo` (`tipo`),
  KEY `idx_referencia` (`referencia_tabla`,`referencia_id`),
  KEY `idx_tipo_movimiento` (`tipo_movimiento`),
  KEY `usuario_id` (`usuario_id`),
  KEY `idx_fecha_hora` (`fecha_hora`),
  KEY `idx_sucursal_fecha_hora` (`sucursal_id`,`fecha_hora`),
  CONSTRAINT `movimientos_caja_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `movimientos_caja_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_caja`
--

LOCK TABLES `movimientos_caja` WRITE;
/*!40000 ALTER TABLE `movimientos_caja` DISABLE KEYS */;
INSERT INTO `movimientos_caja` VALUES (1,'2026-01-27 15:31:02','ingreso','Pago prefactura #1 - Renta #61 (inicial)',605.50,'EFECTIVO',NULL,'Generado automáticamente desde prefactura','automatico','prefacturas',50,1,1,'2026-01-27 15:05:36');
/*!40000 ALTER TABLE `movimientos_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos_inventario` (
  `id_movimiento` int NOT NULL AUTO_INCREMENT,
  `id_sucursal` int NOT NULL,
  `id_pieza` int NOT NULL,
  `tipo_movimiento` varchar(50) NOT NULL,
  `cantidad` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario` int DEFAULT NULL,
  `sucursal_destino` int DEFAULT NULL,
  `observaciones` text,
  `folio_nota_salida` varchar(10) DEFAULT NULL,
  `folio_nota_entrada` varchar(10) DEFAULT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_sucursal` (`id_sucursal`),
  KEY `id_pieza` (`id_pieza`),
  KEY `sucursal_destino` (`sucursal_destino`),
  KEY `fk_usuario` (`usuario`),
  CONSTRAINT `fk_usuario` FOREIGN KEY (`usuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`),
  CONSTRAINT `movimientos_inventario_ibfk_3` FOREIGN KEY (`sucursal_destino`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=183 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` VALUES (120,1,5,'alta',1,'2025-12-22 19:02:35',1,NULL,NULL,NULL,NULL,NULL),(121,1,17,'alta_equipo',3,'2026-01-06 19:05:08',1,NULL,NULL,NULL,'52','Alta de equipo nuevo. '),(122,1,1,'transferencia_salida',1,'2026-01-06 19:21:37',1,2,'','00053',NULL,'Envío a Sucursal Los Reyes'),(123,1,7,'a_reparacion',1,'2026-01-07 20:25:49',1,NULL,NULL,NULL,NULL,'Enviado a reparación'),(124,1,7,'reparacion_lote',4,'2026-01-08 15:36:36',1,NULL,NULL,'54',NULL,'Lote reparación - '),(125,1,7,'reparacion_finalizada',5,'2026-01-08 15:37:12',1,NULL,NULL,NULL,NULL,'Reparación finalizada - tracking limpiado'),(126,1,7,'alta_equipo',5,'2026-01-08 15:40:42',1,NULL,NULL,NULL,'54','Alta de equipo nuevo. '),(127,1,2,'reparacion_finalizada',2,'2026-01-08 15:46:40',1,NULL,NULL,NULL,NULL,'Reparación finalizada - tracking limpiado'),(128,1,12,'retorno_salida_interna',1,'2026-01-08 20:41:11',1,NULL,NULL,NULL,NULL,'Retorno de salida interna - Folio: SUC1-0057 - '),(129,1,12,'salida_interna',1,'2026-01-09 19:15:11',1,NULL,NULL,NULL,NULL,'Salida interna - Folio: SUC1-0059 - Responsable: josé'),(130,1,10,'salida_interna',1,'2026-01-09 19:15:13',1,NULL,NULL,NULL,NULL,'Salida interna - Folio: SUC1-0059 - Responsable: josé'),(131,1,9,'salida_interna',1,'2026-01-09 19:15:15',1,NULL,NULL,NULL,NULL,'Salida interna - Folio: SUC1-0059 - Responsable: josé'),(132,1,10,'transferencia_salida',2,'2026-01-13 19:52:39',1,2,'','00064',NULL,'Envío a Sucursal Los Reyes'),(133,1,8,'transferencia_salida',1,'2026-01-13 19:56:07',1,3,'','00065',NULL,'Envío a Sucursal Lerma'),(134,1,1,'transferencia_salida',3,'2026-01-14 18:31:08',1,2,'','00066',NULL,'Envío a Sucursal Los Reyes'),(135,1,8,'transferencia_salida',5,'2026-01-14 18:31:09',1,2,'','00066',NULL,'Envío a Sucursal Los Reyes'),(136,1,5,'transferencia_salida',6,'2026-01-14 18:31:09',1,2,'','00066',NULL,'Envío a Sucursal Los Reyes'),(137,1,7,'transferencia_salida',7,'2026-01-14 18:31:09',1,2,'','00066',NULL,'Envío a Sucursal Los Reyes'),(138,1,7,'transferencia_entrada',6,'2026-01-14 18:46:39',1,1,'',NULL,'00067','Recepción de Sucursal Los Reyes'),(139,1,5,'transferencia_entrada',8,'2026-01-14 18:46:40',1,1,'',NULL,'00067','Recepción de Sucursal Los Reyes'),(140,1,2,'transferencia_entrada',8,'2026-01-14 18:46:40',1,1,'',NULL,'00067','Recepción de Sucursal Los Reyes'),(141,1,8,'transferencia_entrada',10,'2026-01-14 18:46:40',1,1,'',NULL,'00067','Recepción de Sucursal Los Reyes'),(142,1,11,'transferencia_salida',3,'2026-01-14 19:00:44',1,3,'Envío para limpieza y pintura','00068',NULL,'Envío a Sucursal Lerma'),(143,1,10,'transferencia_salida',2,'2026-01-14 19:00:44',1,3,'Envío para limpieza y pintura','00068',NULL,'Envío a Sucursal Lerma'),(144,1,17,'transferencia_salida',4,'2026-01-14 19:00:44',1,3,'Envío para limpieza y pintura','00068',NULL,'Envío a Sucursal Lerma'),(145,1,14,'transferencia_salida',1,'2026-01-15 14:51:44',1,2,'','00069',NULL,'Envío a Sucursal Los Reyes'),(146,1,5,'transferencia_salida',4,'2026-01-15 14:51:45',1,2,'','00069',NULL,'Envío a Sucursal Los Reyes'),(147,1,9,'transferencia_salida',4,'2026-01-15 14:51:46',1,2,'','00069',NULL,'Envío a Sucursal Los Reyes'),(148,1,2,'transferencia_salida',6,'2026-01-15 14:51:47',1,2,'','00069',NULL,'Envío a Sucursal Los Reyes'),(149,1,16,'transferencia_entrada',1,'2026-01-15 14:53:53',1,3,'',NULL,'00070','Recepción de Sucursal Lerma'),(150,1,8,'transferencia_entrada',2,'2026-01-15 14:53:53',1,3,'',NULL,'00070','Recepción de Sucursal Lerma'),(151,1,9,'transferencia_entrada',4,'2026-01-15 14:53:54',1,3,'',NULL,'00070','Recepción de Sucursal Lerma'),(152,1,3,'transferencia_entrada',4,'2026-01-15 14:53:55',1,3,'',NULL,'00070','Recepción de Sucursal Lerma'),(153,1,14,'transferencia_entrada',1,'2026-01-15 14:57:31',1,2,'pruebas de inventario',NULL,'00071','Recepción de Sucursal Los Reyes'),(154,1,2,'transferencia_salida',1,'2026-01-15 15:10:22',1,3,'Pruebas de transferencia de equipo shalalala uaua biribiri bam bam','00072',NULL,'Envío a Sucursal Lerma'),(155,1,7,'transferencia_salida',1,'2026-01-15 15:10:28',1,3,'Pruebas de transferencia de equipo shalalala uaua biribiri bam bam','00072',NULL,'Envío a Sucursal Lerma'),(156,1,6,'transferencia_salida',1,'2026-01-15 15:10:30',1,3,'Pruebas de transferencia de equipo shalalala uaua biribiri bam bam','00072',NULL,'Envío a Sucursal Lerma'),(157,1,5,'transferencia_salida',1,'2026-01-15 15:10:33',1,3,'Pruebas de transferencia de equipo shalalala uaua biribiri bam bam','00072',NULL,'Envío a Sucursal Lerma'),(158,1,10,'transferencia_salida',1,'2026-01-15 15:10:37',1,3,'Pruebas de transferencia de equipo shalalala uaua biribiri bam bam','00072',NULL,'Envío a Sucursal Lerma'),(159,1,14,'transferencia_salida',1,'2026-01-15 17:08:04',1,2,'prueba prueba de biri biri bam bam, uuuuhhhhh lalalala pruebas pruebas pruebas pruebas pruebas, prueba de salto de línea en el PDF\'s','00073',NULL,'Envío a Sucursal Los Reyes'),(160,1,2,'transferencia_entrada',2,'2026-01-15 17:43:25',1,2,'',NULL,'00074','Recepción de Sucursal Los Reyes'),(161,1,6,'transferencia_entrada',2,'2026-01-15 17:43:25',1,2,'',NULL,'00074','Recepción de Sucursal Los Reyes'),(162,1,15,'transferencia_entrada',2,'2026-01-15 17:43:25',1,2,'',NULL,'00074','Recepción de Sucursal Los Reyes'),(163,1,5,'transferencia_entrada',2,'2026-01-15 17:43:25',1,2,'',NULL,'00074','Recepción de Sucursal Los Reyes'),(164,1,13,'transferencia_entrada',3,'2026-01-15 17:43:25',1,2,'',NULL,'00074','Recepción de Sucursal Los Reyes'),(165,1,14,'transferencia_entrada',2,'2026-01-15 17:55:55',1,2,'Pruebas de tranferecnias de entrada, sistema nuevo, pruebas pruebas pruebas purebas jiji jajaj dos lineas para las observaciones, pruebas de comportamiento',NULL,'00075','Recepción de Sucursal Los Reyes'),(166,1,5,'transferencia_entrada',100,'2026-01-15 17:55:55',1,2,'Pruebas de tranferecnias de entrada, sistema nuevo, pruebas pruebas pruebas purebas jiji jajaj dos lineas para las observaciones, pruebas de comportamiento',NULL,'00075','Recepción de Sucursal Los Reyes'),(167,1,4,'transferencia_entrada',100,'2026-01-15 17:55:55',1,2,'Pruebas de tranferecnias de entrada, sistema nuevo, pruebas pruebas pruebas purebas jiji jajaj dos lineas para las observaciones, pruebas de comportamiento',NULL,'00075','Recepción de Sucursal Los Reyes'),(168,1,1,'transferencia_entrada',100,'2026-01-15 17:55:55',1,2,'Pruebas de tranferecnias de entrada, sistema nuevo, pruebas pruebas pruebas purebas jiji jajaj dos lineas para las observaciones, pruebas de comportamiento',NULL,'00075','Recepción de Sucursal Los Reyes'),(169,1,8,'transferencia_entrada',100,'2026-01-15 17:55:56',1,2,'Pruebas de tranferecnias de entrada, sistema nuevo, pruebas pruebas pruebas purebas jiji jajaj dos lineas para las observaciones, pruebas de comportamiento',NULL,'00075','Recepción de Sucursal Los Reyes'),(170,1,16,'alta_equipo',1,'2026-01-15 19:17:51',1,NULL,NULL,NULL,'76','Alta de equipo nuevo. pruebas de alta de equipo nuevo, biri biri bamm biri biri biri bam babam  tururururuuru pruebaaaaas pruebas '),(171,1,4,'alta_equipo',1,'2026-01-15 19:17:52',1,NULL,NULL,NULL,'76','Alta de equipo nuevo. pruebas de alta de equipo nuevo, biri biri bamm biri biri biri bam babam  tururururuuru pruebaaaaas pruebas '),(172,1,12,'alta_equipo',1,'2026-01-15 19:17:52',1,NULL,NULL,NULL,'76','Alta de equipo nuevo. pruebas de alta de equipo nuevo, biri biri bamm biri biri biri bam babam  tururururuuru pruebaaaaas pruebas '),(173,1,6,'alta_equipo',4,'2026-01-15 19:17:52',1,NULL,NULL,NULL,'76','Alta de equipo nuevo. pruebas de alta de equipo nuevo, biri biri bamm biri biri biri bam babam  tururururuuru pruebaaaaas pruebas '),(174,1,7,'alta_equipo',1,'2026-01-16 14:36:19',1,NULL,NULL,NULL,'00077','Alta de equipo nuevo. ssssss'),(175,1,5,'transferencia_salida',2,'2026-01-16 14:37:04',1,2,'hhhhhhhhhhhhhhhhh','00078',NULL,'Envío a Sucursal Los Reyes'),(176,1,10,'transferencia_entrada',3,'2026-01-16 14:38:48',1,3,'eeeeeeeeeeeeeeeeee',NULL,'00079','Recepción de Sucursal Lerma'),(177,1,2,'transferencia_salida',1,'2026-01-16 14:49:22',1,2,'','00080',NULL,'Envío a Sucursal Los Reyes'),(178,1,10,'transferencia_salida',1,'2026-01-16 14:49:22',1,2,'','00080',NULL,'Envío a Sucursal Los Reyes'),(179,1,14,'marcar_daniadas',1,'2026-01-16 17:30:50',1,NULL,NULL,NULL,NULL,'Marcado como dañada'),(180,1,4,'reparacion_lote',1,'2026-01-16 17:47:25',1,NULL,NULL,'81',NULL,'Lote reparación - llllllllllllllllltd ytfyv bhgfty yutftygh ytftyfycr6fd6 vvf67fty gct7fyv uy8vguy hjvyu vytfv'),(181,1,7,'reparacion_lote',1,'2026-01-16 17:47:27',1,NULL,NULL,'81',NULL,'Lote reparación - llllllllllllllllltd ytfyv bhgfty yutftygh ytftyfycr6fd6 vvf67fty gct7fyv uy8vguy hjvyu vytfv'),(182,1,3,'reparacion_lote',1,'2026-01-16 18:02:23',1,NULL,NULL,'00082',NULL,'Lote reparación - ferf efcerffer ');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_cobro_extra`
--

DROP TABLE IF EXISTS `notas_cobro_extra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_cobro_extra` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nota_entrada_id` int NOT NULL,
  `tipo` varchar(20) DEFAULT NULL,
  `subtotal` decimal(10,2) NOT NULL DEFAULT '0.00',
  `iva` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total` decimal(10,2) NOT NULL DEFAULT '0.00',
  `metodo_pago` varchar(20) DEFAULT NULL,
  `monto_recibido` decimal(10,2) DEFAULT NULL,
  `cambio` decimal(10,2) DEFAULT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `facturable` tinyint(1) DEFAULT '0',
  `numero_seguimiento` varchar(50) DEFAULT NULL,
  `observaciones` text,
  `estado_pago` varchar(20) NOT NULL DEFAULT 'Extra Pendiente',
  `folio` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `nota_entrada_id` (`nota_entrada_id`),
  CONSTRAINT `notas_cobro_extra_ibfk_1` FOREIGN KEY (`nota_entrada_id`) REFERENCES `notas_entrada` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_cobro_extra`
--

LOCK TABLES `notas_cobro_extra` WRITE;
/*!40000 ALTER TABLE `notas_cobro_extra` DISABLE KEYS */;
INSERT INTO `notas_cobro_extra` VALUES (1,47,'extra',92500.00,14800.00,107300.00,'tarjeta_debito',107300.00,0.00,'2026-01-22 12:04:29',1,'234','Pruebas del sistema','Extra Pagado',0),(2,54,'extra',70.00,11.20,81.20,'efectivo',100.00,19.00,'2026-01-23 21:43:30',1,'','','Extra Pagado',0);
/*!40000 ALTER TABLE `notas_cobro_extra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_cobro_extra_detalle`
--

DROP TABLE IF EXISTS `notas_cobro_extra_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_cobro_extra_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cobro_extra_id` int NOT NULL,
  `id_pieza` int DEFAULT NULL,
  `tipo_afectacion` varchar(20) DEFAULT NULL,
  `cantidad` int NOT NULL DEFAULT '0',
  `costo_unitario` decimal(10,2) NOT NULL DEFAULT '0.00',
  `subtotal` decimal(10,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `cobro_extra_id` (`cobro_extra_id`),
  KEY `id_pieza` (`id_pieza`),
  CONSTRAINT `notas_cobro_extra_detalle_ibfk_1` FOREIGN KEY (`cobro_extra_id`) REFERENCES `notas_cobro_extra` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `notas_cobro_extra_detalle_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_cobro_extra_detalle`
--

LOCK TABLES `notas_cobro_extra_detalle` WRITE;
/*!40000 ALTER TABLE `notas_cobro_extra_detalle` DISABLE KEYS */;
INSERT INTO `notas_cobro_extra_detalle` VALUES (1,1,7,'perdida',50,50.00,2500.00),(2,1,6,'sucia',50,50.00,2500.00),(3,1,2,'dañada',20,2500.00,50000.00),(4,1,2,'perdida',15,2500.00,37500.00),(5,2,7,'dañada',1,50.00,50.00),(6,2,5,'sucia',1,20.00,20.00);
/*!40000 ALTER TABLE `notas_cobro_extra_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_cobro_retraso`
--

DROP TABLE IF EXISTS `notas_cobro_retraso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_cobro_retraso` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nota_entrada_id` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `subtotal` decimal(10,2) NOT NULL,
  `iva` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  `monto_recibido` decimal(10,2) DEFAULT NULL,
  `cambio` decimal(10,2) DEFAULT NULL,
  `observaciones` text,
  `facturable` tinyint(1) DEFAULT '0',
  `traslado_extra` varchar(50) DEFAULT NULL,
  `costo_traslado_extra` decimal(10,2) DEFAULT '0.00',
  `estado_pago` varchar(30) DEFAULT 'Retraso Pendiente',
  `numero_seguimiento` varchar(50) DEFAULT NULL,
  `folio` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `nota_entrada_id` (`nota_entrada_id`),
  CONSTRAINT `notas_cobro_retraso_ibfk_1` FOREIGN KEY (`nota_entrada_id`) REFERENCES `notas_entrada` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_cobro_retraso`
--

LOCK TABLES `notas_cobro_retraso` WRITE;
/*!40000 ALTER TABLE `notas_cobro_retraso` DISABLE KEYS */;
INSERT INTO `notas_cobro_retraso` VALUES (1,46,'2026-01-22 20:21:48',1348.00,215.68,1564.00,'EFECTIVO',2000.00,436.00,'',1,'ninguno',0.00,'Retraso Pagado','',0),(2,48,'2026-01-23 22:43:13',174.00,27.84,202.00,'EFECTIVO',210.00,8.00,'',1,'ninguno',0.00,'Retraso Pagado','',0);
/*!40000 ALTER TABLE `notas_cobro_retraso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_cobro_retraso_detalle`
--

DROP TABLE IF EXISTS `notas_cobro_retraso_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_cobro_retraso_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cobro_retraso_id` int NOT NULL,
  `id_producto` int NOT NULL,
  `nombre_producto` varchar(100) DEFAULT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `dias_retraso` int NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cobro_retraso_id` (`cobro_retraso_id`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `notas_cobro_retraso_detalle_ibfk_1` FOREIGN KEY (`cobro_retraso_id`) REFERENCES `notas_cobro_retraso` (`id`),
  CONSTRAINT `notas_cobro_retraso_detalle_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_cobro_retraso_detalle`
--

LOCK TABLES `notas_cobro_retraso_detalle` WRITE;
/*!40000 ALTER TABLE `notas_cobro_retraso_detalle` DISABLE KEYS */;
INSERT INTO `notas_cobro_retraso_detalle` VALUES (1,1,2,'ANDAMIO ANGOSTO 0.80',2,30.00,2,120.00),(2,1,5,'REVOLVEDORA',1,450.00,2,900.00),(3,1,8,'TORNILLO NIVELADOR',2,20.00,2,80.00),(4,1,3,'PUNTALES 3m',8,8.00,2,128.00),(5,1,1,'ANDAMIO ESTANDAR 2x1.52',2,30.00,2,120.00),(6,2,7,'ANDAMIO ANGOSTO 1m',3,18.00,1,54.00),(7,2,6,'ESCALERA 6m',1,120.00,1,120.00);
/*!40000 ALTER TABLE `notas_cobro_retraso_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_entrada`
--

DROP TABLE IF EXISTS `notas_entrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_entrada` (
  `id` int NOT NULL AUTO_INCREMENT,
  `folio` int NOT NULL,
  `renta_id` int NOT NULL,
  `nota_salida_id` int NOT NULL,
  `fecha_entrada_real` datetime DEFAULT CURRENT_TIMESTAMP,
  `requiere_traslado_extra` enum('ninguno','medio','redondo') DEFAULT 'ninguno',
  `costo_traslado_extra` decimal(10,2) DEFAULT '0.00',
  `observaciones` text,
  `estado` enum('normal','con_extras') DEFAULT 'normal',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estado_retraso` varchar(30) DEFAULT 'Sin Retraso',
  `accion_devolucion` varchar(20) NOT NULL DEFAULT 'no',
  PRIMARY KEY (`id`),
  KEY `nota_salida_id` (`nota_salida_id`),
  KEY `idx_renta` (`renta_id`),
  CONSTRAINT `notas_entrada_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`),
  CONSTRAINT `notas_entrada_ibfk_2` FOREIGN KEY (`nota_salida_id`) REFERENCES `notas_salida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_entrada`
--

LOCK TABLES `notas_entrada` WRITE;
/*!40000 ALTER TABLE `notas_entrada` DISABLE KEYS */;
INSERT INTO `notas_entrada` VALUES (1,2,6,5,'2025-11-27 18:18:17','ninguno',0.00,'','normal','2025-11-27 18:18:17','Sin Retraso','no'),(2,4,7,6,'2025-11-27 18:37:29','ninguno',0.00,'','normal','2025-11-27 18:37:29','Sin Retraso','no'),(3,5,2,1,'2025-12-01 22:45:03','ninguno',0.00,'','normal','2025-12-01 22:45:03','Retraso Pendiente','no'),(4,7,3,2,'2025-12-02 18:07:22','ninguno',0.00,'','normal','2025-12-02 18:07:22','Retraso Pendiente','renovacion'),(5,8,5,4,'2025-12-02 18:14:48','ninguno',0.00,'','normal','2025-12-02 18:14:48','Sin Retraso','renovacion'),(6,9,4,3,'2025-12-02 18:22:51','ninguno',0.00,'','normal','2025-12-02 18:22:51','Retraso Pendiente','renovacion'),(7,11,16,8,'2025-12-02 18:36:06','ninguno',0.00,'','normal','2025-12-02 18:36:06','Sin Retraso','pendiente'),(8,12,16,8,'2025-12-02 18:36:43','ninguno',0.00,'','normal','2025-12-02 18:36:43','Sin Retraso','no'),(9,14,17,9,'2025-12-02 18:56:29','ninguno',0.00,'','normal','2025-12-02 18:56:29','Sin Retraso','renovacion'),(20,16,17,9,'2025-12-02 19:23:47','ninguno',0.00,'','normal','2025-12-02 19:23:47','Sin Retraso','no'),(21,17,20,10,'2025-12-08 18:12:34','ninguno',0.00,'','normal','2025-12-08 18:11:53','Retraso Pendiente','no'),(22,19,22,11,'2025-12-09 14:20:58','ninguno',0.00,'','normal','2025-12-09 14:20:58','Sin Retraso','no'),(23,21,24,12,'2025-12-09 14:50:43','ninguno',0.00,'','normal','2025-12-09 14:50:43','Retraso Pendiente','renovacion'),(24,22,24,12,'2025-12-09 14:52:38','ninguno',0.00,'','normal','2025-12-09 14:52:38','Retraso Pendiente','no'),(25,24,25,13,'2025-12-09 14:56:19','ninguno',0.00,'','normal','2025-12-09 14:56:19','Retraso Pendiente','renovacion'),(26,25,25,13,'2025-12-09 14:59:19','ninguno',0.00,'','normal','2025-12-09 14:59:19','Sin Retraso','no'),(27,27,27,14,'2025-12-09 15:16:11','ninguno',0.00,'','normal','2025-12-09 15:16:11','Retraso Pendiente','renovacion'),(28,28,27,14,'2025-12-09 15:17:47','ninguno',0.00,'','normal','2025-12-09 15:17:47','Sin Retraso','no'),(29,30,29,15,'2025-12-09 15:25:27','ninguno',0.00,'','normal','2025-12-09 15:25:27','Retraso Pendiente','renovacion'),(30,0,29,15,'2025-12-09 17:46:46','ninguno',0.00,'','normal','2025-12-09 15:54:50','Retraso Pendiente','no'),(31,32,31,16,'2025-12-10 18:26:51','ninguno',0.00,'','normal','2025-12-10 18:26:51','Sin Retraso','renovacion'),(32,33,31,16,'2025-12-10 18:27:47','ninguno',0.00,'','normal','2025-12-10 18:27:47','Sin Retraso','no'),(33,35,33,17,'2025-12-10 18:36:52','ninguno',0.00,'','normal','2025-12-10 18:36:52','Sin Retraso','renovacion'),(34,36,33,17,'2025-12-10 18:37:46','ninguno',0.00,'','normal','2025-12-10 18:37:46','Sin Retraso','no'),(35,39,38,19,'2025-12-10 20:28:51','ninguno',0.00,'','normal','2025-12-10 20:28:51','Retraso Pendiente','renovacion'),(36,40,38,19,'2025-12-10 20:30:17','ninguno',0.00,'','normal','2025-12-10 20:30:17','Sin Retraso','no'),(37,42,40,20,'2025-12-11 14:38:20','ninguno',0.00,'','normal','2025-12-11 14:38:20','Sin Retraso','pendiente'),(38,43,40,20,'2025-12-11 14:39:17','ninguno',0.00,'','normal','2025-12-11 14:39:17','Sin Retraso','no'),(39,45,41,21,'2025-12-11 14:50:02','ninguno',0.00,'','normal','2025-12-11 14:50:02','Sin Retraso','renovacion'),(40,46,41,21,'2025-12-11 14:51:23','ninguno',0.00,'','normal','2025-12-11 14:51:23','Sin Retraso','renovacion'),(41,47,41,21,'2025-12-11 14:53:10','ninguno',0.00,'','normal','2025-12-11 14:53:10','Sin Retraso','no'),(42,51,48,24,'2026-01-06 19:04:35','ninguno',0.00,'','normal','2026-01-06 19:04:35','Sin Retraso','no'),(43,62,52,26,'2026-01-09 19:22:55','ninguno',0.00,'','normal','2026-01-09 19:22:55','Sin Retraso','renovacion'),(44,63,52,26,'2026-01-09 19:25:24','ninguno',0.00,'','normal','2026-01-09 19:25:24','Sin Retraso','no'),(45,85,56,28,'2026-01-21 19:31:49','ninguno',0.00,'','normal','2026-01-21 19:31:49','Sin Retraso','no'),(46,86,55,27,'2026-01-22 15:06:47','ninguno',0.00,'','normal','2026-01-22 15:06:47','Retraso Pagado','no'),(47,88,57,29,'2026-01-22 18:01:47','ninguno',0.00,'','normal','2026-01-22 18:01:47','Sin Retraso','no'),(48,91,61,31,'2026-01-22 19:57:46','ninguno',0.00,'','normal','2026-01-22 19:57:46','Retraso Pagado','no'),(49,94,59,32,'2026-01-23 14:34:46','ninguno',0.00,'','normal','2026-01-23 14:34:46','Sin Retraso','pendiente'),(50,95,59,32,'2026-01-23 14:36:26','ninguno',0.00,'','normal','2026-01-23 14:36:26','Sin Retraso','no'),(51,96,62,33,'2026-01-23 14:37:52','ninguno',0.00,'','normal','2026-01-23 14:37:52','Sin Retraso','pendiente'),(52,97,62,33,'2026-01-23 14:38:35','ninguno',0.00,'','normal','2026-01-23 14:38:35','Sin Retraso','no'),(53,98,58,30,'2026-01-23 17:02:46','ninguno',0.00,'','normal','2026-01-23 17:02:46','Sin Retraso','no'),(54,100,63,34,'2026-01-24 03:42:36','ninguno',0.00,'','normal','2026-01-24 03:42:36','Sin Retraso','pendiente'),(55,101,63,34,'2026-01-24 03:43:54','ninguno',0.00,'','normal','2026-01-24 03:43:54','Sin Retraso','no');
/*!40000 ALTER TABLE `notas_entrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_entrada_detalle`
--

DROP TABLE IF EXISTS `notas_entrada_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_entrada_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nota_entrada_id` int NOT NULL,
  `id_pieza` int NOT NULL,
  `cantidad_esperada` int NOT NULL,
  `cantidad_recibida` int DEFAULT NULL,
  `cantidad_buena` int DEFAULT '0',
  `cantidad_danada` int DEFAULT '0',
  `cantidad_sucia` int DEFAULT '0',
  `cantidad_perdida` int DEFAULT '0',
  `observaciones_pieza` text,
  PRIMARY KEY (`id`),
  KEY `id_pieza` (`id_pieza`),
  KEY `idx_nota_entrada` (`nota_entrada_id`),
  CONSTRAINT `notas_entrada_detalle_ibfk_1` FOREIGN KEY (`nota_entrada_id`) REFERENCES `notas_entrada` (`id`) ON DELETE CASCADE,
  CONSTRAINT `notas_entrada_detalle_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`)
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_entrada_detalle`
--

LOCK TABLES `notas_entrada_detalle` WRITE;
/*!40000 ALTER TABLE `notas_entrada_detalle` DISABLE KEYS */;
INSERT INTO `notas_entrada_detalle` VALUES (1,1,7,4,4,4,0,0,0,''),(2,1,5,2,2,2,0,0,0,''),(3,1,4,2,2,2,0,0,0,''),(4,2,12,1,1,1,0,0,0,''),(5,3,7,16,16,16,0,0,0,''),(6,3,5,8,8,8,0,0,0,''),(7,3,1,8,8,8,0,0,0,''),(8,3,8,2,2,2,0,0,0,''),(9,4,7,28,16,16,0,0,0,''),(10,4,5,14,8,8,0,0,0,''),(11,4,3,6,0,0,0,0,0,''),(12,4,1,8,8,8,0,0,0,''),(13,4,8,3,3,3,0,0,0,''),(14,5,7,8,8,8,0,0,0,''),(15,5,5,4,4,4,0,0,0,''),(16,5,3,4,4,4,0,0,0,''),(17,5,8,1,0,0,0,0,0,''),(18,6,7,4,4,4,0,0,0,''),(19,6,5,2,2,2,0,0,0,''),(20,6,1,2,2,2,0,0,0,''),(21,6,8,1,0,0,0,0,0,''),(22,7,11,3,2,2,0,0,0,''),(23,8,11,1,1,1,0,0,0,''),(24,9,8,2,1,1,0,0,0,''),(37,20,8,1,1,1,0,0,0,''),(39,21,10,3,3,3,0,0,0,''),(40,22,7,4,4,4,0,0,0,''),(41,22,5,2,2,2,0,0,0,''),(42,22,3,2,2,2,0,0,0,''),(43,23,7,4,4,4,0,0,0,''),(44,23,5,2,2,2,0,0,0,''),(45,23,4,2,2,2,0,0,0,''),(46,23,10,4,1,1,0,0,0,''),(47,24,10,3,3,3,0,0,0,''),(48,25,10,5,3,3,0,0,0,''),(49,26,10,2,2,2,0,0,0,''),(50,27,10,4,2,2,0,0,0,''),(51,28,10,2,2,2,0,0,0,''),(52,29,10,4,2,2,0,0,0,''),(53,30,10,2,2,2,0,0,0,''),(54,31,10,4,2,2,0,0,0,''),(55,32,10,2,2,2,0,0,0,''),(56,33,8,4,2,2,0,0,0,''),(57,34,8,2,2,2,0,0,0,''),(58,35,10,4,2,2,0,0,0,''),(59,36,10,2,2,2,0,0,0,''),(60,37,10,4,2,2,0,0,0,''),(61,38,10,2,2,2,0,0,0,''),(62,39,10,5,3,3,0,0,0,''),(63,40,10,2,1,1,0,0,0,''),(64,41,10,1,1,1,0,0,0,''),(65,42,7,8,8,8,0,0,0,''),(66,42,5,4,4,4,0,0,0,''),(67,42,3,4,4,4,0,0,0,''),(68,42,8,1,1,1,0,0,0,''),(69,43,7,4,0,0,0,0,0,''),(70,43,5,2,1,1,0,0,0,''),(71,43,4,2,2,2,0,0,0,''),(72,44,7,4,4,4,0,0,0,''),(73,44,5,1,1,1,0,0,0,''),(74,45,7,40,40,40,0,0,0,''),(75,45,16,1,1,1,0,0,0,''),(76,45,5,20,20,20,0,0,0,''),(77,45,4,10,10,10,0,0,0,''),(78,45,1,10,10,10,0,0,0,''),(79,45,8,10,10,10,0,0,0,''),(80,45,10,51,51,51,0,0,0,''),(81,46,7,16,16,16,0,0,0,''),(82,46,5,8,8,8,0,0,0,''),(83,46,3,4,4,4,0,0,0,''),(84,46,1,4,4,4,0,0,0,''),(85,46,10,8,8,8,0,0,0,''),(86,46,12,1,1,1,0,0,0,''),(87,46,9,2,2,2,0,0,0,''),(88,47,7,200,200,150,0,0,50,''),(89,47,6,100,100,100,0,50,0,''),(90,47,2,100,100,65,20,0,15,''),(91,48,7,12,12,12,0,0,0,''),(92,48,5,6,6,6,0,0,0,''),(93,48,11,1,1,1,0,0,0,''),(94,48,4,6,6,6,0,0,0,''),(95,49,7,16,13,12,1,0,0,''),(96,49,5,8,8,8,0,1,0,''),(97,49,4,8,8,8,0,1,0,''),(98,49,10,5,5,5,0,0,0,''),(99,50,7,3,3,3,0,0,0,''),(100,51,7,4,2,2,0,0,0,''),(101,51,5,2,2,1,1,0,0,''),(102,51,4,2,2,2,0,0,0,''),(103,52,7,2,2,2,0,0,0,''),(104,53,7,12,12,11,1,0,0,''),(105,53,5,6,6,6,0,1,0,''),(106,53,4,6,6,4,1,0,1,''),(107,53,8,3,3,3,0,0,0,''),(108,54,7,20,20,19,1,0,0,''),(109,54,5,10,8,8,0,1,0,''),(110,54,4,10,10,10,0,0,0,''),(111,55,5,2,2,2,0,0,0,'');
/*!40000 ALTER TABLE `notas_entrada_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_salida`
--

DROP TABLE IF EXISTS `notas_salida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_salida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `folio` int NOT NULL,
  `numero_referencia` varchar(100) DEFAULT NULL,
  `renta_id` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `observaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `renta_id` (`renta_id`),
  CONSTRAINT `notas_salida_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_salida`
--

LOCK TABLES `notas_salida` WRITE;
/*!40000 ALTER TABLE `notas_salida` DISABLE KEYS */;
INSERT INTO `notas_salida` VALUES (1,1,'',2,'2025-11-24 09:59:52',''),(2,2,'',3,'2025-11-24 12:19:21',''),(3,3,'',4,'2025-11-24 12:20:49',''),(4,4,'',5,'2025-11-24 12:21:14',''),(5,1,'',6,'2025-11-27 12:01:45',''),(6,3,'',7,'2025-11-27 12:36:15',''),(7,6,'',10,'2025-12-02 11:16:42',''),(8,10,'',16,'2025-12-02 12:32:09',''),(9,13,'',17,'2025-12-02 12:43:04',''),(10,15,'',20,'2025-12-02 13:06:36',''),(11,18,'',22,'2025-12-08 12:36:00',''),(12,20,'',24,'2025-12-09 08:34:16',''),(13,23,'',25,'2025-12-09 08:55:04',''),(14,26,'',27,'2025-12-09 09:15:22',''),(15,29,'',29,'2025-12-09 09:24:12',''),(16,31,'',31,'2025-12-10 12:26:23',''),(17,34,'',33,'2025-12-10 12:36:25',''),(18,37,'',37,'2025-12-10 14:24:02',''),(19,38,'',38,'2025-12-10 14:25:21',''),(20,41,'',40,'2025-12-11 08:37:15',''),(21,44,'',41,'2025-12-11 08:49:18',''),(22,48,'',46,'2026-01-06 08:30:29',''),(23,49,'',47,'2026-01-06 09:02:29','NO SON PUNTALES, SON RUEDAS, EN EL INVENTARIO NO LO TENGO ASOCIADO BIEN '),(24,50,'',48,'2026-01-06 13:04:16',''),(25,60,'',50,'2026-01-09 13:16:25',''),(26,61,'',52,'2026-01-09 13:19:49',''),(27,83,'',55,'2026-01-19 08:42:33',''),(28,84,'9821316654',56,'2026-01-21 09:27:19',''),(29,87,'',57,'2026-01-22 12:00:13',''),(30,89,'9821316654',58,'2026-01-22 12:07:22',''),(31,90,'',61,'2026-01-22 12:52:18',''),(32,92,'',59,'2026-01-22 14:10:57',''),(33,93,'',62,'2026-01-23 08:32:30',''),(34,99,'9821316654',63,'2026-01-23 21:28:55','');
/*!40000 ALTER TABLE `notas_salida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notas_salida_detalle`
--

DROP TABLE IF EXISTS `notas_salida_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notas_salida_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nota_salida_id` int NOT NULL,
  `id_pieza` int NOT NULL,
  `cantidad` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `nota_salida_id` (`nota_salida_id`),
  KEY `id_pieza` (`id_pieza`),
  CONSTRAINT `notas_salida_detalle_ibfk_1` FOREIGN KEY (`nota_salida_id`) REFERENCES `notas_salida` (`id`),
  CONSTRAINT `notas_salida_detalle_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notas_salida_detalle`
--

LOCK TABLES `notas_salida_detalle` WRITE;
/*!40000 ALTER TABLE `notas_salida_detalle` DISABLE KEYS */;
INSERT INTO `notas_salida_detalle` VALUES (5,1,1,8),(6,1,5,8),(7,1,7,16),(8,1,8,2),(9,2,1,8),(10,2,5,14),(11,2,7,28),(12,2,8,3),(13,2,3,6),(14,3,1,2),(15,3,5,2),(16,3,7,4),(17,3,8,1),(18,4,3,4),(19,4,5,4),(20,4,7,8),(21,4,8,1),(22,5,4,2),(23,5,5,2),(24,5,7,4),(25,6,12,1),(26,7,1,10),(27,7,5,10),(28,7,7,20),(29,7,8,4),(30,8,11,3),(31,9,8,2),(32,10,10,3),(33,11,3,2),(34,11,5,2),(35,11,7,4),(36,12,4,2),(37,12,5,2),(38,12,7,4),(39,12,10,4),(40,13,10,5),(41,14,10,4),(42,15,10,4),(43,16,10,4),(44,17,8,4),(45,19,10,4),(46,20,10,4),(47,21,10,5),(48,22,4,2),(49,22,5,2),(50,22,7,4),(51,23,1,20),(52,23,5,20),(53,23,7,40),(54,23,8,8),(55,23,10,4),(56,24,3,4),(57,24,5,4),(58,24,7,8),(59,24,8,1),(60,26,4,2),(61,26,5,2),(62,26,7,4),(63,27,3,4),(64,27,5,8),(65,27,7,16),(66,27,12,1),(67,27,9,2),(68,27,10,8),(69,27,1,4),(70,28,4,10),(71,28,5,20),(72,28,7,40),(73,28,1,10),(74,28,10,51),(75,28,8,10),(76,28,16,1),(77,29,2,100),(78,29,6,100),(79,29,7,200),(80,30,4,6),(81,30,5,6),(82,30,7,12),(83,30,8,3),(84,31,4,6),(85,31,5,6),(86,31,7,12),(87,31,11,1),(88,32,4,8),(89,32,5,8),(90,32,7,16),(91,32,10,5),(92,33,4,2),(93,33,5,2),(94,33,7,4),(95,34,4,10),(96,34,5,10),(97,34,7,20);
/*!40000 ALTER TABLE `notas_salida_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_reset_tokens`
--

DROP TABLE IF EXISTS `password_reset_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `password_reset_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `token` varchar(128) NOT NULL,
  `expires_at` datetime NOT NULL,
  `usado` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `password_reset_tokens_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_reset_tokens`
--

LOCK TABLES `password_reset_tokens` WRITE;
/*!40000 ALTER TABLE `password_reset_tokens` DISABLE KEYS */;
INSERT INTO `password_reset_tokens` VALUES (8,2,'CJjzyfKaTdp-RmplwH_gmSjT6s3b6MvZvOszTGQ99Gk','2026-01-06 13:26:20',0),(9,2,'Yj2o_YBS82_vE4pUAyZgiJ1oykJMOwYKYBW-tA_dX8c','2026-01-06 13:34:54',1),(10,2,'E-VIooGWCSOj5gRoFnViF5lk_qu6XbDUtSwrfkLoseQ','2026-01-06 13:52:36',1);
/*!40000 ALTER TABLE `password_reset_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES (1,'ver_clientes','Ver la lista de clientes'),(2,'crear_cliente','Registrar un nuevo cliente'),(3,'editar_cliente','Editar datos de un cliente'),(4,'baja_cliente','Dar de baja a un cliente'),(5,'reactivar_cliente','Reactivar un cliente dado de baja'),(6,'eliminar_cliente','Eliminar un cliente definitivamente'),(7,'ver_detalle_cliente','Ver el detalle de un cliente'),(8,'buscar_clientes','Buscar clientes por nombre, apellido, teléfono, etc.'),(9,'ver_inventario_general','Ver el inventario general de la empresa'),(10,'agregar_pieza_inventario_general','Agregar piezas al inventario general'),(11,'modificar_existencias_inventario_general','Dar de alta o baja piezas en inventario general'),(12,'transferir_piezas_inventario','Transferir piezas entre sucursales'),(13,'ver_inventario_sucursal','Ver el inventario de la sucursal asignada'),(14,'mandar_pieza_reparacion','Mandar piezas a reparación desde la sucursal'),(15,'regresar_pieza_disponible','Regresar piezas a disponibles desde la sucursal'),(16,'ver_productos','Ver la lista de productos y sus precios'),(17,'crear_producto','Crear un nuevo producto'),(18,'editar_producto','Editar un producto existente'),(19,'baja_producto','Dar de baja (descontinuar) un producto'),(20,'alta_producto','Dar de alta (activar) un producto'),(21,'ver_empleados','Ver la lista de empleados'),(22,'crear_empleado','Registrar un nuevo empleado'),(23,'editar_empleado','Editar datos de un empleado'),(24,'baja_empleado','Dar de baja a un empleado'),(25,'alta_empleado','Dar de alta (reactivar) un empleado'),(26,'gestionar_permisos_empleado','Gestionar permisos individuales de empleados');
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `piezas`
--

DROP TABLE IF EXISTS `piezas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `piezas` (
  `id_pieza` int NOT NULL AUTO_INCREMENT,
  `nombre_pieza` varchar(100) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `descripcion` text,
  `codigo_pieza` varchar(20) DEFAULT NULL,
  `estatus` varchar(20) DEFAULT 'activo',
  PRIMARY KEY (`id_pieza`),
  UNIQUE KEY `codigo_pieza` (`codigo_pieza`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `piezas`
--

LOCK TABLES `piezas` WRITE;
/*!40000 ALTER TABLE `piezas` DISABLE KEYS */;
INSERT INTO `piezas` VALUES (1,'MARCO ESTÁNDAR (2 X 1.52)','Andamios','Alto: 2 m - Ancho: 1.52 m','10','activo'),(2,'MARCO ESTÁNDAR (1 x 1.52)','Andamios','Alto: 1 m - Ancho: 1.52 m','20','activo'),(3,'MARCO ANGOSTO 0.80','Andamios','Altura: 2 m - Ancho: 0.80 m','30','activo'),(4,'MARCO ANGOSTO 1m','Andamios','Altura: 2 m - Ancho: 1 m','40','activo'),(5,'CRUCETAS  ESTÁNDAR','Crucetas','','50','activo'),(6,'CRUCETAS 2.27m','Crucetas','andamio 1x1.52 m','60','activo'),(7,'COPLES','Coples','','70','activo'),(8,'PLATAFORMA MADERA','Plataformas','','80','activo'),(9,'TORNILLOS DE AJUSTE','','','90','activo'),(10,'PUNTALES','','','110','activo'),(11,'ESCALERAS 6m','','','120','activo'),(12,'REVOLVEDORA','','','130','activo'),(13,'MARTILLO DEMOLEDOR ','','','140','activo'),(14,'BAILARINA','','','150','activo'),(15,'VIBRADOR','','','160','activo'),(16,'CORTADORA DE PISO','','','170','activo'),(17,'RUEDAS','','','180 ','descontinuado');
/*!40000 ALTER TABLE `piezas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prefacturas`
--

DROP TABLE IF EXISTS `prefacturas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prefacturas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `renta_id` int NOT NULL,
  `fecha_emision` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `generada` tinyint(1) DEFAULT '0',
  `tipo` enum('inicial','servicio','recargo','renovacion','abono') DEFAULT 'inicial',
  `pagada` tinyint(1) DEFAULT '0',
  `metodo_pago` enum('EFECTIVO','T.DÉBITO','T.CRÉDITO','TRANSFERENCIA') DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT '0.00',
  `monto_recibido` decimal(10,2) DEFAULT NULL,
  `cambio` decimal(10,2) DEFAULT NULL,
  `numero_seguimiento` varchar(100) DEFAULT NULL,
  `observaciones` text,
  `facturable` tinyint(1) NOT NULL DEFAULT '1',
  `folio` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `renta_id` (`renta_id`),
  CONSTRAINT `prefacturas_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prefacturas`
--

LOCK TABLES `prefacturas` WRITE;
/*!40000 ALTER TABLE `prefacturas` DISABLE KEYS */;
INSERT INTO `prefacturas` VALUES (1,2,'2025-11-24 10:00:18',1,'inicial',1,'EFECTIVO',668.00,718.00,50.00,'',NULL,1,0),(2,3,'2025-11-24 12:16:29',1,'inicial',1,'T.DÉBITO',563.76,563.76,0.00,'1',NULL,1,0),(3,4,'2025-11-24 12:32:24',1,'inicial',1,'TRANSFERENCIA',69.60,69.60,0.00,'2',NULL,0,0),(4,5,'2025-11-24 12:33:20',1,'inicial',1,'EFECTIVO',740.00,740.00,0.00,'',NULL,1,0),(5,6,'2025-11-27 12:02:12',1,'inicial',1,'T.DÉBITO',69.60,69.60,0.00,'0',NULL,0,0),(6,7,'2025-11-27 12:36:52',1,'inicial',1,'T.CRÉDITO',522.00,522.00,0.00,'234',NULL,0,0),(7,45,'2025-12-30 14:05:38',1,'abono',1,'EFECTIVO',50.00,50.00,0.00,'',NULL,1,0),(8,45,'2025-12-30 14:08:24',1,'abono',1,'EFECTIVO',89.19,89.20,0.00,'',NULL,1,0),(9,44,'2025-12-30 14:24:32',1,'abono',1,'EFECTIVO',5.28,5.28,0.00,'',NULL,1,0),(10,44,'2025-12-30 14:47:53',1,'abono',1,'EFECTIVO',4.00,4.00,0.00,'',NULL,1,0),(11,43,'2025-12-30 14:51:54',1,'abono',1,'T.DÉBITO',20.84,20.84,0.00,'99',NULL,1,0),(12,43,'2025-12-30 14:56:31',1,'abono',1,'EFECTIVO',7.00,7.00,0.00,'',NULL,1,0),(13,42,'2025-12-30 14:57:38',1,'inicial',1,'EFECTIVO',28.00,30.00,2.00,'',NULL,1,0),(14,45,'2026-01-05 08:37:41',1,'abono',1,'EFECTIVO',0.01,0.01,0.00,'',NULL,0,0),(15,41,'2026-01-05 12:03:55',1,'abono',1,'EFECTIVO',25.00,25.00,0.00,'',NULL,1,0),(16,41,'2026-01-05 12:05:10',1,'abono',1,'EFECTIVO',21.00,25.00,4.00,'',NULL,1,0),(17,40,'2026-01-05 12:23:02',1,'abono',1,'T.DÉBITO',10.12,10.12,0.00,'33',NULL,1,0),(18,40,'2026-01-05 12:23:29',1,'abono',1,'T.DÉBITO',27.00,27.00,0.00,'2',NULL,0,0),(19,39,'2026-01-05 12:31:51',1,'abono',1,'EFECTIVO',20.00,20.00,0.00,'',NULL,1,0),(20,41,'2026-01-05 12:42:06',1,'abono',1,'T.DÉBITO',0.40,0.40,0.00,'0',NULL,0,0),(21,39,'2026-01-05 12:42:42',1,'abono',1,'T.DÉBITO',17.12,17.12,0.00,'00',NULL,1,0),(22,38,'2026-01-05 12:43:31',1,'abono',1,'EFECTIVO',25.00,25.00,0.00,'',NULL,1,0),(23,38,'2026-01-05 12:44:10',1,'abono',1,'EFECTIVO',12.00,15.00,3.00,'',NULL,0,0),(24,46,'2026-01-06 08:32:46',1,'abono',1,'EFECTIVO',30.00,30.00,0.00,'',NULL,1,0),(25,46,'2026-01-06 08:33:21',1,'abono',1,'T.DÉBITO',4.80,4.80,0.00,'23',NULL,1,0),(26,47,'2026-01-06 08:47:01',1,'inicial',1,'T.DÉBITO',3774.64,3774.64,0.00,'3',NULL,1,0),(27,48,'2026-01-06 08:47:27',1,'inicial',1,'EFECTIVO',573.00,700.00,127.00,'',NULL,1,0),(28,48,'2026-01-06 11:56:47',1,'inicial',1,'EFECTIVO',0.00,700.00,700.00,'',NULL,1,0),(29,48,'2026-01-06 11:57:24',1,'abono',1,'T.DÉBITO',573.04,573.04,0.00,'7',NULL,1,0),(30,32,'2026-01-06 11:57:49',1,'inicial',1,'EFECTIVO',74.00,100.00,26.00,'',NULL,1,0),(31,49,'2026-01-06 12:00:31',1,'inicial',1,'EFECTIVO',9.00,10.00,1.00,'',NULL,0,0),(32,49,'2026-01-06 12:04:15',1,'inicial',1,'EFECTIVO',9.00,10.00,1.00,'',NULL,1,0),(33,31,'2026-01-06 12:04:50',1,'inicial',1,'EFECTIVO',74.00,100.00,26.00,'',NULL,1,0),(34,50,'2026-01-06 12:06:02',1,'inicial',1,'EFECTIVO',35.00,100.00,65.00,'',NULL,1,0),(35,51,'2026-01-06 12:07:26',1,'abono',1,'EFECTIVO',15.00,15.00,0.00,'',NULL,1,0),(36,51,'2026-01-06 12:07:54',1,'abono',1,'EFECTIVO',20.00,20.00,0.00,'',NULL,1,0),(37,55,'2026-01-19 15:08:16',1,'inicial',1,'EFECTIVO',1564.00,2000.00,436.00,'',NULL,1,0),(38,56,'2026-01-20 16:24:43',1,'abono',1,'EFECTIVO',10000.00,10000.00,0.00,'',NULL,1,0),(39,56,'2026-01-20 16:26:27',1,'abono',1,'T.DÉBITO',2000.00,2000.00,0.00,'23',NULL,1,0),(40,56,'2026-01-20 16:31:18',1,'abono',1,'EFECTIVO',8265.00,8265.00,0.00,'',NULL,1,0),(41,57,'2026-01-20 16:49:51',1,'abono',1,'EFECTIVO',7000.00,7000.00,0.00,'',NULL,1,0),(42,58,'2026-01-21 08:48:10',1,'abono',1,'EFECTIVO',200.00,200.00,0.00,'',NULL,1,0),(43,59,'2026-01-21 08:51:50',1,'inicial',1,'EFECTIVO',650.00,700.00,50.00,'',NULL,1,0),(44,58,'2026-01-21 08:56:06',1,'abono',1,'EFECTIVO',218.00,300.00,82.00,'',NULL,1,0),(45,60,'2026-01-21 09:00:51',1,'abono',1,'EFECTIVO',500.00,500.00,0.00,'',NULL,1,0),(46,60,'2026-01-21 09:02:43',1,'abono',1,'T.DÉBITO',875.76,875.76,0.00,'89',NULL,1,0),(47,62,'2026-01-23 08:46:31',1,'abono',1,'EFECTIVO',50.00,50.00,0.00,'',NULL,1,0),(48,62,'2026-01-23 08:47:04',1,'abono',1,'EFECTIVO',20.00,25.00,5.00,'',NULL,1,0),(49,63,'2026-01-23 21:36:31',1,'inicial',1,'EFECTIVO',754.00,800.00,46.00,'',NULL,1,0),(50,61,'2026-01-27 09:05:35',1,'inicial',1,'EFECTIVO',605.50,650.00,44.50,'',NULL,1,1);
/*!40000 ALTER TABLE `prefacturas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_piezas`
--

DROP TABLE IF EXISTS `producto_piezas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_piezas` (
  `id_producto` int NOT NULL,
  `id_pieza` int NOT NULL,
  `cantidad` int NOT NULL,
  PRIMARY KEY (`id_producto`,`id_pieza`),
  KEY `id_pieza` (`id_pieza`),
  CONSTRAINT `producto_piezas_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `producto_piezas_ibfk_2` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_piezas`
--

LOCK TABLES `producto_piezas` WRITE;
/*!40000 ALTER TABLE `producto_piezas` DISABLE KEYS */;
INSERT INTO `producto_piezas` VALUES (1,1,2),(1,5,2),(1,7,4),(2,3,2),(2,5,2),(2,7,4),(3,10,1),(4,2,2),(4,6,2),(4,7,4),(5,12,1),(6,11,1),(7,4,2),(7,5,2),(7,7,4),(8,9,1),(9,8,1),(10,10,4),(11,16,1),(12,13,1);
/*!40000 ALTER TABLE `producto_piezas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_precios`
--

DROP TABLE IF EXISTS `producto_precios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto_precios` (
  `id_producto` int NOT NULL,
  `precio_dia` decimal(10,2) DEFAULT NULL,
  `precio_7dias` decimal(10,2) NOT NULL,
  `precio_15dias` decimal(10,2) NOT NULL,
  `precio_30dias` decimal(10,2) NOT NULL,
  `precio_31mas` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id_producto`),
  CONSTRAINT `producto_precios_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_precios`
--

LOCK TABLES `producto_precios` WRITE;
/*!40000 ALTER TABLE `producto_precios` DISABLE KEYS */;
INSERT INTO `producto_precios` VALUES (1,30.00,18.00,17.00,15.00,14.00),(2,30.00,18.00,17.00,15.00,14.00),(3,8.00,8.00,8.00,6.00,6.00),(4,30.00,18.00,17.00,15.00,14.00),(5,450.00,0.00,0.00,0.00,0.00),(6,120.00,120.00,120.00,100.00,100.00),(7,30.00,18.00,17.00,15.00,14.00),(8,20.00,14.00,12.00,10.00,8.00),(9,25.00,12.00,10.00,8.00,7.00),(10,35.00,26.00,20.00,15.00,13.00),(11,320.00,0.00,0.00,0.00,0.00),(12,320.00,320.00,310.00,310.00,310.00);
/*!40000 ALTER TABLE `producto_precios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `tipo` enum('conjunto','individual') NOT NULL,
  `estatus` enum('activo','descontinuado') DEFAULT 'activo',
  `precio_unico` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'ANDAMIO ESTANDAR 2x1.52','Alto: 2 m - Ancho: 1.52 m','conjunto','activo',0),(2,'ANDAMIO ANGOSTO 0.80','Alto: 2m - Ancho: 0.80','conjunto','activo',0),(3,'PUNTALES 3m','descripción puntales','individual','activo',0),(4,'ANDAMIO ESTÁNDAR 1x1.52','Alto: 1m - Ancho: 1.52m','conjunto','activo',0),(5,'REVOLVEDORA','','individual','activo',1),(6,'ESCALERA 6m','Min. 3m - Max. 6m','individual','activo',0),(7,'ANDAMIO ANGOSTO 1m','Alto: 2m - Ancho: 1m','conjunto','activo',0),(8,'TORNILLO NIVELADOR','','individual','activo',0),(9,'PLATAFORMA','Plataforma madera','individual','activo',0),(10,'RUEDAS','Juego 4 pzs','conjunto','activo',0),(11,'CORTADORA DE PISO','','individual','activo',1),(12,'MARTILLO DEMOLEDOR','','individual','activo',1);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `renta_detalle`
--

DROP TABLE IF EXISTS `renta_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `renta_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `renta_id` int DEFAULT NULL,
  `id_producto` int NOT NULL,
  `cantidad` int NOT NULL,
  `dias_renta` int DEFAULT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `renta_id` (`renta_id`),
  KEY `id_producto` (`id_producto`),
  CONSTRAINT `renta_detalle_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `renta_detalle_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `renta_detalle`
--

LOCK TABLES `renta_detalle` WRITE;
/*!40000 ALTER TABLE `renta_detalle` DISABLE KEYS */;
INSERT INTO `renta_detalle` VALUES (3,1,1,4,6,18.00,432.00),(4,2,1,4,6,18.00,432.00),(5,2,9,2,6,12.00,144.00),(6,3,1,4,3,18.00,216.00),(7,3,9,3,3,12.00,108.00),(8,3,2,3,3,18.00,162.00),(9,4,1,1,2,18.00,36.00),(10,4,9,1,2,12.00,24.00),(11,5,2,2,6,18.00,216.00),(12,5,9,1,6,12.00,72.00),(13,6,7,1,2,30.00,60.00),(14,7,5,1,1,450.00,450.00),(15,8,4,1,1,30.00,30.00),(16,9,1,2,2,30.00,120.00),(17,9,9,2,2,25.00,100.00),(18,10,1,5,1,30.00,150.00),(19,10,9,4,1,25.00,100.00),(20,11,1,4,7,18.00,504.00),(21,11,9,3,7,12.00,252.00),(22,11,2,3,7,18.00,378.00),(23,12,1,4,4,18.00,288.00),(24,12,9,3,4,12.00,144.00),(25,12,2,3,4,18.00,216.00),(26,13,2,2,6,18.00,216.00),(27,13,9,1,6,12.00,72.00),(28,14,2,2,6,18.00,216.00),(29,14,9,1,6,12.00,72.00),(30,15,1,1,2,18.00,36.00),(31,15,9,1,2,12.00,24.00),(32,16,6,3,2,120.00,720.00),(33,17,9,2,2,25.00,100.00),(34,18,9,1,3,25.00,75.00),(35,19,9,1,3,25.00,75.00),(36,20,3,3,1,8.00,24.00),(37,21,3,3,7,8.00,168.00),(38,22,2,1,1,30.00,30.00),(39,23,2,1,1,30.00,30.00),(40,24,7,1,1,30.00,30.00),(41,24,3,4,1,8.00,32.00),(42,25,3,5,1,8.00,40.00),(43,26,3,3,2,8.00,48.00),(44,27,3,4,1,8.00,32.00),(45,28,3,2,1,8.00,16.00),(46,29,3,4,1,8.00,32.00),(47,30,3,2,1,8.00,16.00),(48,31,3,4,2,8.00,64.00),(49,32,3,4,2,8.00,64.00),(50,33,9,4,1,25.00,100.00),(51,34,9,4,1,25.00,100.00),(52,35,9,4,1,25.00,100.00),(53,36,9,4,1,25.00,100.00),(54,37,5,2,1,450.00,900.00),(55,38,3,4,1,8.00,32.00),(56,39,3,2,2,8.00,32.00),(57,40,3,4,1,8.00,32.00),(58,41,3,5,1,8.00,40.00),(59,42,3,3,1,8.00,24.00),(60,43,3,3,1,8.00,24.00),(61,44,3,1,1,8.00,8.00),(62,45,6,1,1,120.00,120.00),(63,46,7,1,1,30.00,30.00),(64,47,1,10,6,18.00,1080.00),(65,47,9,8,6,12.00,576.00),(66,47,10,8,6,26.00,1248.00),(67,48,2,2,3,18.00,108.00),(68,48,9,1,3,12.00,36.00),(69,49,3,1,1,8.00,8.00),(70,50,2,1,1,30.00,30.00),(71,51,2,1,1,30.00,30.00),(72,52,7,1,1,30.00,30.00),(73,53,7,1,1,30.00,30.00),(74,54,7,1,1,30.00,30.00),(75,55,2,2,2,30.00,120.00),(76,55,5,1,2,450.00,900.00),(77,55,8,2,2,20.00,80.00),(78,55,3,8,2,8.00,128.00),(79,55,1,2,2,30.00,120.00),(80,56,7,5,20,15.00,1500.00),(81,56,1,5,20,15.00,1500.00),(82,56,3,50,20,6.00,6000.00),(83,56,3,1,20,6.00,120.00),(84,56,9,10,20,8.00,1600.00),(85,56,11,1,20,320.00,6400.00),(86,57,4,50,12,17.00,10200.00),(87,58,7,3,4,18.00,216.00),(88,58,9,3,4,12.00,144.00),(89,59,7,4,5,18.00,360.00),(90,59,3,5,5,8.00,200.00),(91,60,2,2,8,17.00,272.00),(92,60,4,2,8,17.00,272.00),(93,60,9,4,8,10.00,320.00),(94,61,7,3,3,18.00,162.00),(95,61,6,1,3,120.00,360.00),(96,62,7,1,2,30.00,60.00),(97,63,7,5,2,30.00,300.00);
/*!40000 ALTER TABLE `renta_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rentas`
--

DROP TABLE IF EXISTS `rentas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rentas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `id_sucursal` int DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `fecha_salida` date DEFAULT NULL,
  `fecha_entrada` date DEFAULT NULL,
  `direccion_obra` text,
  `estado_renta` varchar(20) DEFAULT 'activa',
  `estado_pago` varchar(20) DEFAULT 'pendiente',
  `estado_cobro_extra` varchar(20) DEFAULT NULL,
  `total` decimal(10,2) DEFAULT '0.00',
  `iva` decimal(10,2) DEFAULT '0.00',
  `total_con_iva` decimal(10,2) DEFAULT '0.00',
  `observaciones` text,
  `fecha_programada` date DEFAULT NULL,
  `costo_traslado` decimal(10,2) DEFAULT '0.00',
  `traslado` varchar(100) DEFAULT NULL,
  `metodo_pago` varchar(55) DEFAULT NULL,
  `renta_asociada_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  KEY `fk_rentas_sucursal` (`id_sucursal`),
  CONSTRAINT `fk_rentas_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `rentas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rentas`
--

LOCK TABLES `rentas` WRITE;
/*!40000 ALTER TABLE `rentas` DISABLE KEYS */;
INSERT INTO `rentas` VALUES (1,3,1,'2025-11-24 09:57:24','2025-11-24','2025-11-29','Taller, colonia Ignazio Zaragoza','eliminada','Pago pendiente',NULL,432.00,69.12,501.12,'',NULL,0.00,'ninguno','Pendiente',NULL),(2,3,1,'2025-11-24 09:58:24','2025-11-24','2025-11-29','Taller, Ignacio Zaragoza','finalizada','Pago realizado',NULL,576.00,92.16,668.16,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(3,4,1,'2025-11-24 12:12:51','2025-11-24','2025-11-26','Tienda Neto','activo','Pago realizado',NULL,486.00,77.76,563.76,'',NULL,0.00,'ninguno','T.DÉBITO',NULL),(4,2,1,'2025-11-24 12:14:12','2025-11-24','2025-11-25','Señor no se qué','activa renovación','Pago realizado',NULL,60.00,9.60,69.60,'',NULL,0.00,'ninguno','TRANSFERENCIA',NULL),(5,1,1,'2025-11-24 12:18:18','2025-11-24','2025-11-29','Felipe Catillo','activa renovación','Pago realizado',NULL,638.00,102.08,740.08,'',NULL,350.00,'redondo','EFECTIVO',NULL),(6,2,2,'2025-11-27 12:01:15','2025-11-27','2025-11-28','prueba','finalizada','Pago realizado',NULL,60.00,9.60,69.60,'',NULL,0.00,'ninguno','T.DÉBITO',NULL),(7,2,2,'2025-11-27 12:35:59','2025-11-27','2025-11-27','prueba','finalizada','Reembolsado',NULL,450.00,72.00,522.00,'',NULL,0.00,'ninguno','T.CRÉDITO',NULL),(8,2,3,'2025-11-28 15:06:31','2025-11-28',NULL,'jjj','en curso','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',NULL),(9,2,1,'2025-11-28 16:58:09','2025-11-28','2025-11-29','Tienda Neto','en curso','Pago pendiente',NULL,220.00,35.20,255.20,'',NULL,0.00,'ninguno','Pendiente',NULL),(10,3,1,'2025-11-28 16:59:22','2025-11-28',NULL,'Arqui. Medina','Activo','Pago pendiente',NULL,250.00,40.00,290.00,'',NULL,0.00,'ninguno','Pendiente',NULL),(11,4,1,'2025-12-01 16:49:33','2025-11-26','2025-12-02','Tienda Neto','activa renovación','Pago pendiente',NULL,1134.00,181.44,1315.44,'',NULL,0.00,'ninguno','Pendiente',3),(12,4,1,'2025-12-02 12:04:54','2025-12-02','2025-12-05','Tienda Neto','activa renovación','Pago pendiente',NULL,648.00,103.68,751.68,'',NULL,0.00,'ninguno','Pendiente',11),(13,1,1,'2025-12-02 12:14:23','2025-11-24','2025-11-29','Felipe Catillo','activa renovación','Pago pendiente',NULL,288.00,46.08,334.08,'',NULL,350.00,'redondo','Pendiente',5),(14,1,1,'2025-12-02 12:15:00','2025-11-24','2025-11-29','Felipe Catillo','activa renovación','Pago pendiente',NULL,288.00,46.08,334.08,'',NULL,350.00,'redondo','Pendiente',5),(15,2,1,'2025-12-02 12:23:59','2025-11-24','2025-11-25','Señor no se qué','activa renovación','Pago pendiente',NULL,60.00,9.60,69.60,'',NULL,0.00,'ninguno','Pendiente',4),(16,3,1,'2025-12-02 12:31:58','2025-12-01','2025-12-02','bhjvhj','finalizada','Pago pendiente',NULL,720.00,115.20,835.20,'',NULL,0.00,'ninguno','Pendiente',NULL),(17,4,1,'2025-12-02 12:42:54','2025-12-01','2025-12-02','sfwfew','finalizada','Pago pendiente',NULL,100.00,16.00,116.00,'',NULL,0.00,'ninguno','Pendiente',NULL),(18,4,1,'2025-12-02 12:56:49','2025-12-02','2025-12-04','sfwfew','renovación finalizad','Pago pendiente',NULL,75.00,12.00,87.00,'',NULL,0.00,'ninguno','Pendiente',17),(19,4,1,'2025-12-02 12:56:51','2025-12-02','2025-12-04','sfwfew','renovación finalizad','Pago pendiente',NULL,75.00,12.00,87.00,'',NULL,0.00,'ninguno','Pendiente',17),(20,4,1,'2025-12-02 13:05:32','2025-12-02','2025-12-02','h','finalizada','Pago pendiente',NULL,24.00,3.84,27.84,'',NULL,0.00,'ninguno','Pendiente',NULL),(21,4,1,'2025-12-08 12:10:58','2025-12-03','2025-12-09','h','renovación finalizad','Pago pendiente',NULL,168.00,26.88,194.88,'',NULL,0.00,'ninguno','Pendiente',20),(22,2,1,'2025-12-08 12:35:33','2025-12-08','2025-12-08','lllll','finalizada','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',NULL),(23,2,1,'2025-12-08 12:37:11','2025-12-09','2025-12-09','lllll','renovación finalizad','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',22),(24,2,1,'2025-12-09 08:33:23','2025-12-07','2025-12-07','prueba','finalizada','Pago pendiente',NULL,62.00,9.92,71.92,'',NULL,0.00,'ninguno','Pendiente',NULL),(25,2,1,'2025-12-09 08:54:13','2025-12-07','2025-12-07','prueba','finalizada','Pago pendiente',NULL,40.00,6.40,46.40,'',NULL,0.00,'ninguno','Pendiente',NULL),(26,2,1,'2025-12-09 08:57:03','2025-12-08','2025-12-09','prueba','renovación finalizad','Pago pendiente',NULL,48.00,7.68,55.68,'',NULL,0.00,'ninguno','Pendiente',25),(27,4,1,'2025-12-09 09:14:10','2025-12-07','2025-12-07','fwefewfew','finalizada','Pago pendiente',NULL,32.00,5.12,37.12,'',NULL,0.00,'ninguno','Pendiente',NULL),(28,4,1,'2025-12-09 09:16:38','2025-12-08','2025-12-08','fwefewfew','renovación finalizad','Pago pendiente',NULL,16.00,2.56,18.56,'',NULL,0.00,'ninguno','Pendiente',27),(29,1,1,'2025-12-09 09:23:40','2025-12-07','2025-12-07','nhhhhh','finalizada','Pago pendiente',NULL,32.00,5.12,37.12,'',NULL,0.00,'ninguno','Pendiente',NULL),(30,1,1,'2025-12-09 09:25:52','2025-12-07','2025-12-07','nhhhhh','renovación finalizad','Pago pendiente',NULL,16.00,2.56,18.56,'',NULL,0.00,'ninguno','Pendiente',29),(31,2,1,'2025-12-10 12:26:08','2025-12-09','2025-12-10','jjj','finalizada','Saldo pendiente',NULL,64.00,10.24,74.24,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(32,2,1,'2025-12-10 12:27:06','2025-12-11','2025-12-12','jjj','renovación finalizad','Saldo pendiente',NULL,64.00,10.24,74.24,'',NULL,0.00,'ninguno','EFECTIVO',31),(33,2,1,'2025-12-10 12:35:42','2025-12-10','2025-12-10','kkk','finalizada','Pago pendiente',NULL,100.00,16.00,116.00,'',NULL,0.00,'ninguno','Pendiente',NULL),(34,2,1,'2025-12-10 12:37:12','2025-12-11','2025-12-11','kkk','renovación finalizad','Pago pendiente',NULL,100.00,16.00,116.00,'',NULL,0.00,'ninguno','Pendiente',33),(35,2,1,'2025-12-10 12:37:13','2025-12-11','2025-12-11','kkk','renovación finalizad','Pago pendiente',NULL,100.00,16.00,116.00,'',NULL,0.00,'ninguno','Pendiente',33),(36,2,1,'2025-12-10 12:37:16','2025-12-11','2025-12-11','kkk','renovación finalizad','Pago pendiente',NULL,100.00,16.00,116.00,'',NULL,0.00,'ninguno','Pendiente',33),(37,3,1,'2025-12-10 14:23:42','2025-12-09','2025-12-09','lll','cancelada','Reembolsado',NULL,900.00,144.00,1044.00,'',NULL,0.00,'ninguno','Pendiente',NULL),(38,2,1,'2025-12-10 14:24:57','2025-12-09','2025-12-09','ppp','finalizada','Saldo pendiente',NULL,32.00,5.12,37.12,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(39,2,1,'2025-12-10 14:29:10','2025-12-10','2025-12-11','ppp','renovación finalizad','Pago realizado',NULL,32.00,5.12,37.12,'',NULL,0.00,'ninguno','T.DÉBITO',38),(40,4,1,'2025-12-11 08:34:20','2025-12-11','2025-12-11','reee','finalizada','Pago realizado',NULL,32.00,5.12,37.12,'',NULL,0.00,'ninguno','T.DÉBITO',NULL),(41,3,1,'2025-12-11 08:48:30','2025-12-11','2025-12-11','qqqq','finalizada','Pago realizado',NULL,40.00,6.40,46.40,'',NULL,0.00,'ninguno','T.DÉBITO',NULL),(42,3,1,'2025-12-11 08:50:45','2025-12-12','2025-12-12','qqqq','renovación finalizad','Pago realizado',NULL,24.00,3.84,27.84,'',NULL,0.00,'ninguno','EFECTIVO',41),(43,3,1,'2025-12-11 08:50:47','2025-12-12','2025-12-12','qqqq','renovación finalizad','Pago realizado',NULL,24.00,3.84,27.84,'',NULL,0.00,'ninguno','EFECTIVO',41),(44,3,1,'2025-12-11 08:51:52','2025-12-11','2025-12-11','qqqq','renovación finalizad','Pago realizado',NULL,8.00,1.28,9.28,'',NULL,0.00,'ninguno','EFECTIVO',41),(45,1,1,'2025-12-30 08:44:23','2025-12-30','2025-12-30','eeeeee','en curso','Pago realizado',NULL,120.00,19.20,139.20,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(46,2,1,'2026-01-06 08:30:16','2026-01-06','2026-01-06','pruebas','Activo','Pago realizado',NULL,30.00,4.80,34.80,'',NULL,0.00,'redondo','T.DÉBITO',NULL),(47,4,1,'2026-01-06 08:38:40','2026-01-06','2026-01-11','Escuela Miguel Hidalgo','Activo','Pago realizado',NULL,3254.00,520.64,3774.64,'',NULL,350.00,'redondo','T.DÉBITO',NULL),(48,4,1,'2026-01-06 08:46:27','2026-01-06','2026-01-08','Fovisste Pablo García','finalizada','Pago realizado',NULL,494.00,79.04,573.04,'',NULL,350.00,'redondo','T.DÉBITO',NULL),(49,2,1,'2026-01-06 11:59:11','2026-01-06','2026-01-06','uuuuu','en curso','Pago realizado',NULL,8.00,1.28,9.28,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(50,4,1,'2026-01-06 12:05:36','2026-01-06','2026-01-06','uuiiui','Activo','Pago realizado',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(51,1,1,'2026-01-06 12:06:58','2026-01-06','2026-01-06','uu','cancelada','Reembolsado',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(52,2,1,'2026-01-09 13:18:33','2026-01-09','2026-01-09','www','finalizada','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',NULL),(53,2,1,'2026-01-09 13:20:59','2026-01-10','2026-01-10','www','renovación finalizad','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',52),(54,2,1,'2026-01-09 13:23:53','2026-01-11','2026-01-11','www','renovación finalizad','Pago pendiente',NULL,30.00,4.80,34.80,'',NULL,0.00,'ninguno','Pendiente',52),(55,2,1,'2026-01-19 08:39:20','2026-01-19','2026-01-20','pruebas ','finalizada','Pago realizado',NULL,1348.00,215.68,1563.68,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(56,3,1,'2026-01-20 16:23:51','2026-01-20','2026-02-08','Pruebas del sistema','finalizada','Saldo pendiente',NULL,17470.00,2795.20,20265.20,'',NULL,350.00,'redondo','EFECTIVO',NULL),(57,3,1,'2026-01-20 16:49:10','2026-01-20','2026-01-31','pruebas del sistema','finalizada','Saldo pendiente','Extra Pagado',10200.00,1632.00,11832.00,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(58,3,1,'2026-01-21 08:46:52','2026-01-21','2026-01-24','pruebas de sistema','finalizada','Pago realizado','Extra Pendiente',360.00,57.60,417.60,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(59,3,1,'2026-01-21 08:50:14','2026-01-21','2026-01-25','pruebas del sistema','finalizada','Pago realizado',NULL,560.00,89.60,649.60,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(60,3,1,'2026-01-21 08:59:57','2026-01-21','2026-01-28','pruebas del sistema lasmlñefonrwof kfcnewiofjew noidjwoienfew nfcoijfoiren nfwenjenefoiwenf jknfoinfoiewn wenfoiewnf','en curso','Pago realizado',NULL,1186.00,189.76,1375.76,'',NULL,322.00,'redondo','T.DÉBITO',NULL),(61,3,1,'2026-01-22 12:51:26','2026-01-19','2026-01-21','pruebas','finalizada','Saldo pendiente',NULL,522.00,83.52,605.52,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(62,4,1,'2026-01-22 16:13:20','2026-01-22','2026-01-23','peuebas','finalizada','Pago realizado',NULL,60.00,9.60,69.60,'',NULL,0.00,'ninguno','EFECTIVO',NULL),(63,3,1,'2026-01-23 21:27:49','2026-01-23','2026-01-24','pruebas','finalizada','Pago realizado',NULL,650.00,104.00,754.00,'',NULL,350.00,'redondo','EFECTIVO',NULL);
/*!40000 ALTER TABLE `rentas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rentas_pendientes`
--

DROP TABLE IF EXISTS `rentas_pendientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rentas_pendientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `renta_id` int NOT NULL,
  `id_producto` int NOT NULL,
  `id_pieza` int NOT NULL,
  `cantidad_pendiente` int NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` varchar(30) DEFAULT 'pendiente',
  `renta_renovacion_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `renta_id` (`renta_id`),
  KEY `id_producto` (`id_producto`),
  KEY `id_pieza` (`id_pieza`),
  KEY `renta_renovacion_id` (`renta_renovacion_id`),
  CONSTRAINT `rentas_pendientes_ibfk_1` FOREIGN KEY (`renta_id`) REFERENCES `rentas` (`id`),
  CONSTRAINT `rentas_pendientes_ibfk_2` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `rentas_pendientes_ibfk_3` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`),
  CONSTRAINT `rentas_pendientes_ibfk_4` FOREIGN KEY (`renta_renovacion_id`) REFERENCES `rentas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rentas_pendientes`
--

LOCK TABLES `rentas_pendientes` WRITE;
/*!40000 ALTER TABLE `rentas_pendientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `rentas_pendientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'cliente'),(2,'administrador'),(3,'secretaria'),(4,'cargador');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles_permisos`
--

DROP TABLE IF EXISTS `roles_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles_permisos` (
  `rol_id` int NOT NULL,
  `permiso_id` int NOT NULL,
  `permitido` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`rol_id`,`permiso_id`),
  KEY `permiso_id` (`permiso_id`),
  CONSTRAINT `roles_permisos_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `roles_permisos_ibfk_2` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles_permisos`
--

LOCK TABLES `roles_permisos` WRITE;
/*!40000 ALTER TABLE `roles_permisos` DISABLE KEYS */;
INSERT INTO `roles_permisos` VALUES (2,1,1),(2,2,1),(2,3,1),(2,4,1),(2,5,1),(2,6,1),(2,7,1),(2,8,1),(2,9,1),(2,10,1),(2,11,1),(2,12,1),(2,13,1),(2,14,1),(2,15,1),(2,16,1),(2,17,1),(2,18,1),(2,19,1),(2,20,1),(2,21,1),(2,22,1),(2,23,1),(2,24,1),(2,25,1),(2,26,1),(3,1,1),(3,2,1),(3,3,1),(3,4,1),(3,5,1),(3,6,1),(3,7,1),(3,8,1),(3,13,1),(3,14,1),(3,15,1),(3,16,1),(4,13,1),(4,14,1),(4,15,1);
/*!40000 ALTER TABLE `roles_permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salidas_internas`
--

DROP TABLE IF EXISTS `salidas_internas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salidas_internas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_sucursal` int NOT NULL,
  `folio_sucursal` int NOT NULL,
  `fecha_salida` datetime NOT NULL,
  `responsable_entrega` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Nombre del chofer o persona que se lleva el equipo',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `estado` enum('activa','finalizada_regreso','finalizada_no_regreso','cancelada') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activa',
  `fecha_finalizacion` datetime DEFAULT NULL,
  `observaciones_finalizacion` text COLLATE utf8mb4_unicode_ci,
  `usuario_creacion` int NOT NULL,
  `usuario_finalizacion` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_folio_sucursal` (`id_sucursal`,`folio_sucursal`),
  KEY `idx_sucursal` (`id_sucursal`),
  KEY `idx_folio_sucursal` (`folio_sucursal`),
  KEY `idx_estado` (`estado`),
  KEY `idx_fecha_salida` (`fecha_salida`),
  KEY `fk_salidas_internas_usuario_creacion` (`usuario_creacion`),
  KEY `fk_salidas_internas_usuario_finalizacion` (`usuario_finalizacion`),
  CONSTRAINT `fk_salidas_internas_sucursal` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `fk_salidas_internas_usuario_creacion` FOREIGN KEY (`usuario_creacion`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `fk_salidas_internas_usuario_finalizacion` FOREIGN KEY (`usuario_finalizacion`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabla para registrar salidas internas de equipo (préstamos sin pago)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salidas_internas`
--

LOCK TABLES `salidas_internas` WRITE;
/*!40000 ALTER TABLE `salidas_internas` DISABLE KEYS */;
INSERT INTO `salidas_internas` VALUES (1,1,55,'2026-01-08 14:34:44','josé','contador','activa',NULL,NULL,1,NULL,'2026-01-08 20:34:44','2026-01-08 20:34:44'),(2,1,56,'2026-01-08 14:35:03','josé','contador','activa',NULL,NULL,1,NULL,'2026-01-08 20:35:03','2026-01-08 20:35:03'),(3,1,57,'2026-01-08 14:39:10','eeee','eeee','finalizada_regreso','2026-01-08 14:41:11','',1,1,'2026-01-08 20:39:10','2026-01-08 20:41:11'),(4,1,58,'2026-01-09 13:07:40','gali','conta','activa',NULL,NULL,1,NULL,'2026-01-09 19:07:41','2026-01-09 19:07:41'),(5,1,59,'2026-01-09 13:15:08','josé','ccccccc','activa',NULL,NULL,1,NULL,'2026-01-09 19:15:09','2026-01-09 19:15:09');
/*!40000 ALTER TABLE `salidas_internas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salidas_internas_detalle`
--

DROP TABLE IF EXISTS `salidas_internas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salidas_internas_detalle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `salida_interna_id` int NOT NULL,
  `id_pieza` int NOT NULL,
  `cantidad` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_salida_interna` (`salida_interna_id`),
  KEY `idx_pieza` (`id_pieza`),
  CONSTRAINT `fk_salidas_internas_detalle_pieza` FOREIGN KEY (`id_pieza`) REFERENCES `piezas` (`id_pieza`),
  CONSTRAINT `fk_salidas_internas_detalle_salida` FOREIGN KEY (`salida_interna_id`) REFERENCES `salidas_internas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Detalle de productos en cada salida interna';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salidas_internas_detalle`
--

LOCK TABLES `salidas_internas_detalle` WRITE;
/*!40000 ALTER TABLE `salidas_internas_detalle` DISABLE KEYS */;
INSERT INTO `salidas_internas_detalle` VALUES (1,1,4,2,'2026-01-08 20:34:44'),(2,2,4,2,'2026-01-08 20:35:03'),(3,3,12,1,'2026-01-08 20:39:11'),(4,4,11,1,'2026-01-09 19:07:42'),(5,5,12,1,'2026-01-09 19:15:10'),(6,5,10,1,'2026-01-09 19:15:12'),(7,5,9,1,'2026-01-09 19:15:13');
/*!40000 ALTER TABLE `salidas_internas_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sucursales`
--

DROP TABLE IF EXISTS `sucursales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sucursales`
--

LOCK TABLES `sucursales` WRITE;
/*!40000 ALTER TABLE `sucursales` DISABLE KEYS */;
INSERT INTO `sucursales` VALUES (1,'Matriz Colosio','Dirección de la matriz'),(2,'Sucursal Los Reyes','Dirección Los Reyes'),(3,'Sucursal Lerma','Dirección Lerma');
/*!40000 ALTER TABLE `sucursales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido1` varchar(100) NOT NULL,
  `apellido2` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `requiere_cambio_password` tinyint(1) DEFAULT '1',
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `rol_id` int NOT NULL,
  `sucursal_id` int NOT NULL,
  `foto_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario` (`correo`),
  KEY `fk_usuarios_roles` (`rol_id`),
  KEY `fk_usuarios_sucursales` (`sucursal_id`),
  CONSTRAINT `fk_usuarios_roles` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `fk_usuarios_sucursales` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`sucursal_id`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Administrador','','','admin@colosio.com','$argon2id$v=19$m=65536,t=3,p=4$sqS0iP9ZkrRW+6TamVWsIw$3oznKqzecK/u3oVhZv3UqgoNOkW8I/MpVwZofIQB9eg',0,'activo',2,1,'/static/uploads/1_prueba_3.jpeg'),(2,'Eugenia','Fuentes','Caraveo','eugenia2003fuentes@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$k3pkxox+NMBnbPhBxVsnIQ$/amGcjq4tXF8vb5OlyzC+PhSyVJWi+bH9Ij0tiXo7ag',0,'activo',3,2,'/static/uploads/2_prueba_2.jpg'),(3,'Genny','Fuentees','Caraveoo','al070143@uacam.mx','$argon2id$v=19$m=65536,t=3,p=4$7LlBxy3X7f5j+3PVW6dmbg$pegtpeSqfsKT+NHQrHz8C6AvH8kjK1pvVrz1pvThy0I',0,'activo',2,1,NULL),(8,'Mario','Bernadette','Cuña','eugeniafuentes2003@gmail.com','$argon2id$v=19$m=65536,t=3,p=4$CfXqxH69JxLmnfA/hP1ErA$GuE+yy9PxJsu71TmV0AmwiR0nWfVXAV5SvorM8zdHgY',0,'activo',2,1,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_permisos`
--

DROP TABLE IF EXISTS `usuarios_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios_permisos` (
  `usuario_id` int NOT NULL,
  `permiso_id` int NOT NULL,
  `permitido` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`usuario_id`,`permiso_id`),
  KEY `permiso_id` (`permiso_id`),
  CONSTRAINT `usuarios_permisos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `usuarios_permisos_ibfk_2` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_permisos`
--

LOCK TABLES `usuarios_permisos` WRITE;
/*!40000 ALTER TABLE `usuarios_permisos` DISABLE KEYS */;
INSERT INTO `usuarios_permisos` VALUES (2,1,1),(2,2,0),(2,3,0),(2,4,0),(2,5,1),(2,6,1),(2,7,0),(2,8,1),(2,13,1),(2,14,1),(2,15,1),(2,16,1);
/*!40000 ALTER TABLE `usuarios_permisos` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-27 13:13:50
