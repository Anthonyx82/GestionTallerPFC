import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './interceptors/auth.interceptor';
import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

/**
 * Configuración principal de la aplicación Angular.
 * Define los proveedores globales, incluyendo:
 * - Detección de cambios optimizada con event coalescing
 * - Configuración de rutas
 * - Formularios reactivos
 * - Cliente HTTP con interceptores
 * - Animaciones asincrónicas
 */
export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    ReactiveFormsModule,
    provideHttpClient(
      withInterceptors([authInterceptor])
    ), provideAnimationsAsync()
  ]
};
