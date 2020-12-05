import { Injectable } from '@angular/core';
import {OAuthService, UserInfo} from 'angular-oauth2-oidc';
import { authCodeFlowConfig } from './auth.config';
import * as jwt_decode from 'jwt-decode';
import Swal from 'sweetalert2'
import {tryCatch} from "rxjs/internal-compatibility";

const promiseTimeout = function(ms, promise){

  // Create a promise that rejects in <ms> milliseconds
  let timeout = new Promise((resolve, reject) => {
    let id = setTimeout(() => {
      clearTimeout(id);
      reject('Timed out in '+ ms + 'ms.')
    }, ms)
  })

  // Returns a race between our timeout and the passed in promise
  return Promise.race([
    promise,
    timeout
  ])
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  userinfo: UserInfo;
  keycloakAvailable: boolean;

  constructor(private oauthService: OAuthService) {
    this.configureSingleSignOn();
  }

  configureSingleSignOn(){
    this.oauthService.configure(authCodeFlowConfig);
    this.oauthService.setupAutomaticSilentRefresh();
    promiseTimeout(1000, this.oauthService.loadDiscoveryDocumentAndTryLogin()).then((response) => {
      if (this.oauthService.hasValidAccessToken()) {
        this.oauthService.loadUserProfile().then((t) => {
          this.userinfo = t;
        });
      }
    }).catch((err) => {
      if(err == "Timed out in 1000ms." || err.ok == false){
        Swal.fire('Oops.. ', 'SSO (Keycloak) is not available!', 'error');
      }else{
        console.log("Catched error" + err)
      }
    });


  }



  login(){

    promiseTimeout(1000, this.oauthService.loadDiscoveryDocumentAndTryLogin()).then((response) => {
      console.log('Keycloak available. Logging in...');
      this.oauthService.initLoginFlow();
    }).catch((err) => {
      if(err == "Timed out in 1000ms."|| err.ok == false){
        Swal.fire('Oops.. ', 'SSO (Keycloak) is not available!', 'error');
      }else{
        console.log("Catched error" + err)
      }
    });
  }

  logout(){

    promiseTimeout(1000, this.oauthService.loadDiscoveryDocumentAndTryLogin()).then((response) => {
      console.log('Keycloak available. Logging out...');
      this.oauthService.logOut();

      this.oauthService.revokeTokenAndLogout();
    }).catch((err) => {
      if(err == "Timed out in 1000ms."){
        Swal.fire('Oops.. ', 'SSO (Keycloak) is not available!', 'error');
      }
    });

  }

  get givenName() {
    return this.userinfo == null ? null : this.userinfo.preferred_username;
  }

  get uid() {
    return this.userinfo == null ? null : this.userinfo.sub;
  }

  isLoggedIn(){
    return !(this.userinfo == null);
  }

  hasConfidentialRole(){
    let decoded = jwt_decode(this.oauthService.getAccessToken());
    return (-1) !== decoded.realm_access.roles.indexOf('view-confidential');

  }

  getAuthHeader(){
    return this.oauthService.authorizationHeader();
  }
}
