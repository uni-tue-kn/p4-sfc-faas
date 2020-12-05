import { Component, OnInit } from '@angular/core';
import {CdkDragDrop, moveItemInArray, transferArrayItem} from '@angular/cdk/drag-drop';
import {ConfigService} from '../../shared/services/config.service';
import {VnfConfig} from '../../models/VnfConfig';
import {AuthService} from '../../auth/auth.service';
import {MatTableDataSource} from "@angular/material/table";
import {TrafficType} from "../../models/TrafficType";
import {SfcConfig} from "../../models/SfcConfig";
import Swal from "sweetalert2";
import {stringify} from "querystring";

@Component({
  selector: 'app-sfc-configurator',
  templateUrl: './sfc-configurator.component.html',
  styleUrls: ['./sfc-configurator.component.css']
})
export class SfcConfiguratorComponent implements OnInit {

  selectedTrafficType: string;
  unusedTrafficTypes: TrafficType[] = [];
  public vnfsInSfc: VnfConfig[] = [];
  public sfcConfig: SfcConfig;

  constructor(public configService: ConfigService, public authService: AuthService) {

  }

  ngOnInit(): void {
    // sync VNFs
    this.configService.fetchVNFs()
      .subscribe((res: any) => {
        this.configService.vnfConfigs = res;
      }, err => {
        console.log(err);
      });

    this.configService.syncVnfInventory();

    this.configService.fetchTrafficTypes()
      .subscribe((res: any) => {
        this.configService.trafficTypes = res;
        console.log('All trafficTypes: ' + this.configService.trafficTypes.toString());

        // Compute unused Traffic Types. A traffic type can not be used twice,
        // since this leads to ambiguous or faulty classfication of a packet.
        let trafficTypesInUse = [];
        for (let sfc of this.configService.sfcConfigs){
          trafficTypesInUse.push(sfc.trafficType);
          console.log('sfc.trafficType: ' + sfc.trafficType.toString());
        }
        console.log('trafficTypesInUSe: ' + trafficTypesInUse.toString());

        for(let trafficType of this.configService.trafficTypes){

          console.log('configService.trafficType: ' + JSON.stringify(trafficType));
          if(!(trafficTypesInUse.includes(JSON.stringify(trafficType)))){
            this.unusedTrafficTypes.push(trafficType);
          }
        }

        console.log('unusedTrafficTypes: ' + this.unusedTrafficTypes.toString());

      }, err => {
        console.log(err);
      });
  }

  dropVnfConfig(event: CdkDragDrop<VnfConfig[]>) {
    if (event.previousContainer === event.container) {
      console.log('Drag&Drop: Move item in array.')
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      console.log('Drag&Drop: Transfer array item.')
      transferArrayItem(event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex);
    }
  }

  applySFC() {

    if(this.selectedTrafficType == undefined){
      console.log('Traffic type must be selected!') // TODO: Better feedback for user
    }
    else{
      this.sfcConfig = new SfcConfig(JSON.stringify(this.authService.uid), JSON.stringify(this.selectedTrafficType), JSON.stringify(this.vnfsInSfc)); // TODO: Vnfs not as string!
      console.log('Applying SFC: ' + this.sfcConfig.toString());

      this.configService.addSFC(this.sfcConfig).subscribe((res: SfcConfig) => {
        this.configService.fetchSFCs().subscribe((res: SfcConfig[]) => {
          this.configService.sfcConfigs = res;
          this.vnfsInSfc = [];
          this.unusedTrafficTypes = [];
          this.selectedTrafficType = '';


          this.configService.fetchTrafficTypes()
            .subscribe((res: any) => {
              this.configService.trafficTypes = res;

              // Compute unused Traffic Types. A traffic type can not be used twice,
              // since this leads to ambiguous or faulty classfication of a packet.
              let trafficTypesInUse = [];

              for (let sfc of this.configService.sfcConfigs){
                trafficTypesInUse.push(sfc.trafficType);
              }

              for(let trafficType of this.configService.trafficTypes){
                if(!(trafficTypesInUse.includes(JSON.stringify(trafficType)))){
                  this.unusedTrafficTypes.push(trafficType);
                }
              }
            }, err => {
              console.log(err);
            });


          Swal.fire({
            position: 'center',
            icon: 'success',
            title: 'The SFC definition is saved and will now be applied.',
            showConfirmButton: false,
            timer: 1500
          });
        }, err => {
          console.log(err);
        });
      });


    }

  }

}
