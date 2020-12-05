import {Component, Input, OnInit} from '@angular/core';
import {VnfConfig} from "../../../models/VnfConfig";

@Component({
  selector: 'app-sfc-visual',
  templateUrl: './sfc-visual.component.html',
  styleUrls: ['./sfc-visual.component.css']
})
export class SfcVisualComponent implements OnInit {

  @Input() sfcConfig;
  sfcConfigJsonObject;
  vnfs;
  trafficType;

  constructor() { }

  ngOnInit(): void {
    //this.sfcConfig = JSON.parse(this.sfcConfig)
    this.sfcConfigJsonObject = JSON.parse(JSON.stringify(this.sfcConfig));
    console.log(this.sfcConfigJsonObject.id)
    this.vnfs = JSON.parse(this.sfcConfigJsonObject.vnfs);
    this.trafficType = JSON.parse(this.sfcConfigJsonObject.trafficType)

  }

}
