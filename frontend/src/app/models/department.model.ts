/**
 * department.model.ts - Model cho thông tin khoa/phòng
 */

export interface Department {
  id: number;
  name: string;
  description: string;
  commonSymptoms?: string[];
  location?: string;
  workingHours?: string;
}

export interface DepartmentResponse {
  departments: Department[];
}
