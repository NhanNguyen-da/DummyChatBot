import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Message } from '../../models/message.model';

@Component({
  selector: 'app-message',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './message.html',
  styleUrl: './message.scss'
})
export class MessageComponent {
  @Input() message!: Message;

  get isBot(): boolean {
    return this.message.type === 'bot';
  }

  get isUser(): boolean {
    return this.message.type === 'user';
  }

  get isSystem(): boolean {
    return this.message.type === 'system';
  }

  get isAlert(): boolean {
    return this.message.type === 'alert';
  }

  get formattedTime(): string {
    const date = new Date(this.message.timestamp);
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  get alertClass(): string {
    if (!this.message.alertLevel) return '';
    return `alert-${this.message.alertLevel}`;
  }
}
