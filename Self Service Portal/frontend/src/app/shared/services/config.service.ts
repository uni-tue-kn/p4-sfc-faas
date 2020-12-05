import {Injectable, OnInit} from '@angular/core';
import {AuthService} from '../../auth/auth.service';
import {VnfConfig} from '../../models/VnfConfig';
import {TrafficType} from '../../models/TrafficType';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable, of} from 'rxjs';
import {catchError, tap} from 'rxjs/operators';
import Swal from 'sweetalert2'
import {environment} from "../../../environments/environment";
import {MatTableDataSource} from "@angular/material/table";
import {SfcConfig} from "../../models/SfcConfig";
import {stringify} from "querystring";

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  // tslint:disable:variable-name
  private _trafficTypes: TrafficType[] = [];
  private _vnfConfigs: VnfConfig[] = [];
  private _sfcConfigs: SfcConfig[] = [];
  private _vnfInventory: VnfConfig[] = [];


  // Variables used in http calls for authentication at backend
  private creds = this.authService.getAuthHeader();
  private httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: this.creds});
  private httpOptions = {headers: this.httpheaders}

  public isLoadingSFC = false;

  constructor(public authService: AuthService, private httpClient: HttpClient) {

    // sync traffic types
    this.fetchTrafficTypes()
      .subscribe((res: any) => {
        this._trafficTypes = res;
      }, err => {
        console.log(err);
      });

    // sync SFCs
    this.fetchSFCs()
      .subscribe((res: any) => {
        this._sfcConfigs = res;
      }, err => {
        console.log(err);
      });

    // sync VNFs
    this.fetchVNFs()
      .subscribe((res: any) => {
        this._vnfConfigs = res;
        this.syncVnfInventory();
      }, err => {
        console.log(err);
      });
  }

  get vnfConfigs(){
    return this._vnfConfigs;
  }
  set vnfConfigs(vnfConfigs){
   this._vnfConfigs = vnfConfigs;
  }

  get vnfInventory(){
    return this._vnfInventory;
  }
  set vnfInventory(vnfConfigs){
    this._vnfInventory = vnfConfigs;
  }

  get trafficTypes(){
    return this._trafficTypes;
  }

  set trafficTypes(trafficTypes) {
    this._trafficTypes = trafficTypes;
  }

  get sfcConfigs(): SfcConfig[] {
    return this._sfcConfigs;
  }

  set sfcConfigs(sfcconfs: SfcConfig[]) {
    this._sfcConfigs = sfcconfs;
  }

  syncVnfInventory(){
    let vnfsInUse = "";
    this.vnfInventory = []

    for(let sfc of this.sfcConfigs){
      vnfsInUse += sfc.vnfs.toString()
    }
    for(let vnf of this.vnfConfigs){
      if(!vnfsInUse.includes(JSON.stringify(vnf))){
        this.vnfInventory.push(vnf);
      }
    }
  }


  addVNF(vnfConfig){
    return this.httpClient.post(environment.apiBaseUrl + '/VNF/', vnfConfig, this.httpOptions)
      .pipe(
        catchError(this.handleError('addVNF', []))
      )
  }

  fetchVNFs(){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders}

    return this.httpClient.get(environment.apiBaseUrl + '/VNF/', options).pipe(
      catchError(this.handleError('fetchVNFs', []))
    );
  }

  deleteVNF(vnfID){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders};

    return this.httpClient.delete(environment.apiBaseUrl + '/VNF/' + vnfID, options)
      .pipe(
        catchError(this.handleError('deleteVNF', []))
      )
  }

  addSFC(userSfcConfig){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders};

    return this.httpClient.post(environment.apiBaseUrl + '/SFC/', userSfcConfig, options)
      .pipe(
        catchError(this.handleError('addTrafficType', []))
      )
  }

  fetchSFCs(){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders}

    return this.httpClient.get(environment.apiBaseUrl + '/SFC/', options).pipe(
      catchError(this.handleError('fetchSFCs', []))
    );
  }

  deleteSFC(sfcID){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders};

    return this.httpClient.delete(environment.apiBaseUrl + '/SFC/' + sfcID, options)
      .pipe(
        catchError(this.handleError('deleteSFC', []))
      )
  }

  addTrafficType(userTrafficType){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders}

    return this.httpClient.post(environment.apiBaseUrl + '/TrafficTypes/', userTrafficType, options)
      .pipe(
        catchError(this.handleError('addTrafficType', []))
      )
  }

  fetchTrafficTypes(){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders}

    return this.httpClient.get(environment.apiBaseUrl + '/TrafficTypes/', options).pipe(
      catchError(this.handleError('fetchTrafficTypes', []))
    );

  }

  deleteTrafficType(userTrafficType){
    const creds = this.authService.getAuthHeader();
    const httpheaders = new HttpHeaders({'Content-Type': 'application/json', Authorization: creds});
    const options = {headers: httpheaders}

    return this.httpClient.delete(environment.apiBaseUrl + '/TrafficTypes/' + userTrafficType.id + '/', options)
      .pipe(
        catchError(this.handleError('addTrafficType', []))
      )
  }

  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      console.error(error); // log to console instead
      Swal.fire('Oops.. ', 'Somethings wrong with communication to the backend!', 'error');

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }
}
