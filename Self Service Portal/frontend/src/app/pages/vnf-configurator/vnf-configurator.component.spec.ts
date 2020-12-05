import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VnfConfiguratorComponent } from './vnf-configurator.component';

describe('VnfConfiguratorNewComponent', () => {
  let component: VnfConfiguratorComponent;
  let fixture: ComponentFixture<VnfConfiguratorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VnfConfiguratorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VnfConfiguratorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
