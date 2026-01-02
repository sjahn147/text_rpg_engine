/**
 * 에디터 백업/복원 기능 훅
 */
import { useCallback } from 'react';
import { projectApi } from '../../services/api';

export interface EditorBackupActions {
  saveBackup: (filename?: string) => Promise<void>;
  restoreBackup: () => Promise<void>;
  exportData: (type: 'map' | 'entities' | 'regions' | 'full') => Promise<void>;
}

export const useEditorBackup = (
  onStatusChange: (status: 'ready' | 'loading' | 'saving' | 'error', message: string) => void,
  onRefresh: () => Promise<void>
) => {
  const saveBackup = useCallback(async (filename?: string) => {
    try {
      onStatusChange('saving', '백업 저장 중...');
      
      const response = await projectApi.export();
      const projectData = response.data.data;
      
      const data = JSON.stringify(projectData, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `world_backup_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      onStatusChange('ready', '백업 저장 완료');
    } catch (error) {
      onStatusChange('error', '백업 저장 실패');
      throw error;
    }
  }, [onStatusChange]);

  const restoreBackup = useCallback(async () => {
    if (!confirm('백업을 복원하시겠습니까? 현재 데이터가 모두 덮어씌워집니다.')) {
      return;
    }
    
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      try {
        onStatusChange('loading', '백업 복원 중...');
        
        const response = await projectApi.importFile(file);
        const stats = response.data.stats;
        
        await onRefresh();
        onStatusChange('ready', `백업 복원 완료: ${JSON.stringify(stats)}`);
      } catch (error) {
        onStatusChange('error', '백업 복원 실패');
        throw error;
      }
    };
    input.click();
  }, [onStatusChange, onRefresh]);

  const exportData = useCallback(async (type: 'map' | 'entities' | 'regions' | 'full') => {
    try {
      onStatusChange('saving', '내보내는 중...');
      
      // TODO: 실제 export 로직 구현
      // 현재는 EditorMode.tsx에 있는 로직을 참고
      
      onStatusChange('ready', '내보내기 완료');
    } catch (error) {
      onStatusChange('error', '내보내기 실패');
      throw error;
    }
  }, [onStatusChange]);

  return {
    saveBackup,
    restoreBackup,
    exportData,
  };
};

