<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人资料</h2>
    </div>

    <div class="profile-content">
      <!-- 用户信息卡片 -->
      <el-card class="profile-card" v-loading="userLoading">
        <template #header>
          <div class="card-header">
            <span>用户信息</span>
            <el-button type="primary" link @click="openEditUserDialog">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </template>
        <div class="user-info">
          <div class="avatar-section">
            <el-avatar :size="100" :src="userForm.avatarUrl || defaultAvatar" />
            <el-button type="primary" link @click="uploadAvatar">更换头像</el-button>
          </div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用户ID">{{ userForm.id }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ userForm.username }}</el-descriptions-item>
            <el-descriptions-item label="昵称">{{ userForm.nickname || '-' }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag :type="getRoleType(userForm.role)">{{ getRoleLabel(userForm.role) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="手机号">{{ userForm.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ userForm.email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="userForm.status === 'ACTIVE' ? 'success' : 'danger'">
                {{ userForm.status === 'ACTIVE' ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatDateTime(userForm.createdAt) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-card>

      <!-- 社团信息卡片 -->
      <el-card class="club-card" v-loading="clubLoading">
        <template #header>
          <div class="card-header">
            <span>我的社团</span>
            <el-button type="primary" link @click="openEditClubDialog">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </template>
        <div class="club-info" v-if="clubInfo.id">
          <div class="club-logo">
            <el-avatar :size="80" :src="clubInfo.logoUrl || defaultClubLogo" shape="square" />
          </div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="社团ID">{{ clubInfo.id }}</el-descriptions-item>
            <el-descriptions-item label="社团名称">{{ clubInfo.name }}</el-descriptions-item>
            <el-descriptions-item label="社团编码">{{ clubInfo.code }}</el-descriptions-item>
            <el-descriptions-item label="类别">
              <el-tag>{{ getCategoryLabel(clubInfo.category) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="clubInfo.status === 'ACTIVE' ? 'success' : 'danger'">
                {{ clubInfo.status === 'ACTIVE' ? '正常' : '停用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="成员数">{{ clubInfo.memberCount }} 人</el-descriptions-item>
            <el-descriptions-item label="指导教师">{{ clubInfo.facultyAdvisor || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDateTime(clubInfo.createdAt) }}</el-descriptions-item>
            <el-descriptions-item label="社团描述" :span="2">{{ clubInfo.description || '暂无描述' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div v-else class="empty-club">
          <el-empty description="暂无社团信息" />
        </div>
      </el-card>

      <!-- 统计数据卡片 -->
      <el-card class="stats-card" v-loading="statsLoading">
        <template #header>
          <div class="card-header">
            <span>社团活动统计</span>
          </div>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ clubStats.activityCount || 0 }}</div>
            <div class="stat-label">活动总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ clubStats.totalParticipants || 0 }}</div>
            <div class="stat-label">总参与人数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ clubStats.pendingCount || 0 }}</div>
            <div class="stat-label">待审批活动</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ clubStats.ongoingCount || 0 }}</div>
            <div class="stat-label">进行中活动</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 编辑用户信息对话框 -->
    <el-dialog v-model="editUserDialogVisible" title="编辑个人信息" width="500px">
      <el-form label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editUserForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editUserForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editUserForm.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editUserDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingUser" @click="saveUserInfo">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑社团信息对话框 -->
    <el-dialog v-model="editClubDialogVisible" title="编辑社团信息" width="500px">
      <el-form :model="clubForm" label-width="100px">
        <el-form-item label="社团名称">
          <el-input v-model="editClubForm.name" placeholder="请输入社团名称" />
        </el-form-item>
        <el-form-item label="社团类别">
          <el-select v-model="editClubForm.category" placeholder="请选择类别" style="width: 100%">
            <el-option label="学术科技" value="ACADEMIC" />
            <el-option label="文化艺术" value="ARTS" />
            <el-option label="体育运动" value="SPORTS" />
            <el-option label="公益志愿" value="VOLUNTEER" />
            <el-option label="科技创新" value="TECHNOLOGY" />
            <el-option label="传统文化" value="CULTURE" />
            <el-option label="其他" value="OTHER" />
          </el-select>
        </el-form-item>
        <el-form-item label="指导教师">
          <el-input v-model="editClubForm.facultyAdvisor" placeholder="请输入指导教师姓名" />
        </el-form-item>
        <el-form-item label="社团描述">
          <el-input v-model="editClubForm.description" type="textarea" :rows="4" placeholder="请输入社团描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editClubDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingClub" @click="saveClubInfo">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Edit } from '@element-plus/icons-vue';
import { apiClient, formatDateTime, UserRoleMap } from '@campus/shared';
import { useUserStore } from '@/stores/user';

// 社团类别标签映射（本地定义，避免构建问题）
const ClubCategoryMap: Record<string, { label: string; color: string }> = {
  'ACADEMIC': { label: '学术科技', color: '#409EFF' },
  'ARTS': { label: '文化艺术', color: '#E6A23C' },
  'SPORTS': { label: '体育运动', color: '#67C23A' },
  'VOLUNTEER': { label: '公益志愿', color: '#F56C6C' },
  'TECHNOLOGY': { label: '科技创新', color: '#909399' },
  'CULTURE': { label: '传统文化', color: '#8B4513' },
  'OTHER': { label: '其他', color: '#606266' },
};

const userStore = useUserStore();
const route = useRoute();

// 监听路由变化，每次进入页面都重新获取数据
watch(() => route.path, (newPath) => {
  if (newPath === '/profile') {
    console.log('[Profile] Route changed to /profile, fetching data...');
    fetchUserInfo();
  }
});

// 加载状态
const userLoading = ref(false);
const clubLoading = ref(false);
const statsLoading = ref(false);
const savingUser = ref(false);
const savingClub = ref(false);

// 对话框显示状态
const editUserDialogVisible = ref(false);
const editClubDialogVisible = ref(false);

// 默认头像
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default';
const defaultClubLogo = 'https://api.dicebear.com/7.x/identicon/svg?seed=club';

// 用户信息
const userForm = ref({
  id: 0,
  username: '',
  nickname: '',
  role: '',
  phone: '',
  email: '',
  status: '',
  avatarUrl: '',
  createdAt: '',
});

// 社团信息
const clubInfo = ref({
  id: 0,
  name: '',
  code: '',
  category: '',
  status: '',
  memberCount: 0,
  facultyAdvisor: '',
  description: '',
  logoUrl: '',
  createdAt: '',
});

// 社团表单（用于编辑）
const clubForm = ref({
  name: '',
  category: '',
  facultyAdvisor: '',
  description: '',
});

// 编辑表单（对话框中使用）
const editUserForm = ref({
  nickname: '',
  phone: '',
  email: '',
});

const editClubForm = ref({
  name: '',
  category: '',
  facultyAdvisor: '',
  description: '',
});

// 社团统计数据
const clubStats = ref({
  activityCount: 0,
  totalParticipants: 0,
  pendingCount: 0,
  ongoingCount: 0,
});

// 获取角色标签类型
function getRoleType(role: string) {
  const typeMap: Record<string, string> = {
    'STUDENT': 'info',
    'CLUB_MEMBER': 'primary',
    'CLUB_PRESIDENT': 'success',
    'ADMIN': 'warning',
    'SUPER_ADMIN': 'danger',
  };
  return typeMap[role] || 'info';
}

// 获取角色标签文本
function getRoleLabel(role: string) {
  return UserRoleMap[role as keyof typeof UserRoleMap]?.label || role;
}

// 获取社团类别标签
function getCategoryLabel(category: string) {
  return ClubCategoryMap[category]?.label || category;
}

// 获取当前用户信息
async function fetchUserInfo() {
  userLoading.value = true;
  try {
    const response = await apiClient.get('/api/v1/users/me');
    const data = response.data || response;
    // 完全替换，避免旧数据残留
    userForm.value = {
      id: data.id || 0,
      username: data.username || '',
      nickname: data.nickname || '',
      role: data.role || '',
      phone: data.phone || '',
      email: data.email || '',
      status: data.status || '',
      avatarUrl: data.avatarUrl || '',
      createdAt: data.createdAt || '',
    };
    console.log('[Profile] 用户信息:', userForm.value);

    // 社团端只有社长使用，直接获取我的社团
    await fetchMyClub();
  } catch (error: any) {
    console.error('获取用户信息失败:', error);
    ElMessage.error('获取用户信息失败');
  } finally {
    userLoading.value = false;
  }
}

// 获取我的社团信息
async function fetchMyClub() {
  clubLoading.value = true;
  console.log('[Profile] 开始获取我的社团信息...');
  try {
    const response = await apiClient.get('/api/v1/clubs/my');
    console.log('[Profile] API 原始响应:', response);

    // 处理 ApiResponse 包装的数据
    const data = response.data || response;
    console.log('[Profile] 提取的社团数据:', data);

    if (!data || !data.id) {
      console.warn('[Profile] 社团数据为空或没有ID');
      ElMessage.warning('您还没有创建社团');
      return;
    }

    // 直接替换整个对象确保响应式更新
    clubInfo.value = {
      id: data.id,
      name: data.name || '',
      code: data.code || '',
      category: data.category || '',
      status: data.status || '',
      memberCount: data.memberCount || 0,
      facultyAdvisor: data.facultyAdvisor || '',
      description: data.description || '',
      logoUrl: data.logoUrl || '',
      createdAt: data.createdAt || '',
    };

    console.log('[Profile] 赋值后的clubInfo:', clubInfo.value);

    // 获取社团统计
    await fetchClubStats(data.id);

    ElMessage.success('社团信息加载成功');
  } catch (error: any) {
    console.error('[Profile] 获取社团信息失败:', error);
    const errorMsg = error.response?.data?.message || error.message || '获取社团信息失败';
    console.error('[Profile] 错误详情:', errorMsg);
    ElMessage.error(errorMsg);
  } finally {
    clubLoading.value = false;
  }
}

// 获取社团信息
async function fetchClubInfo(clubId: number) {
  clubLoading.value = true;
  try {
    const response = await apiClient.get(`/api/v1/clubs/${clubId}`);
    const data = response.data || response;
    clubInfo.value = { ...clubInfo.value, ...data };
  } catch (error: any) {
    console.error('获取社团信息失败:', error);
  } finally {
    clubLoading.value = false;
  }
}

// 获取社团统计数据
async function fetchClubStats(clubId: number) {
  statsLoading.value = true;
  try {
    const response = await apiClient.get(`/api/v1/clubs/${clubId}/stats`);
    const data = response.data || response;
    clubStats.value = { ...clubStats.value, ...data };
  } catch (error: any) {
    console.error('获取社团统计失败:', error);
    // 如果接口不存在，使用默认值
  } finally {
    statsLoading.value = false;
  }
}

// 打开编辑用户对话框
function openEditUserDialog() {
  editUserForm.value = {
    nickname: userForm.value.nickname || '',
    phone: userForm.value.phone || '',
    email: userForm.value.email || '',
  };
  editUserDialogVisible.value = true;
}

// 保存用户信息
async function saveUserInfo() {
  savingUser.value = true;
  try {
    await apiClient.put('/api/v1/users/me', {
      nickname: editUserForm.value.nickname,
      phone: editUserForm.value.phone,
      email: editUserForm.value.email,
    });
    ElMessage.success('保存成功');
    editUserDialogVisible.value = false;
    // 更新 store 中的用户信息
    await fetchUserInfo();
  } catch (error: any) {
    console.error('保存用户信息失败:', error);
    ElMessage.error(error.message || '保存失败');
  } finally {
    savingUser.value = false;
  }
}

// 打开编辑社团对话框
function openEditClubDialog() {
  editClubForm.value = {
    name: clubInfo.value.name || '',
    category: clubInfo.value.category || '',
    facultyAdvisor: clubInfo.value.facultyAdvisor || '',
    description: clubInfo.value.description || '',
  };
  editClubDialogVisible.value = true;
}

// 保存社团信息
async function saveClubInfo() {
  if (!clubInfo.value.id) return;

  savingClub.value = true;
  try {
    await apiClient.put(`/api/v1/clubs/${clubInfo.value.id}`, {
      name: editClubForm.value.name,
      category: editClubForm.value.category,
      facultyAdvisor: editClubForm.value.facultyAdvisor,
      description: editClubForm.value.description,
    });
    ElMessage.success('保存成功');
    editClubDialogVisible.value = false;
    await fetchClubInfo(clubInfo.value.id);
  } catch (error: any) {
    console.error('保存社团信息失败:', error);
    ElMessage.error(error.message || '保存失败');
  } finally {
    savingClub.value = false;
  }
}

// 上传头像
function uploadAvatar() {
  ElMessage.info('头像上传功能开发中');
}

onMounted(async () => {
  console.log('[Profile] Page mounted, fetching user info...');
  fetchUserInfo();
});
</script>

<style scoped lang="scss">
.profile-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;

  h2 {
    margin: 0;
    color: #303133;
  }
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card,
.club-card,
.stats-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.user-info,
.club-info {
  display: flex;
  gap: 24px;

  .avatar-section,
  .club-logo {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }

  .el-descriptions {
    flex: 1;
  }
}

.empty-club {
  padding: 40px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  .stat-item {
    text-align: center;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    .stat-value {
      font-size: 32px;
      font-weight: 600;
      color: #409EFF;
      margin-bottom: 8px;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

@media (max-width: 768px) {
  .user-info,
  .club-info {
    flex-direction: column;
    align-items: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
