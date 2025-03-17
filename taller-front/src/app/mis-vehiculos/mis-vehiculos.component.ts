import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
    this.http.get('https://anthonyx82.ddns.net/taller/api/mis-vehiculos/').subscribe({
    next: (data: any) => this.vehiculos = data,
    error: (error) => console.log('Error al obtener vehículos:', error)
  });

  }
}
