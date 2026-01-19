/**
 * department.service.ts - Service xử lý department API
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Department, DepartmentResponse } from '../models/department.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {
  private apiUrl = `${environment.apiUrl}/departments`;

  constructor(private http: HttpClient) { }

  /**
   * Lấy tất cả các khoa
   * @returns Observable với danh sách các khoa
   */
  getAllDepartments(): Observable<DepartmentResponse> {
    return this.http.get<DepartmentResponse>(this.apiUrl);
  }

  /**
   * Lấy thông tin một khoa theo ID
   * @param id - ID của khoa
   * @returns Observable với thông tin khoa
   */
  getDepartmentById(id: number): Observable<Department> {
    return this.http.get<Department>(`${this.apiUrl}/${id}`);
  }
}
