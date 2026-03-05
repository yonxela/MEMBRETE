// SISDEL DATACENTER — Configuración Central de Supabase
// Este archivo centraliza la conexión para que todo el sistema esté sincronizado.

const SUPABASE_URL = 'https://rxrodfskmvldozpznyrp.supabase.co';
const SUPABASE_KEY = 'sb_publishable_rm-U3aeXydu4W0wdSMLW5w_I4LIW5MO';

// Inicialización del cliente Supabase
const { createClient } = window.supabase;
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

console.log('✅ SISDEL DATACENTER: Conexión con Supabase establecida.');

/**
 * Función para verificar sesión activa en todas las páginas.
 * Ahora usa una ruta absoluta para asegurar que la redirección a index.html funcione
 * desde cualquier subdirectorio (como modulos_ocultos).
 */
function checkSession() {
    const session = sessionStorage.getItem('sisdel_session');

    // Si no hay sesión y no estamos en la página de inicio, redirigir
    // Usamos una lógica más robusta para detectar la página de inicio
    const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');

    if (!session && !isLoginPage) {
        // Redirigir a la raíz (index.html)
        // Si estamos en un subdirectorio, necesitamos subir un nivel
        const prefix = window.location.pathname.includes('/modulos_ocultos/') ? '../' : './';
        window.location.href = prefix + 'index.html';
    }
    return session ? JSON.parse(session) : null;
}

/**
 * Función para cerrar sesión de forma segura
 */
function logout() {
    sessionStorage.removeItem('sisdel_session');
    const prefix = window.location.pathname.includes('/modulos_ocultos/') ? '../' : './';
    window.location.href = prefix + 'index.html';
}
