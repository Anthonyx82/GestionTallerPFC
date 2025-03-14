import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  registerForm: FormGroup = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  register() {
    if (this.registerForm.valid) {
      this.http.post('https://anthonyx82.ddns.net/taller/api/register', this.registerForm.value).subscribe({
        next: () => alert('Usuario registrado correctamente'),
        error: (error) => alert(`Error en el registro: ${error.error.detail || 'Desconocido'}`)
      });
    } else {
      alert('Por favor, complete el formulario correctamente.');
    }
  }
}