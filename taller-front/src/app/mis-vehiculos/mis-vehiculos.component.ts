import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';

/**
 * ![mis-vehiculos](../assets/docs/screenshots/mis-vehiculos.png)
 * <br>
 * Componente para mostrar y gestionar los vehículos del usuario.
 * 
 * Permite visualizar la lista de vehículos del usuario, mostrando imagen y detalles.
 * Permite seleccionar un vehículo para ver más detalles y errores asociados.
 * Incluye funcionalidad para editar, eliminar vehículos y solicitar informes vía email.
 * 
 * Gestiona el estado de carga de imágenes y muestra mensajes de éxito o error según las operaciones.
 */
@Component({
  selector: 'app-mis-vehiculos',
  standalone: true,
  imports: [RouterModule, CommonModule, MatIconModule, MatButtonModule, FormsModule],
  templateUrl: './mis-vehiculos.component.html',
  styleUrls: ['./mis-vehiculos.component.css']
})
export class MisVehiculosComponent {
  /**
  * Cliente HTTP de Angular para realizar peticiones al backend.
  */
  private http = inject(HttpClient);

  /**
   * Lista de vehículos del usuario.
   */
  vehiculos: any[] = [];

  /**
   * Vehículo seleccionado para mostrar detalles.
   */
  vehiculoSeleccionado: any = null;

  /**
   * Indica si los datos están cargándose.
   */
  cargando: boolean = true;

  /**
  * Contador de imágenes cargadas para sincronizar la carga.
  */
  imagenesCargadas: number = 0;

  /**
   * Email del cliente para solicitar informes.
   */
  emailCliente: string = '';

  /**
   * Mensaje que se muestra al usuario (éxito o error).
   */
  mensaje: string = '';

  /**
   * Tipo de mensaje mostrado ('error' o 'exito').
   */
  tipoMensaje: 'error' | 'exito' = 'exito';

  /**
  * Inyecta el servicio de navegación `Router` para redirigir entre vistas.
  * @param router Servicio de enrutamiento de Angular
  */
  constructor(private router: Router) { }

  /**
   * Inicializa la carga de vehículos al montar el componente.
   * Obtiene los vehículos del backend y comienza la carga de sus imágenes.
   */
  ngOnInit() {
    this.http.get('https://anthonyx82.ddns.net/taller/api/mis-vehiculos/').subscribe({
      next: (data: any) => {
        this.vehiculos = data.vehiculos ?? [];
        if (this.vehiculos.length === 0) {
          this.cargando = false;
        } else {
          this.cargarImagenesVehiculos();
        }
      },
      error: (error) => {
        console.log('Error al obtener vehículos:', error);
        this.cargando = false;
      }
    });
  }


  /**
   * Muestra un mensaje temporal de éxito o error.
   * @param mensaje Texto a mostrar
   * @param tipo Tipo de mensaje ('error' o 'exito'), por defecto 'exito'
   */
  mostrarMensaje(mensaje: string, tipo: 'error' | 'exito' = 'exito') {
    this.mensaje = mensaje;
    this.tipoMensaje = tipo;
    setTimeout(() => this.mensaje = '', 5000);
  }


  /**
   * Carga las imágenes de todos los vehículos solicitándolas al backend.
   * Actualiza la propiedad `imagenUrl` de cada vehículo.
   * Marca `cargando` como false cuando todas las imágenes se han cargado.
   */
  cargarImagenesVehiculos(): void {
    this.imagenesCargadas = 0;

    this.vehiculos.forEach((vehiculo, index) => {
      this.obtenerImagen(vehiculo.marca, vehiculo.modelo).then(imagenUrl => {
        vehiculo.imagenUrl = imagenUrl;
        this.imagenesCargadas++;

        if (this.imagenesCargadas === this.vehiculos.length) {
          this.cargando = false;
        }
      });
    });
  }

  /**
   * Obtiene la URL de la imagen para un vehículo dado marca y modelo.
   * Si falla, retorna una imagen por defecto.
   * @param marca Marca del vehículo
   * @param modelo Modelo del vehículo
   * @returns Promise con la URL de la imagen
   */
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

  /**
   * Solicita y muestra los detalles de un vehículo, incluyendo sus errores asociados.
   * @param vehiculoId Identificador del vehículo
   */
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

  /**
   * Envía una solicitud para generar un informe del vehículo y enviarlo al email proporcionado.
   * Valida el formato del email antes de enviar.
   * Copia el enlace del informe al portapapeles tras éxito.
   * @param vehiculoId Identificador del vehículo
   */
  solicitarInformeConEmail(vehiculoId: number) {
    if (!this.emailCliente || !this.emailCliente.includes('@')) {
      this.mostrarMensaje('Por favor, introduce un email válido.', 'error');
      return;
    }

    this.http.post<{ enlace: string }>(
      `https://anthonyx82.ddns.net/taller/api/crear-informe/${vehiculoId}`,
      { email: this.emailCliente },
      { headers: { 'Content-Type': 'application/json' } }
    ).subscribe({
      next: (res) => {
        this.mostrarMensaje('Informe generado y enviado por correo.');
        navigator.clipboard.writeText(res.enlace);
        this.emailCliente = '';
      },
      error: () => {
        this.mostrarMensaje('Error al generar el informe.', 'error');
      }
    });
  }

  /**
   * Cierra la vista de detalles del vehículo seleccionado.
   */
  cerrarDetalles(): void {
    this.vehiculoSeleccionado = null;
  }

  /**
   * Navega a la ruta para editar el vehículo indicado.
   * @param vehiculoId Identificador del vehículo
   */
  editarVehiculo(vehiculoId: number): void {
    this.router.navigate([`/editar-vehiculo/${vehiculoId}`]);
  }

  /**
   * Elimina un vehículo del backend y actualiza la lista local.
   * @param vehiculoId Identificador del vehículo a eliminar
   */
  eliminarVehiculo(vehiculoId: number): void {
    this.http.delete(`https://anthonyx82.ddns.net/taller/api/eliminar-vehiculo/${vehiculoId}`).subscribe({
      next: () => {
        this.vehiculos = this.vehiculos.filter(v => v.id !== vehiculoId);
        console.log('Vehículo eliminado');
      },
      error: (error) => console.log('Error al eliminar vehículo:', error)
    });
  }

  /**
   * Navega a la página principal.
   */
  volverInicio(): void {
    this.router.navigate(['/']);
  }
}
