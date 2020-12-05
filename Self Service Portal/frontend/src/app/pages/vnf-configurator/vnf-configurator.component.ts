import {ChangeDetectorRef, Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {FirewallRule} from '../../models/FirewallRule'
import {MatTableDataSource} from "@angular/material/table";
import {SelectionModel} from "@angular/cdk/collections";
import {FirewallVnfConfig} from "../../models/FirewallVnfConfig";
import {AuthService} from "../../auth/auth.service";
import {ConfigService} from "../../shared/services/config.service";
import {VnfConfig} from "../../models/VnfConfig";
import {TrafficType} from "../../models/TrafficType";
import Swal from "sweetalert2";
import { NavigationExtras, Router} from "@angular/router";

const PRECONFIGURED_RULES: FirewallRule[] = [new FirewallRule('Block-HTTP', 'DENY', 'BOTH', 'TCP', 80),
                                                  new FirewallRule('Block-ICMP', 'DENY', 'BOTH', 'ICMP', 0)];

@Component({
  selector: 'app-vnf-configurator',
  templateUrl: './vnf-configurator.component.html',
  styleUrls: ['./vnf-configurator.component.css']
})
export class VnfConfiguratorComponent implements OnInit {

  firewallRules: FirewallRule[];
  configuredRulesDatasource: MatTableDataSource<FirewallRule>;

  isLinear = true;
  vnfTypeFormGroup: FormGroup;
  customFormGroup: FormGroup;
  requirementsFormGroup: FormGroup;
  firewallFormGroup: FormGroup;
  displayedColumns = ['select', 'name', 'policy', 'protocol', 'port']; //'direction',
  selection = new SelectionModel<FirewallRule>(true, []);

  getFirewallRules(){
    return this.firewallRules;
  }

  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.configuredRulesDatasource.data.length;
    return numSelected === numRows;
  }

  /** Selects all rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    this.isAllSelected() ?
      this.selection.clear() :
      this.configuredRulesDatasource.data.forEach(row => this.selection.select(row));
  }

  constructor(private _formBuilder: FormBuilder, private changeDetectorRefs: ChangeDetectorRef,
              private authService: AuthService, private configService: ConfigService, private router: Router) {}

  ngOnInit() {
    this.firewallRules=[];
    this.firewallRules=this.firewallRules.concat(PRECONFIGURED_RULES);

    this.configuredRulesDatasource = new MatTableDataSource<FirewallRule>(this.firewallRules);

    this.vnfTypeFormGroup = this._formBuilder.group({
      name: ['', Validators.required],
      type: ['', Validators.required],
    });

    this.requirementsFormGroup = this._formBuilder.group( {
      vcpus: ['', Validators.required],
      vmem: ['', Validators.required],
      virtualization: ['', Validators.required],
    });

    this.customFormGroup = this._formBuilder.group({
      custom: [''],
      bidirectional: [true],
    });

    this.firewallFormGroup = this._formBuilder.group({
      name: ['',],
      policy: ['',],
     // direction: ['',],
      protocol: ['',],
      port: ['',],
    });
  }

  submit(){

    // TODO: Better handling of firewallrules
    // TODO: Make firewall not always bidirectional!
    let newVNFConf: VnfConfig;
    if(this.vnfTypeFormGroup.get('type').value == 'firewall'){
      newVNFConf = new FirewallVnfConfig(this.authService.uid, this.vnfTypeFormGroup.get('name').value,
        this.vnfTypeFormGroup.get('type').value, true, this.requirementsFormGroup.get('virtualization').value,
        this.requirementsFormGroup.get('vcpus').value, this.requirementsFormGroup.get('vmem').value, JSON.stringify(this.firewallRules));
    }
    else if (this.vnfTypeFormGroup.get('type').value == 'custom'){
      newVNFConf = new VnfConfig(this.authService.uid, this.vnfTypeFormGroup.get('name').value,
        this.vnfTypeFormGroup.get('type').value, this.customFormGroup.get('bidirectional').value, this.requirementsFormGroup.get('virtualization').value,
        this.requirementsFormGroup.get('vcpus').value, this.requirementsFormGroup.get('vmem').value);
    }

    console.log("Submit VNF: " + newVNFConf)

    // Update the vnfConfigs in configService and push vnfConfig to inventory
    this.configService.addVNF(newVNFConf).subscribe((res: VnfConfig) => {
      this.configService.vnfInventory.push(res);

      this.configService.fetchVNFs().subscribe((res: VnfConfig[]) => {
          this.configService.vnfConfigs = res;

        Swal.fire({
          position: 'center',
          icon: 'success',
          title: 'The VNF definition is saved and is available for use in an SFC.',
          showConfirmButton: false,
          timer: 1500
        });

        this.ngOnInit();

      }, err => {
        console.log(err);
      });
    });


  }

  addFirewallRule() {

    let rule = new FirewallRule(this.firewallFormGroup.get('name').value,
      this.firewallFormGroup.get('policy').value,
      'BOTH',
      //this.firewallFormGroup.get('direction').value,
      this.firewallFormGroup.get('protocol').value,
      this.firewallFormGroup.get('port').value);

    if(rule.policy == '' || rule.name == '' || rule.direction == '' || rule.protocol == ''){
      console.log('Firewall rule not defined properly.')
    }
    else{

      this.firewallRules = this.firewallRules.concat([rule]);
      this.configuredRulesDatasource = new MatTableDataSource<FirewallRule>(this.firewallRules);
    }
    console.log(this.firewallRules)
  };


  deleteSelectedFirewallRules() {
    console.log(this.selection.selected);

    for(let rule of this.selection.selected){

      let index = this.firewallRules.indexOf(rule, 0);
      if(index > -1){
        this.firewallRules.splice(index,1);
        this.firewallRules = this.firewallRules.concat([]);
      }

    }
    console.log(this.firewallRules)

    this.configuredRulesDatasource = new MatTableDataSource<FirewallRule>(this.firewallRules);
  }
}



