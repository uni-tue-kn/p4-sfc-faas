import {OnInit} from '@angular/core';

export class FirewallRule implements OnInit{
  public policy: string;
  public direction: string;
  public protocol: string;
  public port: number;
  public name: string;

  constructor(name: string, policy: string, direction: string, protocol: string, port: number) {
    this.name = name;
    this.policy = policy;
    this.direction = direction;
    this.protocol = protocol;
    this.port = port;
  }

  ngOnInit(): void {
  }

  toString(){
    return JSON.stringify(this);
  }
}
