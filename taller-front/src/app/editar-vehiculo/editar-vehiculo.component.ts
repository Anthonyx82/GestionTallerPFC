import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

/** 
 * ![editar-vehiculo](assets/docs/screenshots/editar-vehiculo.png)
 * <br>
 * Componente para editar los datos de un vehículo existente.
 *
 * Permite modificar la marca, modelo, año, VIN, RPM, velocidad y revisión.
 * Valida la existencia de un token para acceso seguro.
 * Carga los datos actuales del vehículo desde la API y los guarda tras edición.
 */
@Component({
  selector: 'app-editar-vehiculo',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './editar-vehiculo.component.html',
  styleUrls: ['./editar-vehiculo.component.css']
})
export class EditarVehiculoComponent implements OnInit {

  /** 
   * ID del vehículo a editar, obtenido desde los parámetros de la ruta.
   */
  vehiculoId!: number;

  /** 
   * Objeto que almacena los datos del vehículo que se van a editar.
   */
  vehiculo: {
    marca: string;
    modelo: string;
    year: number | null;
    vin: string;
    rpm: number | null;
    velocidad: number | null;
    revision?: string;
  } = {
    marca: '',
    modelo: '',
    year: null,
    vin: '',
    rpm: null,
    velocidad: null
  };

  /** 
   * Indica si el token de autenticación existe y es considerado válido.
   */
  tokenValido = false;

  /**
   * Inyección de dependencias del enrutador, rutas activas y cliente HTTP.
   * @param route - Proporciona acceso a los parámetros de la ruta activa.
   * @param router - Permite la navegación entre rutas.
   * @param http - Cliente HTTP para realizar peticiones a la API.
   */
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient
  ) { }

  /**
   * Hook del ciclo de vida que se ejecuta al inicializar el componente.
   * Verifica si hay un token válido y, si existe un ID, carga los datos del vehículo.
   */
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

  /**
   * Carga los datos del vehículo desde la API usando el ID actual.
   * Realiza una petición HTTP GET al backend.
   */
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

  /**
   * Guarda los cambios realizados al vehículo actual.
   * Realiza una petición HTTP PUT con los nuevos datos al backend.
   */
  guardarEdicion(): void {
    const vehiculoActualizado = {
      marca: this.vehiculo.marca,
      modelo: this.vehiculo.modelo,
      year: this.vehiculo.year,
      vin: this.vehiculo.vin,
      rpm: this.vehiculo.rpm,
      velocidad: this.vehiculo.velocidad,
      revision: this.vehiculo.revision
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

  /**
   * Redirige al usuario a la vista de listado de vehículos sin realizar cambios.
   */
  volver(): void {
    this.router.navigate(['/mis-vehiculos']);
  }
}
