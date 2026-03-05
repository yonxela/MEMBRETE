# Documentación Técnica - Sistema de Control Residencial SISDEL

## 1. Visión General del Proyecto
**SISDEL** (también referido en código fuente como DELCO/GaritaApp/Membrete) es una aplicación web de control de accesos y administración para condominios. Su función principal es agilizar la entrada en la garita de seguridad mediante códigos y escaneo QR, al mismo tiempo que permite a la Junta Directiva (administradores) gestionar el estado de los residentes, pagos, visitas y comunicación.

El sistema fue diseñado con una arquitectura **Multi-Tenant (Multi-Condominio)**, lo que permite que desde un mismo dominio de alojamiento (ej. GitHub Pages) se puedan gestionar y aislar las bases de datos de múltiples proyectos o condominios residenciales distintos a través de un "Control Maestro".

## 2. Pila Tecnológica (Tech Stack)
- **Frontend Core:** HTML5, CSS3 (Vanilla, Glassmorphism UI), JavaScript (ES6+ Vanilla).
- **Almacenamiento Local (Caché/Offline):** `window.localStorage` (utilizado para cargas rápidas de UI y mantener estado de sesión).
- **Backend / Base de Datos Nube (BaaS):** [Supabase](https://supabase.com/) (PostgreSQL auto-generado, API REST para clientes via `@supabase/supabase-js`).
- **Librerías Externas:** 
  - API generadora de Códigos QR (`api.qrserver.com`).
  - Google Fonts (Outfit, Roboto).
  - Supabase JS Client v2 (CDN).
- **Hospedaje (Hosting):** GitHub Pages (actualmente alojado en rama `main` del repositorio).

---

## 3. Arquitectura del Sistema

La aplicación utiliza un enfoque híbrido **"Local-First" con Sincronización a la Nube**:
1. El código JavaScript lee *por defecto* de arreglos almacenados en memoria local (`localStorage`), lo que garantiza que la página jamás tenga tiempos de carga lentos y pueda funcionar si hay micro-cortes de internet.
2. Sin embargo, para permitir la administración o acceso **Multi-dispositivo**, el sistema realiza consultas asíncronas asertivas (`async/await`) contra **Supabase** (la fuente real de la verdad) en momentos críticos:
   - Al crear un proyecto.
   - Al abrir el panel maestro.
   - Al escanear el marbete de un residente (si no se halla en local, brinca a Supabase).
   - "Al Conectar" a un condominio específico (Descarga toda la tabla de la nube).

### 3.1 Control Maestro multi-proyecto
Hay una constante global lógica llamada **SISDEL 2026** (Clave Maestra). Al ingresarla en el panel de administrador, levanta el "Control Maestro", que lee la tabla global de proyectos y permite saltar de una base de datos a otra borrando la memoria caché activa y cargando los datos del condominio seleccionado.

---

## 4. Estructura Principal de Archivos

- `/index.html`: La cara pública para residentes y visitas. Incluye el teclado numérico de acceso rápido en garita, lógica de validación universal (búsqueda local y en Supabase mediante la tabla `vecinos_universal`) y alertas de denegación/aprobación.
- `/login.html`: Portal estandarizado para iniciar sesión dirigido a seguridad (Rol 3) o Directiva/Admin (Rol 1). Valida las credenciales contra la variable `delco_usuarios`.
- `/marbete.html`: La tarjeta digital (ID) del residente. Genera dinámicamente el código QR validando si hay mora o bloqueos, jalando los datos de Supabase si es necesario, mostrando mensajes que la directiva dejó para el residente en cuestión.
- `/modulos_ocultos/admin.html`: Es el panel principal de control (SPA - Single Page Application). Maneja:
  - Creación y edición de vecinos.
  - Sincronización 1 a 1 de usuarios hacia Supabase.
  - Panel Maestro (para cambiar de condominio).
  - Envío de notificaciones al tablero de avisos del Marbete.
  - Visualización del historial de visitas y control de estado (solvente, mora, etc).
- `/supabase-config.js`: Contiene la llave pública (anon key) y la URL del proyecto en Supabase para instanciar la variable principal de conexión a Base de Datos (nombrada como `supabaseDb`).

---

## 5. Modelado de Datos

El sistema convive en dos ambientes estructurales distintos, el almacenamiento Local Browser y el almacenamiento en Supabase.

### 5.1 Base de Datos - Supabase (PostgreSQL)

**Tabla 1: `condominios`**
Utilizada para guardar todos los proyectos/clientes activos de la plataforma.
- `id` (uuid, gen_random_uuid)
- `created_at` (timestamp)
- `nombre` (text) - Nombre general del proyecto (Ej: VILLA FERRER).
- `encargado` (text) - Nombre del administrador.
- `correo` (text)
- `tel` (text)
- `codigo_acceso` (text) - Credencial master de ese proyecto.
- `activo` (boolean)

**Tabla 2: `vecinos_universal`**
Tabla centralizada donde conviven absolutamente todos los residentes de todos los proyectos al unísono, diferenciados por la columna `condo_nombre`.
- `id` (int8) - Timestamp local para ID relacional rápido.
- `created_at` (timestamp)
- `condo_nombre` (text) - Llave de fragmentación. (Ej: VILLA FERRER).
- `nombre` (text)
- `lote` (text) - Número de casa / Domicilio.
- `codigo` (text) - PIN numérico o alfanumérico para entrada rápido. Actúa a veces como Password.
- `rol` (int4) - Niveles: 1 (Admin), 2 (Vecino Solvente), 3 (Garita), 4 (Inquilino/Temporal).
- `status` (int4) - 0 (Bloqueado/Mora Crítica), 1 (Solvente/Adelantado), 2 (Mora leve activa).
- `telefono` (text)
- `placas` (text) - Control vehicular.
- `dias_demora` (int4)

### 5.2 Estructura del LocalStorage (Caché por Cliente)

Cuando un proyecto (X) está Activo en una computadora, su LocalStorage mapea estas variables:
- `delco_config`: JSON de ajustes (nombre, teléfonos de la garita, etc).
- `delco_vecinos`: Array JSON descargado de `vecinos_universal`.
- `delco_usuarios`: Cuentas habilitadas para hacer login y entrar al admin/garita (basado en los vecinos con rol de directiva/seguridad).
- `delco_visitas`: Historial de entrada y salida local.
- `delco_mensajes`: Tabla cruzada para bandeja de entrada al visitar el marbete.
- `SISDEL_DB_[NOMBRE_CONDOMINIO]`: Un JSON gigantesco tipo *backup* que engloba todas  las variables `delco_*` cuando el administrador salta de un proyecto a otro. Sirve para no perder configuración local offline de condominios paralelos.
- `SISDEL_LISTADO_MASTER`: Lista caché mapeada desde la tabla maestra de condominios.

---

## 6. Flujos de Lógica Críticos (Importante a Considerar)

### 6.1 "Conectar" / Switching de Proyectos en Panel (Multi-Tenant)
La función `ejecutarCambioProyecto()` (dentro de `admin.html`) es responsable de la magia multi-cliente:
1. Mete toda la sesión actual (variables delco) del condominio A en un cubo `SISDEL_DB_A`.
2. Actualiza `delco_config` a los ajustes básicos del condominio B.
3. Ejecuta un "FETCH" asíncrono hacia la tabla `vecinos_universal` en Supabase buscando la llave foránea virtual `condo_nombre = B`.
4. Si encuentra vecinos en la nube, regenera toda la lista en caché `delco_vecinos` y construye perfiles de usuario y passwords (`delco_usuarios`) al vuelo. Redibuja la matriz.

### 6.2 Escáner Multi-Condominio Universitario
La función `buscarCodigoEnTodos()` de `index.html` es el orquestador principal.
Si el usuario pone el PIN en su computadora:
1. Buscará a nivel de memoria RAM / LocalStorage de inmediato. Funciona rápido.
2. Si un Administrador hizo una recarga remota en su celular y el PIN no está en el esqueleto local aún, se llamará a `supabaseDb.from(...).maybeSingle()`.
3. Al dar el OK, inyecta su perfil y evalúa según rol y estatus el desvío hacia el marbete verde, bloqueo rojo o autorización condicional.

### 6.3 Inicialización / Prevención de Conflictos Supabase
El cliente CDN genera globalmente el objeto `window.supabase`. Para evitar sobreescritura, conflicto de scopes, o *Shadowing*, el archivo conctor `/supabase-config.js` expone de forma estricta la conexión con el nombre lógico global `window.supabaseDb`. Todo el DOM interactuará a través de `supabaseDb`.

---

## 7. Instrucciones Prácticas para Continuar/Rehacer

1. **Mantener RLS Apagado en Supabase al Re-programar:** 
   El sistema actualmente asume que la Key entregada en el JS config tiene plenos permisos (`anon/public`). Si otro programador crea un backend nuevo, deberá usar políticas tipo *Allow ALL* para el rol público anon mientras transiciona al motor. Si prefiere cerrar la base, tendrá que incrustar validaciones con JWT desde Supabase Auth.
   
2. **Re-crear Tablas en Supabase:**
   Si se instala en una organización nueva de supabase, basta con ejecutar el código SQL dentro del *SQL Editor* con los campos exactos documentados en la Sección 5.1. El tipo de base de datos nunca requiere migración estructurada severa porque el Front-End reconstruye todo.

3. **Inyección de IDs:**
   Nótese que el ID interno de los vecinos (`id`) es una estampa de tiempo computacional (`Date.now()`), no confíen en el auto-incrementador de SQL, ya que el Offline-First rompe secuencias serializadas fácilmente, este ID se utiliza para emparejar registros en las pasarelas sin colisiones.
