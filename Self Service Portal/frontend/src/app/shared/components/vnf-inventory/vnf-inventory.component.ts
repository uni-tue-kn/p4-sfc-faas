import {Component, Input, OnInit} from '@angular/core';
import {VnfConfig} from '../../../models/VnfConfig';
import {AuthService} from '../../../auth/auth.service';
import {ConfigService} from '../../services/config.service';

@Component({
  selector: 'app-vnf-inventory',
  templateUrl: './vnf-inventory.component.html',
  styleUrls: ['./vnf-inventory.component.css']
})
export class VnfInventoryComponent implements OnInit {

  @Input() public draggableItems: boolean;

  constructor(public configService: ConfigService) {
  }

  ngOnInit(): void {

  }
}
