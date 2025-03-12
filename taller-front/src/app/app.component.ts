import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Api Automotriz';
  description = 'Bienvenido a la primera api para taller. Gestionamos la información de tus vehículos en tiempo real y te ofrecemos un servicio rápido y eficiente con tecnología avanzada.';
  
  constructor(private http: HttpClient) {}

  // Método para probar la API
  probarAPI(): void {
    this.http.get('https://anthonyx82.ddns.net/taller/api/saludo')
      .subscribe(response => {
        console.log(response);
      });
  }
}
