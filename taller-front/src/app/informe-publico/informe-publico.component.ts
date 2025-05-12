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
  revisionesPreparadas: { seccion: string, puntos: string[] }[] = [];

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
        this.prepararRevisiones();
        this.cargando = false;
      },
      error: () => {
        this.error = 'Informe no encontrado o expirado.';
        this.cargando = false;
      }
    });
  }

  prepararRevisiones(): void {
    const revision = this.datosInforme?.vehiculo?.revision;
    this.revisionesPreparadas = [];

    if (revision && typeof revision === 'object') {
      for (const seccion in revision) {
        if (Array.isArray(revision[seccion])) {
          this.revisionesPreparadas.push({
            seccion,
            puntos: revision[seccion]
          });
        }
      }
    }
  }

  descargarPDF(): void {
    const doc = new jsPDF({ unit: 'pt', format: 'a4' });
    const pageWidth = doc.internal.pageSize.getWidth();

    // -- Encabezado --
    doc.setFillColor(255, 111, 0);
    doc.rect(0, 0, pageWidth, 80, 'F');
    doc.setFontSize(24);
    doc.setTextColor('#ffffff');
    doc.text('Informe del Vehículo', pageWidth / 2, 50, { align: 'center' });

    // -- Datos del vehículo --
    const v = this.datosInforme.vehiculo;
    let cursorY = 110;
    doc.setFillColor(245, 245, 245);
    doc.roundedRect(20, cursorY - 10, pageWidth - 40, 100, 8, 8, 'F');
    doc.setTextColor('#333333');
    doc.setFontSize(12);
    doc.text(`Marca: ${v.marca}`, 30, cursorY);
    doc.text(`Modelo: ${v.modelo}`, 200, cursorY);
    doc.text(`Año: ${v.year}`, 380, cursorY);
    cursorY += 20;
    doc.text(`VIN: ${v.vin}`, 30, cursorY);
    doc.text(`Velocidad: ${v.velocidad} km/h`, 200, cursorY);
    doc.text(`RPM: ${v.rpm}`, 380, cursorY);

    // -- Puntos revisados --
    cursorY += 40;
    doc.setFontSize(16);
    doc.setTextColor(255, 111, 0);
    doc.text('Puntos revisados', 30, cursorY);
    cursorY += 20;
    doc.setFontSize(12);
    doc.setTextColor('#555555');

    this.revisionesPreparadas.forEach(({ seccion, puntos }) => {
      if (cursorY > 750) {
        doc.addPage();
        cursorY = 40;
      }
      doc.text(`• ${this.titleCase(seccion)}:`, 40, cursorY);
      cursorY += 16;

      puntos.forEach((punto) => {
        if (cursorY > 750) {
          doc.addPage();
          cursorY = 40;
        }
        doc.text(`  - ${punto}`, 60, cursorY);
        cursorY += 16;
      });

      cursorY += 10;
    });

    // -- Errores detectados --
    if (cursorY > 750) {
      doc.addPage();
      cursorY = 40;
    }
    doc.setFontSize(16);
    doc.setTextColor(255, 111, 0);
    doc.text('Errores detectados', 30, cursorY);
    cursorY += 20;
    doc.setFontSize(12);
    doc.setTextColor('#cc3300');

    this.datosInforme.errores.forEach((err: string) => {
      if (cursorY > 750) {
        doc.addPage();
        cursorY = 40;
      }
      doc.text(`• ${err}`, 40, cursorY);
      cursorY += 18;
    });

    // -- Guardar PDF --
    doc.save(`informe-vehiculo-${v.vin}.pdf`);
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

  private titleCase(text: string): string {
    return text.replace(/\w\S*/g, (txt) => txt[0].toUpperCase() + txt.substring(1).toLowerCase());
  }
}
