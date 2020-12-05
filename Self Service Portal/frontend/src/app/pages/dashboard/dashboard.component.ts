import { Component, OnInit } from '@angular/core';
import {AuthService} from '../../auth/auth.service';
import {ConfigService} from '../../shared/services/config.service';
import Swal from "sweetalert2";
import {TrafficType} from "../../models/TrafficType";
import {stringify} from "querystring";

@Component({
  selector: 'app-confidential',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {

  constructor(private authService: AuthService, public configService: ConfigService) { }

  ngOnInit(): void {
    this.configService.fetchSFCs()
      .subscribe((res: any) => {
        this.configService.sfcConfigs = res;
        console.log('onOnit activeSfcConfig: ' + this.configService.sfcConfigs);
      }, err => {
        console.log(err);
      });
  }

  deleteSFC(sfcConfig){
    console.log('Delete SFC with ID ' + sfcConfig.id + ' ... ');

    Swal.fire({
      title: 'Are you sure to delete this SFC?',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
      if (result.isConfirmed) {

        this.configService.deleteSFC(sfcConfig.id)
          .subscribe((res: any) => {
            console.log('DONE.');

            this.configService.fetchSFCs()
              .subscribe((res: any) => {
                this.configService.sfcConfigs = res;
                console.log('onOnit activeSfcConfig: ' + this.configService.sfcConfigs);
              }, err => {
                console.log(err);
              });

            Swal.fire({
              position: 'center',
              icon: 'success',
              title: 'Deleted!',
              html: 'The SFC has been deleted.',
              showConfirmButton: false,
              timer: 1500
            });


          }, err => {
            console.log(err);
          });


      }
    })


  }

  deleteVNF(vnfConfig){
    console.log('Delete VNF with ID ' + vnfConfig.id + ' ... ');

    this.configService.syncVnfInventory();

    console.log('vnfCOnfig: ' + JSON.stringify(vnfConfig));
    console.log('vnfInventory: ' + JSON.stringify(this.configService.vnfInventory));

    if(!this.configService.vnfInventory.includes(vnfConfig)){
      console.log('VNF is used in an active SFC. Please delete SFC first.')
      Swal.fire({
        title: 'VNF is in use!',
        text: 'VNF is currently used in an active SFC. Please delete the respective SFC first.',
        icon: 'warning'
      })
    }else{

      Swal.fire({
        title: 'Are you sure to delete this VNF?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.isConfirmed) {
          this.configService.deleteVNF(vnfConfig.id)
            .subscribe((res: any) => {
              console.log('DONE.');

              this.configService.fetchVNFs()
                .subscribe((res: any) => {
                  this.configService.vnfConfigs = res;
                }, err => {
                  console.log(err);
                });

              Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Deleted!',
                html: 'The VNF has been deleted.',
                showConfirmButton: false,
                timer: 1500
              });

            }, err => {
              console.log(err);
            });


        }
      })
    }
  }

}
