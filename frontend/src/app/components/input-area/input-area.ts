import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-input-area',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './input-area.html',
  styleUrl: './input-area.scss'
})
export class InputAreaComponent {
  @Input() disabled = false;
  @Input() placeholder = 'Nhap trieu chung cua ban...';
  @Output() messageSent = new EventEmitter<string>();

  @ViewChild('inputField') inputField!: ElementRef<HTMLTextAreaElement>;

  messageText = '';

  onSend(): void {
    const trimmedMessage = this.messageText.trim();
    if (trimmedMessage && !this.disabled) {
      this.messageSent.emit(trimmedMessage);
      this.messageText = '';
      this.resetTextareaHeight();
    }
  }

  onKeyDown(event: KeyboardEvent): void {
    // Send on Enter (without Shift)
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onSend();
    }
  }

  onInput(): void {
    this.autoResize();
  }

  private autoResize(): void {
    const textarea = this.inputField?.nativeElement;
    if (textarea) {
      textarea.style.height = 'auto';
      const maxHeight = 120;
      textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px';
    }
  }

  private resetTextareaHeight(): void {
    const textarea = this.inputField?.nativeElement;
    if (textarea) {
      textarea.style.height = 'auto';
    }
  }

  focusInput(): void {
    this.inputField?.nativeElement?.focus();
  }
}
