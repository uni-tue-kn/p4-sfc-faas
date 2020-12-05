import {OnInit} from '@angular/core';
import {VnfConfig} from "./VnfConfig";
import {TrafficType} from "./TrafficType";

export class SfcConfig implements OnInit{

  // TODO: VnfConfig[] instead of string, TrafficType instead of string
  constructor(public owner: string, public trafficType: string, /*public vnfs: VnfConfig[]*/ public vnfs: string) {
  }

  ngOnInit(): void {
  }

  toString(){
    return JSON.stringify(this);
  }
}
