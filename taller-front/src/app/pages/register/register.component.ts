import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ErrorMessageComponent } from '../../shared/error-message/error-message.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, ErrorMessageComponent],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);
  private router = inject(Router);

  errorMessage: string = '';

  registerForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

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
