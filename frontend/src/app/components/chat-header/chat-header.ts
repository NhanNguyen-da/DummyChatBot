import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chat-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chat-header.html',
  styleUrl: './chat-header.scss'
})
export class ChatHeaderComponent {
  @Output() resetChat = new EventEmitter<void>();
  @Output() toggleLanguage = new EventEmitter<string>();

  currentLanguage = 'VI';
  hospitalName = 'Benh Vien Da Khoa';

  onResetChat(): void {
    this.resetChat.emit();
  }

  onToggleLanguage(): void {
    this.currentLanguage = this.currentLanguage === 'VI' ? 'EN' : 'VI';
    this.toggleLanguage.emit(this.currentLanguage);
  }
}
