import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ErrorMessageComponent } from '../../shared/error-message/error-message.component';

/**
 * ![login](../assets/docs/screenshots/login.png)
 * <br>
 * Componente para el inicio de sesión de usuarios.
 * 
 * Permite a los usuarios ingresar sus credenciales para autenticarse en la aplicación.
 * Proporciona un formulario simple con campos para nombre de usuario y contraseña.
 * 
 * Al enviar el formulario, se realiza una petición HTTP POST a la API para validar las credenciales.
 * Si la autenticación es exitosa, guarda el token de acceso en localStorage y redirige al usuario a la página principal.
 * En caso de error, muestra un mensaje indicando que las credenciales son incorrectas.
 */
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, ErrorMessageComponent],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  /**
   * Nombre de usuario introducido en el formulario.
   */
  username: string = '';

  /**
   * Contraseña introducida en el formulario.
   */
  password: string = '';

  /**
   * Mensaje de error que se muestra cuando las credenciales son incorrectas.
   */
  errorMessage: string = '';

  /**
  * Constructor del componente.
  * Inyecta los servicios HttpClient para hacer peticiones HTTP
  * y Router para navegación dentro de la aplicación.
  */
  constructor(private http: HttpClient, private router: Router) { }

  /**
   * Método que realiza la petición de inicio de sesión.
   * Envía el nombre de usuario y la contraseña al backend para autenticación.
   * 
   * En caso de éxito:
   * - Guarda el token de acceso recibido en localStorage.
   * - Redirige al usuario a la página principal.
   * 
   * En caso de fallo:
   * - Muestra un mensaje de error indicando que las credenciales son incorrectas.
   */
  login() {
    this.http.post<{ access_token: string }>('https://anthonyx82.ddns.net/taller/api/login', {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (response) => {
        localStorage.setItem('token', response.access_token);
        this.router.navigate(['/']);
      },
      error: () => {
        this.errorMessage = 'Credenciales incorrectas';
      }
    });
  }
}