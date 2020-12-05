import {VnfConfig} from "./VnfConfig";
import {FirewallRule} from "./FirewallRule";

export class FirewallVnfConfig extends VnfConfig{

  constructor(public owner: string, public applicationName: string, public serviceType: string, public bidirectional: boolean,
  public virtualization: string,
              public vcpus: number, public vmemory: number, public firewallRules: string) {
    super(owner,  applicationName,  serviceType, bidirectional, virtualization, vcpus,  vmemory);
    this.firewallRules = firewallRules;
  }

}
