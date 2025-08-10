'use client';

import { useEffect, useState } from 'react';
import { db } from '@/lib/localdb/db';
import { seedSampleProject } from '@/lib/localdb/seeds';

export function useBootstrapLocalData() {
  const [isLoading, setIsLoading] = useState(true);
  const [isEmpty, setIsEmpty] = useState(false);
  const [showBootstrapModal, setShowBootstrapModal] = useState(false);

  useEffect(() => {
    async function checkData() {
      try {
        const projectCount = await db.projects.count();
        const isDataEmpty = projectCount === 0;
        
        setIsEmpty(isDataEmpty);
        
        // Auto-seed in development
        if (isDataEmpty && process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_AUTO_SEED === 'true') {
          await seedSampleProject();
          setIsEmpty(false);
        } else if (isDataEmpty) {
          setShowBootstrapModal(true);
        }
      } catch (error) {
        console.error('Failed to check local data:', error);
      } finally {
        setIsLoading(false);
      }
    }

    checkData();
  }, []);

  const createSampleProject = async () => {
    setIsLoading(true);
    try {
      await seedSampleProject();
      setIsEmpty(false);
      setShowBootstrapModal(false);
    } catch (error) {
      console.error('Failed to create sample project:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startBlank = () => {
    setShowBootstrapModal(false);
    setIsEmpty(false);
  };

  return {
    isLoading,
    isEmpty,
    showBootstrapModal,
    createSampleProject,
    startBlank
  };
}