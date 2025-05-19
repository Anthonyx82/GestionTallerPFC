import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';

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

    if (!token) {
      this.error = 'Token no válido';
      this.cargando = false;
      return;
    }

    this.http.get(`https://anthonyx82.ddns.net/taller/api/informe/${token}`).subscribe({
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
    this.revisionesPreparadas = [];
  
    const rawRevision = this.datosInforme?.vehiculo?.revision;
  
    let revision: Record<string, string[]> | null = null;
  
    if (typeof rawRevision === 'string') {
      try {
        const safeJson = rawRevision.replace(/'/g, '"');
        revision = JSON.parse(safeJson);
      } catch (e) {
        console.error('Error al parsear la revisión:', e);
      }
    } else if (typeof rawRevision === 'object' && rawRevision !== null) {
      revision = rawRevision;
    }
  
    if (revision) {
      for (const seccion in revision) {
        if (Array.isArray(revision[seccion])) {
          this.revisionesPreparadas.push({
            seccion,
            puntos: revision[seccion]
          });
        }
      }
    }
  
    console.log('Revisiones preparadas:', this.revisionesPreparadas);
  }

  async descargarPDF(): Promise<void> {
    const element = document.querySelector('.informe-container') as HTMLElement;
    if (!element) return;
  
    // Import dinámico compatible con Angular 18
    const html2pdfModule = await import('html2pdf.js');
    const html2pdf = html2pdfModule.default || html2pdfModule;
  
    const opt = {
      margin:       0,
      filename:     `informe-vehiculo-${this.datosInforme.vehiculo.vin}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2 },
      jsPDF:        { unit: 'pt', format: 'a4', orientation: 'portrait' }
    };
  
    // Clonar para eliminar botones sin afectar el DOM real
    const clone = element.cloneNode(true) as HTMLElement;
    const acciones = clone.querySelector('.acciones');
    if (acciones) acciones.remove();
  
    html2pdf().set(opt).from(clone).save();
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
