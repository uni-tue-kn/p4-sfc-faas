import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { VnfComponent } from './vnf.component';

describe('VnfComponent', () => {
  let component: VnfComponent;
  let fixture: ComponentFixture<VnfComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ VnfComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(VnfComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
