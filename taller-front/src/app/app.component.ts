import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

/**
 * ![home](../assets/docs/screenshots/home.png)
 * <br>
 * Componente raíz principal de la aplicación Angular.
 * 
 * Este componente actúa como la entrada principal de la SPA (Single Page Application) y controla la
 * navegación y visualización condicional de elementos en función del estado de autenticación del usuario.
 * 
 * Presenta una página de bienvenida con la descripción de la API automotriz cuando el usuario está en la página principal,
 * mostrando botones para registrarse o iniciar sesión si no está autenticado, o bien opciones para acceder a
 * la gestión de vehículos y cerrar sesión si está autenticado.
 * 
 * También incluye secciones informativas sobre las características principales de la API, beneficios y
 * testimonios de clientes, todo dentro de un diseño moderno y accesible.
 */
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  /**
   * Título principal que representa el nombre de la aplicación.
   * Se muestra en la cabecera de la página principal.
   */
  title = 'Api Automotriz';

  /**
   * Descripción informativa que explica el propósito y ventajas de la API.
   * Se muestra en la página principal justo debajo del título.
   */
  description = 'Bienvenido a la primera API para taller. Gestionamos la información de tus vehículos en tiempo real y te ofrecemos un servicio rápido y eficiente con tecnología avanzada.';

  /**
   * Constructor del componente.
   * 
   * @param http Cliente HTTP para realizar llamadas al backend (no utilizado directamente aquí, pero inyectado para posibles futuras funciones).
   * @param router Servicio para gestionar la navegación y obtener la URL actual.
   */
  constructor(private http: HttpClient, private router: Router) { }

  /**
   * Determina si la URL actual es la página principal.
   * 
   * @returns `true` si la ruta actual es exactamente `'/'`, lo que indica que el usuario está en la landing page.
   *          `false` en caso contrario.
   */
  esPaginaPrincipal(): boolean {
    return this.router.url === '/';
  }

  /**
   * Comprueba si el usuario está autenticado.
   * 
   * Evalúa la presencia de un token de sesión almacenado en `localStorage`.
   * 
   * @returns `true` si existe un token válido indicando sesión activa, `false` si no hay token.
   */
  usuarioAutenticado(): boolean {
    return !!localStorage.getItem('token');
  }

  /**
   * Cierra la sesión del usuario.
   * 
   * Elimina el token de autenticación almacenado localmente y redirige a la página principal.
   */
  cerrarSesion(): void {
    localStorage.removeItem('token');
    this.router.navigate(['/']);
  }
}
