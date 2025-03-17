import { Component, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-mis-vehiculos',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './mis-vehiculos.component.html',
  styleUrls: ['./mis-vehiculos.component.css']
})
export class MisVehiculosComponent {
  private http = inject(HttpClient);
  vehiculos: any[] = [];

  ngOnInit() {
    const token = localStorage.getItem('token'); // 🔹 Obtener el token del almacenamiento

    if (!token) {
      console.log('No hay token disponible. Redirigiendo a login...');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get('https://anthonyx82.ddns.net/taller/api/mis-vehiculos/', { headers }).subscribe({
      next: (data: any) => this.vehiculos = data,
      error: (error) => console.log('Error al obtener vehículos:', error)
    });
  }
}
