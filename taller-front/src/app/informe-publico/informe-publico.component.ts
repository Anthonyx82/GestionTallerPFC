import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { jsPDF } from 'jspdf';

@Component({
  selector: 'app-informe-publico',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './informe-publico.component.html',
  styleUrls: ['./informe-publico.component.scss']
})
export class InformePublicoComponent {
  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);

  datosInforme: any = null;
  cargando = true;
  error = '';

  ngOnInit(): void {
    const token = this.route.snapshot.paramMap.get('token'); 
    const tokenAuth = localStorage.getItem('token');

    if (!token || !tokenAuth) {
      this.error = 'Token no válido o no autenticado';
      this.cargando = false;
      return;
    }

    const headers = new HttpHeaders().set('Authorization', `Bearer ${tokenAuth}`);

    this.http.get(`https://anthonyx82.ddns.net/taller/api/informe/${token}`, { headers }).subscribe({
      next: (res) => {
        this.datosInforme = res;
        this.cargando = false;
      },
      error: () => {
        this.error = 'Informe no encontrado o expirado.';
        this.cargando = false;
      }
    });
  }

  descargarPDF(): void {
    const doc = new jsPDF();

    const v = this.datosInforme.vehiculo;
    const errores = this.datosInforme.errores;

    doc.setFontSize(20);
    doc.text('Informe del Vehículo', 20, 20);

    doc.setFontSize(12);
    doc.text(`Marca: ${v.marca}`, 20, 40);
    doc.text(`Modelo: ${v.modelo}`, 20, 50);
    doc.text(`Año: ${v.year}`, 20, 60);
    doc.text(`VIN: ${v.vin}`, 20, 70);
    doc.text(`Velocidad: ${v.velocidad} km/h`, 20, 80);
    doc.text(`RPM: ${v.rpm}`, 20, 90);

    doc.text('Errores detectados:', 20, 110);
    errores.forEach((err: any, i: number) => {
      doc.text(`- ${err}`, 25, 120 + i * 10);
    });

    doc.save('informe-vehiculo.pdf');
  }

  compartir(): void {
    const url = window.location.href;
    if (navigator.share) {
      navigator.share({
        title: 'Informe del Vehículo',
        text: 'Consulta el informe de tu vehículo:',
        url
      });
    } else {
      alert('Enlace copiado al portapapeles');
      navigator.clipboard.writeText(url);
    }
  }
}
