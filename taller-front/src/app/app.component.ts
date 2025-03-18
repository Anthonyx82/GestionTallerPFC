import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Api Automotriz';
  description = 'Bienvenido a la primera API para taller. Gestionamos la información de tus vehículos en tiempo real y te ofrecemos un servicio rápido y eficiente con tecnología avanzada.';

  constructor(private http: HttpClient, private router: Router) { }

  esPaginaPrincipal(): boolean {
    return this.router.url === '/';
  }

  usuarioAutenticado(): boolean {
    return !!localStorage.getItem('token');
  }

  cerrarSesion(): void {
    localStorage.removeItem('token');
    this.router.navigate(['/']);
  }
}
