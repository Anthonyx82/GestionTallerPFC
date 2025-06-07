import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { Router } from '@angular/router';

/**
 * Guard que protege rutas que requieren autenticación.
 * Verifica si existe un token en localStorage.
 * Si no hay token, redirige a la página de login y bloquea el acceso.
 */
export const authGuard: CanActivateFn = (route, state) => {
  const token = localStorage.getItem('token');
  const router = inject(Router);

  if (!token) {
    router.navigateByUrl('/login');
    return false;
  }

  return true;
};
