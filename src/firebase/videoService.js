// Video Upload and Analysis Service
// This is the ONLY backend integration for the MVP
// Everything else uses mock data

import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';
import { collection, addDoc, doc, updateDoc, getDoc } from 'firebase/firestore';
import { storage, db } from './config';

/**
 * Upload video file to Firebase Storage
 * @param {File} file - Video file from input
 * @param {Function} onProgress - Progress callback (percent)
 * @returns {Promise<string>} - Download URL
 */
export const uploadVideo = async (file, onProgress) => {
  const timestamp = Date.now();
  const fileName = `${timestamp}_${file.name}`;
  const storageRef = ref(storage, `videos/${fileName}`);
  
  const uploadTask = uploadBytesResumable(storageRef, file);
  
  return new Promise((resolve, reject) => {
    uploadTask.on(
      'state_changed',
      (snapshot) => {
        const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        if (onProgress) onProgress(progress);
      },
      (error) => reject(error),
      async () => {
        const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
        resolve(downloadURL);
      }
    );
  });
};

/**
 * Save video metadata to Firestore
 * @param {Object} videoData - Video metadata
 * @returns {Promise<string>} - Document ID
 */
export const saveVideoMetadata = async (videoData) => {
  const docRef = await addDoc(collection(db, 'videos'), {
    ...videoData,
    uploadedAt: new Date(),
    status: 'processing',
    analysisComplete: false
  });
  
  return docRef.id;
};

/**
 * Update video with analysis results
 * @param {string} videoId - Firestore document ID
 * @param {Object} analysisData - Analysis results
 */
export const updateVideoAnalysis = async (videoId, analysisData) => {
  const videoRef = doc(db, 'videos', videoId);
  
  await updateDoc(videoRef, {
    analysis: analysisData,
    analysisComplete: true,
    status: 'completed',
    analyzedAt: new Date()
  });
};

/**
 * Get video and analysis data
 * @param {string} videoId - Firestore document ID
 * @returns {Promise<Object>} - Video data with analysis
 */
export const getVideoAnalysis = async (videoId) => {
  const videoRef = doc(db, 'videos', videoId);
  const videoSnap = await getDoc(videoRef);
  
  if (videoSnap.exists()) {
    return { id: videoSnap.id, ...videoSnap.data() };
  }
  
  throw new Error('Video not found');
};

/**
 * Simulate AI analysis (replace with actual media pipeline integration)
 * @param {string} videoUrl - Video URL from storage
 * @returns {Promise<Object>} - Mock analysis results
 */
export const analyzeVideo = async (videoUrl) => {
  // TODO: Replace with actual Video AI / Media Pipeline API call
  // For now, return mock data after delay to simulate processing
  
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        movements: {
          squatDepth: 85,
          kneeAlignment: 92,
          hipMobility: 78
        },
        recommendations: [
          'Increase depth gradually',
          'Focus on knee tracking',
          'Work on hip flexibility'
        ],
        riskScore: 'low',
        confidence: 0.89
      });
    }, 3000); // Simulate 3 second analysis
  });
};
