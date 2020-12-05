import {OnInit} from '@angular/core';

export class VnfConfig implements OnInit{

  constructor(public owner: string, public applicationName: string, public serviceType: string, public bidirectional: boolean,
              public virtualization: string, public vcpus: number, public vmemory: number) {
  }

  ngOnInit(): void {
  }

  toString(){
    return JSON.stringify(this);
  }
}
