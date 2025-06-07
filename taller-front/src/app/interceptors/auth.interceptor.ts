import { inject } from '@angular/core';
import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpErrorResponse
} from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

/**
 * Interceptor HTTP para agregar el token de autorización en las cabeceras
 * de las solicitudes salientes y manejar errores de autenticación.
 * 
 * Si la respuesta HTTP devuelve un error 401 (no autorizado),
 * redirige al usuario a la página de login.
 */
export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn): Observable<any> => {
  const router = inject(Router);
  const token = localStorage.getItem('token');

  // Clona la solicitud y añade el token en la cabecera Authorization si existe.
  const authReq = token ? req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  }) : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // En caso de error 401, redirige a login
      if (error.status === 401) {
        setTimeout(() => router.navigateByUrl('/login'), 0);
      }
      return throwError(() => error);
    })
  );
};
