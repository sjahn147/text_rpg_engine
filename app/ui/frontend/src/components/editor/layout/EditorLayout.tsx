/**
 * 에디터 레이아웃 컴포넌트
 * EditorSidebar와 EditorMainArea를 통합하는 레이아웃 래퍼
 */
import React from 'react';
import { EditorSidebar, EditorSidebarProps } from './EditorSidebar';
import { EditorMainArea, EditorMainAreaProps } from './EditorMainArea';

export interface EditorLayoutProps {
  // Sidebar Props
  sidebarProps: EditorSidebarProps;
  // Main Area Props
  mainAreaProps: EditorMainAreaProps;
}

export const EditorLayout: React.FC<EditorLayoutProps> = ({
  sidebarProps,
  mainAreaProps,
}) => {
  return (
    <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>
      <EditorSidebar {...sidebarProps} />
      <EditorMainArea {...mainAreaProps} />
    </div>
  );
};

