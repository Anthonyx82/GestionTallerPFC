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

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn): Observable<any> => {
  const router = inject(Router);
  const token = localStorage.getItem('token');

  const authReq = token ? req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  }) : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        console.log('Token inválido o expirado. Redirigiendo a login...');

        // ✅ Esta línea soluciona problemas de ciclo de vida del Router
        setTimeout(() => router.navigateByUrl('/login'), 0);
      }
      return throwError(() => error);
    })
  );
};