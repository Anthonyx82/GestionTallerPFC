import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-editar-vehiculo',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './editar-vehiculo.component.html',
  styleUrls: ['./editar-vehiculo.component.css']
})
export class EditarVehiculoComponent implements OnInit {
  vehiculoId!: number;
  vehiculo: any = {
    marca: '',
    modelo: '',
    year: null,
    vin: '',
    rpm: null,
    velocidad: null
  };

  tokenValido = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.tokenValido = true;

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.vehiculoId = +id;
      this.cargarVehiculo();
    } else {
      console.error('ID del vehículo no encontrado');
    }
  }

  cargarVehiculo(): void {
    this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-vehiculos/${this.vehiculoId}`).subscribe({
      next: (data: any) => {
        this.vehiculo = data;
      },
      error: (error) => {
        console.error('Error al cargar el vehículo:', error);
      }
    });
  }

  guardarEdicion(): void {
    const vehiculoActualizado = {
      marca: this.vehiculo.marca,
      modelo: this.vehiculo.modelo,
      year: this.vehiculo.year,
      vin: this.vehiculo.vin,
      rpm: this.vehiculo.rpm,
      velocidad: this.vehiculo.velocidad
    };

    this.http.put(`https://anthonyx82.ddns.net/taller/api/editar-vehiculo/${this.vehiculoId}`, vehiculoActualizado).subscribe({
      next: () => {
        console.log('Vehículo actualizado correctamente');
        this.router.navigate(['/mis-vehiculos']);
      },
      error: (error) => {
        console.error('Error al actualizar vehículo:', error);
      }
    });
  }

  volver(): void {
    this.router.navigate(['/mis-vehiculos']);
  }
}
