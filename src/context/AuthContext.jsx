import { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged, signInWithPopup, signOut } from 'firebase/auth'
import { doc, getDoc, setDoc, updateDoc, serverTimestamp } from 'firebase/firestore'
import { auth, db, googleProvider } from '../firebase/config'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [userProfile, setUserProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser)
      if (firebaseUser) {
        const docRef = doc(db, 'users', firebaseUser.uid)
        const docSnap = await getDoc(docRef)
        if (docSnap.exists()) {
          setUserProfile(docSnap.data())
        } else {
          setUserProfile(null)
        }
      } else {
        setUserProfile(null)
      }
      setLoading(false)
    })
    return unsubscribe
  }, [])

  const signInWithGoogle = async () => {
    const result = await signInWithPopup(auth, googleProvider)
    return result.user
  }

  const logout = async () => {
    await signOut(auth)
    setUser(null)
    setUserProfile(null)
  }

  const saveProfile = async (profileData) => {
    const docRef = doc(db, 'users', user.uid)
    const data = {
      ...profileData,
      uid: user.uid,
      email: user.email,
      displayName: profileData.fullName || user.displayName,
      photoURL: user.photoURL,
      status: 'pending',
      createdAt: serverTimestamp(),
    }
    await setDoc(docRef, data)
    setUserProfile(data)
  }

  const refreshProfile = async () => {
    if (!user) return
    const docRef = doc(db, 'users', user.uid)
    const docSnap = await getDoc(docRef)
    if (docSnap.exists()) {
      setUserProfile(docSnap.data())
    }
  }

  return (
    <AuthContext.Provider value={{ user, userProfile, loading, signInWithGoogle, logout, saveProfile, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
