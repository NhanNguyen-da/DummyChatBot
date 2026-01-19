import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuickReply } from '../../models/message.model';

@Component({
  selector: 'app-quick-reply',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './quick-reply.html',
  styleUrl: './quick-reply.scss'
})
export class QuickReplyComponent {
  @Input() replies: QuickReply[] = [];
  @Output() replySelected = new EventEmitter<QuickReply>();

  onSelect(reply: QuickReply): void {
    this.replySelected.emit(reply);
  }
}
