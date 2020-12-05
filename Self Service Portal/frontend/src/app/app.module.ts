import { BrowserModule } from '@angular/platform-browser';
import { NgModule} from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatSliderModule} from '@angular/material/slider';
import {MatToolbarModule} from '@angular/material/toolbar';
import { HomeComponent } from './pages/home/home.component';

import { HttpClientModule} from '@angular/common/http';
import { OAuthModule } from 'angular-oauth2-oidc';
import { AuthService } from './auth/auth.service';
import {AuthGuard} from './auth/auth-guard.service';
import {DragDropModule} from '@angular/cdk/drag-drop';
import {MatButtonToggleModule} from '@angular/material/button-toggle';
import {MatButtonModule} from '@angular/material/button';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NavbarComponent } from './shared/components/navbar/navbar.component';
import {MatCardModule} from '@angular/material/card';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { VnfComponent } from './shared/components/vnf/vnf.component';
import { VnfInventoryComponent } from './shared/components/vnf-inventory/vnf-inventory.component';
import { SfcConfiguratorComponent } from './pages/sfc-configurator/sfc-configurator.component';
import {NgxJsonViewerModule} from 'ngx-json-viewer';
import { VnfConfiguratorComponent } from './pages/vnf-configurator/vnf-configurator.component';
import {MatStepperModule} from "@angular/material/stepper";
import {MatInputModule} from "@angular/material/input";
import {MatListModule} from "@angular/material/list";
import {MatSelectModule} from "@angular/material/select";
import {MatTableModule} from "@angular/material/table";
import {MatCheckboxModule} from "@angular/material/checkbox";
import {DashboardComponent} from "./pages/dashboard/dashboard.component";
import { UserComponent } from './pages/user/user.component';
import { SfcVisualComponent } from './shared/components/sfc-visual/sfc-visual.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    VnfConfiguratorComponent,
    DashboardComponent,
    NavbarComponent,
    VnfComponent,
    VnfInventoryComponent,
    SfcConfiguratorComponent,
    VnfConfiguratorComponent,
    UserComponent,
    SfcVisualComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    HttpClientModule,
    OAuthModule.forRoot({
      resourceServer: {
        allowedUrls: ['http://www.angular.at/api'], // TODO: Urls aendern
        sendAccessToken: true
      }
    }),
    DragDropModule,
    MatButtonModule,
    NgbModule,
    FormsModule,
    NgxJsonViewerModule,
    ReactiveFormsModule,
    MatStepperModule,
    MatInputModule,
    MatListModule,
    MatSelectModule,
    MatTableModule,
    MatCheckboxModule,
    MatCardModule
  ],
  providers: [AuthService, AuthGuard],
  bootstrap: [AppComponent]
})
export class AppModule {}

