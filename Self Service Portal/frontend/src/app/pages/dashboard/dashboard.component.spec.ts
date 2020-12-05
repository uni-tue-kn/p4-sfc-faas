import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfidentialComponent } from './dashboard.component';

describe('ConfidentialComponent', () => {
  let component: ConfidentialComponent;
  let fixture: ComponentFixture<ConfidentialComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConfidentialComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfidentialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
