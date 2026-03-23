// frontend\src\hooks\useApi.js
import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

/**
 * Custom hook for API calls with loading and error states
 */
export const useApi = (apiFunction, immediate = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const execute = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await apiFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Une erreur est survenue';
        setError(errorMessage);
        toast.error(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction]
  );

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  const refetch = useCallback(() => {
    return execute();
  }, [execute]);

  return {
    data,
    loading,
    error,
    execute,
    refetch,
  };
};

/**
 * Hook for API calls with pagination
 */
export const usePaginatedApi = (apiFunction, initialParams = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [params, setParams] = useState(initialParams);

  const fetchData = useCallback(
    async (currentPage = 1, currentParams = params) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await apiFunction({
          page: currentPage,
          limit: 20,
          ...currentParams,
        });
        
        setData(result.data || result);
        setPage(currentPage);
        
        if (result.totalPages) {
          setTotalPages(result.totalPages);
        }
        
        if (result.totalItems) {
          setTotalItems(result.totalItems);
        }
        
        return result;
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Une erreur est survenue';
        setError(errorMessage);
        toast.error(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, params]
  );

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const goToPage = useCallback(
    (newPage) => {
      if (newPage >= 1 && newPage <= totalPages) {
        fetchData(newPage);
      }
    },
    [fetchData, totalPages]
  );

  const updateParams = useCallback(
    (newParams) => {
      setParams(prev => ({ ...prev, ...newParams }));
    },
    []
  );

  const nextPage = useCallback(() => {
    if (page < totalPages) {
      goToPage(page + 1);
    }
  }, [page, totalPages, goToPage]);

  const prevPage = useCallback(() => {
    if (page > 1) {
      goToPage(page - 1);
    }
  }, [page, goToPage]);

  const refresh = useCallback(() => {
    fetchData(page);
  }, [fetchData, page]);

  return {
    data,
    loading,
    error,
    page,
    totalPages,
    totalItems,
    goToPage,
    nextPage,
    prevPage,
    updateParams,
    refresh,
  };
};

/**
 * Hook for infinite scroll API calls
 */
export const useInfiniteApi = (apiFunction, initialParams = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [params, setParams] = useState(initialParams);

  const fetchData = useCallback(
    async (currentPage = 1, currentParams = params, append = false) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await apiFunction({
          page: currentPage,
          limit: 20,
          ...currentParams,
        });
        
        const newData = result.data || result;
        
        if (append) {
          setData(prev => [...prev, ...newData]);
        } else {
          setData(newData);
        }
        
        setPage(currentPage);
        setHasMore(newData.length === 20); // Assuming limit is 20
        
        return result;
      } catch (err) {
        const errorMessage = err.response?.data?.detail || err.message || 'Une erreur est survenue';
        setError(errorMessage);
        toast.error(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, params]
  );

  useEffect(() => {
    fetchData(1, params, false);
  }, [fetchData, params]);

  const loadMore = useCallback(() => {
    if (hasMore && !loading) {
      fetchData(page + 1, params, true);
    }
  }, [hasMore, loading, page, fetchData, params]);

  const refresh = useCallback(() => {
    fetchData(1, params, false);
  }, [fetchData, params]);

  const updateParams = useCallback(
    (newParams) => {
      setParams(prev => ({ ...prev, ...newParams }));
      setPage(1);
      setHasMore(true);
    },
    []
  );

  return {
    data,
    loading,
    error,
    hasMore,
    loadMore,
    refresh,
    updateParams,
  };
};