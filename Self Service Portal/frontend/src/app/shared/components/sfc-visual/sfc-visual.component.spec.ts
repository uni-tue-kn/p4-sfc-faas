import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SfcVisualComponent } from './sfc-visual.component';

describe('SfcVisualComponent', () => {
  let component: SfcVisualComponent;
  let fixture: ComponentFixture<SfcVisualComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SfcVisualComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SfcVisualComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
