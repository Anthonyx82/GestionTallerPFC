import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http'; // Importa HttpClient

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [],  // Ya no es necesario importar HttpClientModule aquí
  templateUrl: './app.component.html',
})
export class AppComponent {
  title = 'taller-front';

  constructor(private http: HttpClient) {} // Inyectar HttpClient

  // Método para guardar el vehículo
  probarAPI(): void {
    // Realiza una solicitud POST a la API FastAPI
    this.http.get('https://anthonyx82.ddns.net/taller/api/saludo')
    .subscribe(response => {
      console.log(response);
    });
  }
}
