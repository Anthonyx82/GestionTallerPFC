import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Componente para mostrar mensajes de error.
 * Recibe un mensaje de error como input y lo muestra en la interfaz.
 */
@Component({
  selector: 'app-error-message',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './error-message.component.html',
  styleUrls: ['./error-message.component.css']
})
export class ErrorMessageComponent {
  /**
   * Mensaje de error que se mostrará.
   */
  @Input() message: string = '';
}
