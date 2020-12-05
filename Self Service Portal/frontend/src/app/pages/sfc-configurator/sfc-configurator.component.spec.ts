import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SfcConfiguratorComponent } from './sfc-configurator.component';

describe('SfcConfiguratorComponent', () => {
  let component: SfcConfiguratorComponent;
  let fixture: ComponentFixture<SfcConfiguratorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SfcConfiguratorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SfcConfiguratorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
