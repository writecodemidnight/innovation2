export interface User {
  id: number;
  username: string;
  realName?: string;
  avatarUrl?: string;
  role: string;
  phone?: string;
  email?: string;
  status: string;
  clubId?: number;
  clubName?: string;
  createdAt: string;
  updatedAt: string;
}

export enum UserRole {
  STUDENT = 'STUDENT',
  CLUB_MEMBER = 'CLUB_MEMBER',
  CLUB_MANAGER = 'CLUB_MANAGER',
  CLUB_PRESIDENT = 'CLUB_PRESIDENT',
  ADMIN = 'ADMIN',
  SUPER_ADMIN = 'SUPER_ADMIN'
}

/**
 * 登录响应类型
 * 对应后端 LoginResponse
 */
export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  tokenType: string;
  user: User;
}
