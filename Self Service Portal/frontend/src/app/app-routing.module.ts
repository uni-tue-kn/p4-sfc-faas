import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {HomeComponent} from './pages/home/home.component';
import {AuthGuard, ConfidentialAuthGuard} from './auth/auth-guard.service';
import {SfcConfiguratorComponent} from './pages/sfc-configurator/sfc-configurator.component';
import {VnfConfiguratorComponent} from "./pages/vnf-configurator/vnf-configurator.component";
import {DashboardComponent} from "./pages/dashboard/dashboard.component";
import {UserComponent} from "./pages/user/user.component";


const routes: Routes = [
  {path: 'home', component: HomeComponent},
  {path: 'vnf-configurator', component: VnfConfiguratorComponent, canActivate: [AuthGuard]},
  {path: 'sfc-configurator', component: SfcConfiguratorComponent, canActivate: [AuthGuard]},
  {path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard]},
  {path: 'user', component: UserComponent},
  {path: '**', redirectTo: 'home'}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
