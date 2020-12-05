import {OnInit} from '@angular/core';

export class TrafficType implements OnInit{
  public owner: string;
  public name: string;
  public ipAddress: string;


  constructor(owner: string, name: string, address: string) {
    this.owner = owner;
    this.name = name;
    this.ipAddress = address;

  }

  ngOnInit(): void {
  }

  toString(){
    return JSON.stringify(this);
  }
}
