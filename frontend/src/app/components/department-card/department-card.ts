import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DepartmentRecommendation } from '../../models/message.model';

@Component({
  selector: 'app-department-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './department-card.html',
  styleUrl: './department-card.scss'
})
export class DepartmentCardComponent {
  @Input() department!: DepartmentRecommendation;
  @Output() bookAppointment = new EventEmitter<DepartmentRecommendation>();
  @Output() startOver = new EventEmitter<void>();

  onBookAppointment(): void {
    this.bookAppointment.emit(this.department);
  }

  onStartOver(): void {
    this.startOver.emit();
  }
}
