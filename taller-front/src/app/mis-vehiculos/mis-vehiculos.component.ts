import { Component, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-mis-vehiculos',
  standalone: true,
  imports: [RouterModule, CommonModule],
  templateUrl: './mis-vehiculos.component.html',
  styleUrls: ['./mis-vehiculos.component.css']
})
export class MisVehiculosComponent {
  private http = inject(HttpClient);
  vehiculos: any[] = [];
  vehiculoSeleccionado: any = null; // Vehículo seleccionado para mostrar detalles

  constructor(private router: Router) {}

  ngOnInit() {
    const token = localStorage.getItem('token');

    if (!token) {
      console.log('No hay token disponible. Redirigiendo a login...');
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get('https://anthonyx82.ddns.net/taller/api/mis-vehiculos/', { headers }).subscribe({
      next: (data: any) => {
        this.vehiculos = data;
        this.cargarImagenesVehiculos();
      },
      error: (error) => console.log('Error al obtener vehículos:', error)
    });
  }

  cargarImagenesVehiculos(): void {
    this.vehiculos.forEach(vehiculo => {
      this.obtenerImagen(vehiculo.marca, vehiculo.modelo).then(imagenUrl => {
        vehiculo.imagenUrl = imagenUrl;
      });
    });
  }

  async obtenerImagen(marca: string, modelo: string): Promise<string> {
    const apiUrl = `https://anthonyx82.ddns.net/taller/api/car-imagery/?searchTerm=${encodeURIComponent(marca + ' ' + modelo)}`;
    try {
      const response = await this.http.get(apiUrl, { responseType: 'text' }).toPromise();
      const match = response?.match(/<string[^>]*>(.*?)<\/string>/);
      return match ? match[1] : 'assets/no-image.png';
    } catch (error) {
      console.log(`Error al obtener imagen de ${marca} ${modelo}:`, error);
      return 'assets/no-image.png';
    }
  }

  // Mostrar los detalles del vehículo seleccionado
  verDetalles(vehiculoId: number): void {
    const token = localStorage.getItem('token');
    if (!token) return;

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    // Obtener detalles del vehículo
    this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-vehiculos/${vehiculoId}`, { headers }).subscribe({
      next: (data: any) => {
        this.vehiculoSeleccionado = data;
        
        // Obtener los errores del vehículo
        this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-errores/${vehiculoId}`, { headers }).subscribe({
          next: (errores: any) => {
            this.vehiculoSeleccionado.errores = errores;
          },
          error: (error) => {
            console.log('Error al obtener errores del vehículo:', error);
            this.vehiculoSeleccionado.errores = [];
          }
        });
      },
      error: (error) => console.log('Error al obtener detalles del vehículo:', error)
    });
  }

  solicitarInforme(vehiculoId: number) {
    const email = prompt("Introduce el email del cliente:");
    if (!email) return;
  
    this.http.post<{ enlace: string }>(`https://anthonyx82.ddns.net/taller/api/crear-informe/${vehiculoId}`, { email }).subscribe(res => {
      alert("Informe generado y enviado por correo. También puedes copiar este enlace: " + res.enlace);
      navigator.clipboard.writeText(res.enlace);
    });
  }

  cerrarDetalles(): void {
    this.vehiculoSeleccionado = null;
  }

  editarVehiculo(vehiculoId: number): void {
    this.router.navigate([`/editar-vehiculo/${vehiculoId}`]);
  }

  eliminarVehiculo(vehiculoId: number): void {
    const token = localStorage.getItem('token');
    if (!token) return;

    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`https://anthonyx82.ddns.net/taller/api/eliminar-vehiculo/${vehiculoId}`, { headers }).subscribe({
      next: () => {
        this.vehiculos = this.vehiculos.filter(v => v.id !== vehiculoId);
        console.log('Vehículo eliminado');
      },
      error: (error) => console.log('Error al eliminar vehículo:', error)
    });
  }

  volverInicio(): void {
    this.router.navigate(['/']);
  }
}
