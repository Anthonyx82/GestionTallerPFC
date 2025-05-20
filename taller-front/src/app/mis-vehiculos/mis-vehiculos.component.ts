import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
  vehiculoSeleccionado: any = null;

  constructor(private router: Router) {}

  ngOnInit() {
    this.http.get('https://anthonyx82.ddns.net/taller/api/mis-vehiculos/').subscribe({
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

  verDetalles(vehiculoId: number): void {
    this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-vehiculos/${vehiculoId}`).subscribe({
      next: (data: any) => {
        this.vehiculoSeleccionado = data;

        this.http.get(`https://anthonyx82.ddns.net/taller/api/mis-errores/${vehiculoId}`).subscribe({
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

    this.http.post<{ enlace: string }>(
      `https://anthonyx82.ddns.net/taller/api/crear-informe/${vehiculoId}`,
      { email: email },
      { headers: { 'Content-Type': 'application/json' } }
    ).subscribe(res => {
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
    this.http.delete(`https://anthonyx82.ddns.net/taller/api/eliminar-vehiculo/${vehiculoId}`).subscribe({
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
