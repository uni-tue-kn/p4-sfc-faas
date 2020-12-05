import { Component, OnInit } from '@angular/core';
import {AuthService} from '../../../auth/auth.service';
import {environment} from "../../../../environments/environment";

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  navbarOpen = false;
  envName = environment.name;

  constructor(public authService: AuthService) { }

  ngOnInit(): void {
  }



  toggleNavbar() {
    console.log("toggle navbar");
    this.navbarOpen = !this.navbarOpen;
  }
}
