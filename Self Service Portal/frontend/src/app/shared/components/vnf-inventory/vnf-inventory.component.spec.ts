import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VnfInventoryComponent } from './vnf-inventory.component';

describe('VnfInventoryComponent', () => {
  let component: VnfInventoryComponent;
  let fixture: ComponentFixture<VnfInventoryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VnfInventoryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VnfInventoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
