/**
 * 에디터 검색 기능 훅
 */
import { useState, useCallback } from 'react';
import { searchApi } from '../../services/api';

export interface SearchResult {
  entity_type: string;
  entity_id: string;
  entity_name: string;
  field: string;
  match_text: string;
}

export interface EditorSearchState {
  searchQuery: string;
  searchResults: SearchResult[];
  isSearching: boolean;
}

export interface EditorSearchActions {
  setSearchQuery: (query: string) => void;
  performSearch: (query: string) => Promise<void>;
  clearSearch: () => void;
}

export const useEditorSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResultsState] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const performSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await searchApi.search(query);
      setSearchResultsState(response.data.results || []);
      setSearchQuery(query);
    } catch (error) {
      console.error('검색 실패:', error);
      setSearchResultsState([]);
      throw error;
    } finally {
      setIsSearching(false);
    }
  }, []);

  const setSearchResults = useCallback((results: SearchResult[]) => {
    setSearchResultsState(results);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResultsState([]);
  }, []);

  return {
    // State
    searchQuery,
    searchResults,
    isSearching,
    // Actions
    setSearchQuery,
    setSearchResults,
    performSearch,
    clearSearch,
  };
};

