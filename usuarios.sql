-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 02-12-2025 a las 18:46:29
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `usuarios`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `perfiles_usuario`
--

CREATE TABLE `perfiles_usuario` (
  `id` int(10) UNSIGNED NOT NULL,
  `usuario_id` int(10) UNSIGNED DEFAULT NULL,
  `altura_cm` decimal(5,2) DEFAULT NULL,
  `peso_actual_kg` decimal(5,2) DEFAULT NULL,
  `peso_objetivo_kg` decimal(5,2) DEFAULT NULL,
  `nivel_actividad` enum('sedentario','ligero','moderado','activo','muy_activo') DEFAULT NULL,
  `objetivo_salud` enum('perder_peso','mantener_peso','ganar_musculo','mejorar_salud') DEFAULT NULL,
  `meta_semanal` enum('perder_0.5kg','perder_1kg','mantener','ganar_0.5kg','ganar_1kg') DEFAULT NULL,
  `condiciones_medicas` text DEFAULT NULL,
  `medicamentos` text DEFAULT NULL,
  `alergias_alimentarias` text DEFAULT NULL,
  `preferencias_alimentarias` set('vegetariano','vegano','sin_gluten','sin_lactosa','bajo_carbohidratos','keto','paleo','mediterraneo') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `perfiles_usuario`
--

INSERT INTO `perfiles_usuario` (`id`, `usuario_id`, `altura_cm`, `peso_actual_kg`, `peso_objetivo_kg`, `nivel_actividad`, `objetivo_salud`, `meta_semanal`, `condiciones_medicas`, `medicamentos`, `alergias_alimentarias`, `preferencias_alimentarias`) VALUES
(3, 2, 1.58, 65.00, 58.00, 'ligero', 'perder_peso', 'perder_1kg', '', '', '', 'bajo_carbohidratos');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(10) UNSIGNED NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `paterno` varchar(100) NOT NULL,
  `materno` varchar(100) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `genero` enum('masculino','femenino') DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_spanish_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `email`, `password`, `nombre`, `paterno`, `materno`, `fecha_nacimiento`, `genero`, `telefono`) VALUES
(1, 'pixeles7u7@gmail.com', 'scrypt:32768:8:1$yzIfqInnu38woMPA$f5eb28fc6178b6cc917a7ccd87d6392cdf24a8fdc78ff0a624d09f2fbcc7b0e0f6c822147f96b798f9ff677aeaa1d2d2bd0880af76bf0399153920a3f290124f', 'miguel angel', 'bautista', 'Soriano', NULL, 'masculino', '6568267436'),
(2, 'andres.karlaa@gmail.com', 'scrypt:32768:8:1$2Xl6HBeMxgHK2Rq1$e73cdf27ded112ab6f164e0549c3917e1cc814be310ffc9bd0ab20e1375997cec5e38092807a1609b2d61a71a3fa8d478a761f97f258dcc329969e66ddd9b41c', 'karla Michelle', 'Andres', 'Cruz', '2008-05-08', '', '6568267436');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `perfiles_usuario`
--
ALTER TABLE `perfiles_usuario`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_usuario_perfil` (`usuario_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `perfiles_usuario`
--
ALTER TABLE `perfiles_usuario`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `perfiles_usuario`
--
ALTER TABLE `perfiles_usuario`
  ADD CONSTRAINT `fk_usuario_perfil` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
