import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common'; // Necesario para usar ngModel y otros módulos de Angular
import { FormsModule } from '@angular/forms'; // Necesario para el uso de ngModel

@Component({
  selector: 'app-editar-vehiculo',
  standalone: true,
  imports: [CommonModule, FormsModule], // Importa CommonModule y FormsModule para el binding de formularios
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

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    // Obtener el ID del vehículo desde la URL
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.vehiculoId = +id;
    } else {
      // Manejar el caso donde no se encuentra el ID
      console.error('ID del vehículo no encontrado');
    }

    this.cargarVehiculo();
  }

  cargarVehiculo(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No hay token disponible');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-vehiculos/${this.vehiculoId}`, { headers }).subscribe({
      next: (data: any) => {
        this.vehiculo = data;
      },
      error: (error) => {
        console.error('Error al cargar el vehículo:', error);
      }
    });
  }

  guardarEdicion(): void {
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('No hay token disponible');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const vehiculoActualizado = {
      marca: this.vehiculo.marca,
      modelo: this.vehiculo.modelo,
      year: this.vehiculo.year,
      vin: this.vehiculo.vin,
      rpm: this.vehiculo.rpm,
      velocidad: this.vehiculo.velocidad
    };

    this.http.put(`https://anthonyx82.ddns.net/taller/api/editar-vehiculo/${this.vehiculoId}`, vehiculoActualizado, { headers }).subscribe({
      next: () => {
        console.log('Vehículo actualizado correctamente');
        this.router.navigate(['/mis-vehiculos']); // Redirigir a la lista de vehículos
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
