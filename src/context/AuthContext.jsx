import { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged, signInWithPopup, signOut } from 'firebase/auth'
import { doc, getDoc, setDoc, collection, query, where, getDocs, serverTimestamp } from 'firebase/firestore'
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
          // Check if this email has been pre-seeded as superadmin
          const seedQuery = query(collection(db, 'superadmin_seeds'), where('email', '==', firebaseUser.email))
          const seedSnap = await getDocs(seedQuery)
          if (!seedSnap.empty) {
            const seedData = seedSnap.docs[0].data()
            const profile = {
              uid: firebaseUser.uid,
              email: firebaseUser.email,
              displayName: firebaseUser.displayName,
              photoURL: firebaseUser.photoURL,
              role: seedData.role,
              status: seedData.status,
              createdAt: serverTimestamp(),
            }
            await setDoc(docRef, profile)
            setUserProfile(profile)
          } else {
            setUserProfile(null)
          }
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
