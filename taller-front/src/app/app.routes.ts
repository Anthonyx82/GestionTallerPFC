import { Routes } from '@angular/router';
import { RegisterComponent } from './pages/register/register.component';
import { MisVehiculosComponent } from './mis-vehiculos/mis-vehiculos.component';
import { LoginComponent } from './pages/login/login.component';
import { EditarVehiculoComponent } from './editar-vehiculo/editar-vehiculo.component';
import { InformePublicoComponent } from './informe-publico/informe-publico.component';

export const routes: Routes = [
    { path: 'register', component: RegisterComponent },
    { path: 'login', component: LoginComponent },
    { path: 'mis-vehiculos', component: MisVehiculosComponent },
    { path: 'editar-vehiculo/:id', component: EditarVehiculoComponent },
    { path: 'informe/:token', component: InformePublicoComponent }
];
