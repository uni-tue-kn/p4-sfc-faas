import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import {AuthService} from "../../auth/auth.service";
import {FirewallRule} from "../../models/FirewallRule";
import {MatTableDataSource} from "@angular/material/table";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {SelectionModel} from "@angular/cdk/collections";
import {ConfigService} from "../../shared/services/config.service";
import {FirewallVnfConfig} from "../../models/FirewallVnfConfig";
import {TrafficType} from "../../models/TrafficType";

@Component({
  selector: 'app-register',
  templateUrl: './user.component.html',
  styleUrls: ['./user.component.css']
})
export class UserComponent implements OnInit {

  configuredTrafficTypesDatasource: MatTableDataSource<TrafficType>;
  trafficTypeFormGroup: FormGroup;
  displayedColumns = ['select', 'name', 'address'];
  selection = new SelectionModel<TrafficType>(true, []);

  constructor(private _formBuilder: FormBuilder, private changeDetectorRefs: ChangeDetectorRef, public authService: AuthService, public configService: ConfigService) {}


  ngOnInit() {

    this.configService.fetchTrafficTypes()
      .subscribe((res: any) => {
        this.configService.trafficTypes = res;
        this.configuredTrafficTypesDatasource = new MatTableDataSource<TrafficType>(this.configService.trafficTypes);
        console.log('Defined MatTableDatasource with: ' + JSON.stringify(this.configService.trafficTypes))
      }, err => {
        console.log(err);
      });



    this.trafficTypeFormGroup = this._formBuilder.group({
      name: ['', Validators.required],
      address: ['', Validators.required],
    });
  }


  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.configuredTrafficTypesDatasource.data.length;
    return numSelected === numRows;
  }

  /** Selects all rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    this.isAllSelected() ?
      this.selection.clear():
      this.configuredTrafficTypesDatasource.data.forEach(row => this.selection.select(row));
  }

  addTrafficType(){
    let trafficType = new TrafficType(this.authService.uid, this.trafficTypeFormGroup.get('name').value,
      this.trafficTypeFormGroup.get('address').value);

    if(trafficType.name == '' || trafficType.ipAddress == ''){
      console.log('Traffic type not defined properly: ' + trafficType)
    }
    else{
      this.configService.addTrafficType(trafficType).subscribe((res: TrafficType) => {
        this.ngOnInit();
      }, err => {
        console.log(err);
      });
    }
  }

  deleteSelectedTrafficTypes(){
    for(let selection in this.selection.selected){
      console.log('Delete the following Traffic Type: ' + JSON.stringify(this.selection.selected[selection]));
      this.configService.deleteTrafficType(this.selection.selected[selection]).subscribe(res => {
        this.ngOnInit();
      }, err => {
        console.log(err);
      });
    }
    this.selection.clear();
  }
}
