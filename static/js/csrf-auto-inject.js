/**
 * DT-19: Auto-inyector de CSRF token.
 * 
 * 1. Inyecta <input type="hidden" name="csrf_token"> en formularios POST.
 * 2. Envuelve window.fetch para agregar el header X-CSRFToken en 
 *    peticiones POST/PUT/DELETE/PATCH.
 * 
 * Uso: incluir este script en el <head> de cada template junto con
 * el meta tag. Ver templates/_csrf_head.html.
 */
(function() {
    'use strict';

    // === Funciones auxiliares ===

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : null;
    }

    // === 1. Auto-inyección en formularios ===

    function injectTokenIntoForm(form) {
        if (!form || form.method.toLowerCase() !== 'post') return;
        
        if (form.querySelector('input[name="csrf_token"]')) return;
        
        const token = getCsrfToken();
        if (!token) {
            console.warn('[CSRF] No se encontro meta[name=csrf-token]. El formulario puede fallar.');
            return;
        }
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrf_token';
        input.value = token;
        form.appendChild(input);
    }

    function injectIntoAllForms() {
        document.querySelectorAll('form').forEach(injectTokenIntoForm);
    }

    // === 2. Wrapper de fetch ===

    const _originalFetch = window.fetch;

    window.fetch = function(url, options) {
        options = options || {};
        
        const method = (options.method || 'GET').toUpperCase();
        const protectedMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];
        
        if (protectedMethods.includes(method)) {
            const token = getCsrfToken();
            if (token) {
                // Preservar headers existentes
                options.headers = options.headers || {};
                
                // Manejar Headers, Array, o Object
                if (options.headers instanceof Headers) {
                    if (!options.headers.has('X-CSRFToken')) {
                        options.headers.set('X-CSRFToken', token);
                    }
                } else if (Array.isArray(options.headers)) {
                    // Convertir array a objeto para simplificar
                    const h = {};
                    options.headers.forEach(([k, v]) => { h[k] = v; });
                    if (!Object.keys(h).some(k => k.toLowerCase() === 'x-csrftoken')) {
                        h['X-CSRFToken'] = token;
                    }
                    options.headers = h;
                } else {
                    const keys = Object.keys(options.headers);
                    if (!keys.some(k => k.toLowerCase() === 'x-csrftoken')) {
                        options.headers['X-CSRFToken'] = token;
                    }
                }
            } else {
                console.warn('[CSRF] fetch ' + method + ' sin token CSRF:', url);
            }
        }
        
        return _originalFetch.call(this, url, options);
    };

    // === Ejecutar al cargar el DOM ===

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectIntoAllForms);
    } else {
        injectIntoAllForms();
    }

    // Exponer funciones globales
    window.injectCsrfToken = injectTokenIntoForm;
    window.injectCsrfTokenAll = injectIntoAllForms;
    window.getCsrfToken = getCsrfToken;
})();