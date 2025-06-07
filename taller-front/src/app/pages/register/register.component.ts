import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ErrorMessageComponent } from '../../shared/error-message/error-message.component';

/**
 * ![registro](../assets/docs/screenshots/registro.png)
 * <br>
 * Componente para el registro de nuevos usuarios en la aplicación.
 * 
 * Proporciona un formulario reactivo que permite a los usuarios crear una cuenta ingresando un nombre de usuario y una contraseña.
 * Valida la entrada localmente asegurando que el nombre de usuario tenga al menos 3 caracteres y la contraseña al menos 6 caracteres.
 * 
 * Al enviar un formulario válido, realiza una petición HTTP POST a la API para registrar al usuario. 
 * Maneja la respuesta mostrando mensajes de error específicos en caso de fallo o navegando a la página principal tras un registro exitoso.
 * 
 * Integra un componente compartido para mostrar mensajes de error personalizados en la interfaz.
 */
@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ErrorMessageComponent],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  /**
   * Cliente HTTP para realizar peticiones al backend.
   */
  private http = inject(HttpClient);

  /**
   * Constructor de formularios reactivos para crear y gestionar el formulario de registro.
   */
  private fb = inject(FormBuilder);

  /**
   * Servicio de navegación para redirigir al usuario tras el registro exitoso.
   */
  private router = inject(Router);

  /**
   * Mensaje de error que se muestra cuando ocurre un fallo durante el registro o la validación.
   */
  errorMessage: string = '';

  /**
   * Formulario reactivo que contiene los campos de nombre de usuario y contraseña.
   * 
   * Validaciones aplicadas:
   * - username: requerido, mínimo 3 caracteres.
   * - password: requerido, mínimo 6 caracteres.
   */
  registerForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  /**
   * Envía los datos del formulario para registrar un nuevo usuario.
   * 
   * Si el formulario es válido, realiza una petición POST a la API de registro.
   * En caso de éxito, redirige al usuario a la página principal.
   * En caso de error, muestra un mensaje específico basado en la respuesta del servidor o un mensaje genérico.
   * Si el formulario no es válido, se asigna un mensaje de error indicando que debe completarse correctamente.
   */
  register() {
    if (this.registerForm.valid) {
      this.http.post('https://anthonyx82.ddns.net/taller/api/register', this.registerForm.value).subscribe({
        next: () => this.router.navigate(['/']),
        error: (error) => {
          this.errorMessage = error.error.detail || 'Error desconocido en el registro.';
        }
      });
    } else {
      this.errorMessage = 'Por favor, completa el formulario correctamente.';
    }
  }
}