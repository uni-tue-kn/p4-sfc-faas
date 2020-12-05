import {Component, Input, OnInit} from '@angular/core';
import {VnfConfig} from '../../../models/VnfConfig';
import {ConfigService} from '../../services/config.service';
import {clearElement} from '@angular/cdk/testing/testbed/fake-events';

@Component({
  selector: 'app-vnf',
  templateUrl: './vnf.component.html',
  styleUrls: ['./vnf.component.css']
})
export class VnfComponent implements OnInit {

  constructor(public configService: ConfigService) { }

  @Input() public vnfConfig: VnfConfig;
  @Input()public deletable = true;

  ngOnInit(): void {
  }

  onXClick() {
    // TODO: Implement X button
    // this.removed = true;
    // if (this.deletable) {
    //   this.configService.vnfConfigs = this.configService.vnfConfigs.filter(item => item !== this.vnfConfig);
    // }
    // else {
    //   this.configService.sfcConfig = this.configService.sfcConfig.vnfs.filter(item => item !== this.vnfConfig);
    // }
  }

}
