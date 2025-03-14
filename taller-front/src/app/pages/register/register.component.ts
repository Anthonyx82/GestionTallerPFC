import { Component, inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,  // <-- IMPORTANTE: declarar standalone
  imports: [CommonModule, ReactiveFormsModule], // <-- IMPORTAR ReactiveFormsModule
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  private http = inject(HttpClient);
  private fb = inject(FormBuilder);

  registerForm: FormGroup = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required]
  });

  register() {
    if (this.registerForm.valid) {
      this.http.post('https://anthonyx82.ddns.net/taller/api/register', this.registerForm.value).subscribe({
        next: () => alert('Usuario registrado correctamente'),
        error: () => alert('Error en el registro')
      });
    }
  }
}
