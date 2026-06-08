/**
 * CUSTOMER PORTAL — FULL E-COMMERCE EXPERIENCE
 * ================================================
 * 
 * Complete shopping flow:
 * - Product Catalog with search, filter, categories
 * - Product Detail Page with add-to-cart, wishlist
 * - Shopping Cart with quantity controls
 * - Wishlist page
 * - Checkout flow
 * - Order history
 * - Support tickets
 * - Reviews & Refunds
 * 
 * Every action:
 * 1. Calls real API (not just /events)
 * 2. Persists to database
 * 3. Creates event
 * 4. Broadcasts via WebSocket
 */

import { useState, useEffect, useCallback } from 'react'
import { Routes, Route, Link, useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import {
  ShoppingBag, Search, Heart, ShoppingCart, Package, Zap, LogOut,
  Star, Plus, Minus, Eye, TrendingUp, Award, Percent, ArrowLeft,
  Trash2, CreditCard, MapPin, CheckCircle, AlertCircle, MessageSquare,
  RotateCcw, X, Headphones
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import api from '../../services/api'

/* ── Helper: Get Category Image ─────────── */
function getCategoryImage(category: string, productId: string): string {
  const cat = (category || '').toLowerCase()
  const seed = productId
  if (cat.includes('electron') || cat.includes('mobiles') || cat.includes('gaming') || cat.includes('comput'))
    return `https://source.unsplash.com/400x400/?electronics,gadget&sig=${seed}`
  if (cat.includes('beauty') || cat.includes('personal care'))
    return `https://source.unsplash.com/400x400/?cosmetics,skincare&sig=${seed}`
  if (cat.includes('fashion') || cat.includes('clothing') || cat.includes('bags'))
    return `https://source.unsplash.com/400x400/?fashion,clothing&sig=${seed}`
  if (cat.includes('footwear') || cat.includes('shoes'))
    return `https://source.unsplash.com/400x400/?shoes,sneakers&sig=${seed}`
  if (cat.includes('home') || cat.includes('furniture') || cat.includes('kitchen'))
    return `https://source.unsplash.com/400x400/?furniture,interior&sig=${seed}`
  if (cat.includes('book'))
    return `https://source.unsplash.com/400x400/?books,reading&sig=${seed}`
  if (cat.includes('sports') || cat.includes('fitness'))
    return `https://source.unsplash.com/400x400/?sports,fitness&sig=${seed}`
  return `https://source.unsplash.com/400x400/?product,shopping&sig=${seed}`
}

/* ── Toast Notification ──────────────────── */
function Toast({ message, type = 'success', onClose }: { message: string; type?: string; onClose: () => void }) {
  useEffect(() => { const t = setTimeout(onClose, 3000); return () => clearTimeout(t) }, [onClose])
  return (
    <motion.div
      initial={{ opacity: 0, y: 50, x: 20 }} animate={{ opacity: 1, y: 0, x: 0 }} exit={{ opacity: 0, y: 50 }}
      className={`fixed bottom-6 right-6 z-[100] px-5 py-3 rounded-xl text-sm font-medium shadow-2xl backdrop-blur-xl border ${
        type === 'success' ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300' : 'bg-red-500/20 border-red-500/30 text-red-300'
      }`}
    >
      <div className="flex items-center gap-2">
        {type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
        {message}
      </div>
    </motion.div>
  )
}

/* ── Product Card ─────────────────────── */
function ProductCard({ product, onView, onAddCart, onToggleWishlist, isWishlisted }: any) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const discountPercent = product.original_price && product.price < product.original_price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100) : 0
  const isBestseller = product.review_count > 100
  const isTrending = product.rating > 4.5 && product.review_count > 50
  const imageUrl = product.image_url || getCategoryImage(product.category, product.product_id)

  return (
    <motion.div
      className="group cursor-pointer relative overflow-hidden rounded-xl border border-slate-800/50 bg-slate-900/30 hover:bg-slate-900/50 transition-all duration-300"
      onClick={onView}
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -6, boxShadow: '0 20px 40px rgba(59, 130, 246, 0.15)' }}
    >
      {/* Badges */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
        {discountPercent > 0 && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-red-500 text-white">
            <Percent size={10} />{discountPercent}% OFF
          </span>
        )}
        {isBestseller && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500 text-white">
            <Award size={10} />Bestseller
          </span>
        )}
        {isTrending && (
          <span className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold bg-purple-500 text-white">
            <TrendingUp size={10} />Trending
          </span>
        )}
      </div>

      {/* Wishlist */}
      <motion.button
        className="absolute top-2 right-2 z-10 w-8 h-8 rounded-full flex items-center justify-center bg-slate-900/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={(e) => { e.stopPropagation(); onToggleWishlist() }}
        whileTap={{ scale: 0.9 }}
      >
        <Heart size={16} className={isWishlisted ? 'fill-red-500 text-red-500' : 'text-slate-400'} />
      </motion.button>

      {/* Image */}
      <div className="relative aspect-square overflow-hidden bg-slate-800/50">
        {!imageLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        <img src={imageUrl} alt={product.name}
          className={`w-full h-full object-cover transition-all duration-500 ${imageLoaded ? 'opacity-100 scale-100' : 'opacity-0 scale-95'} group-hover:scale-110`}
          loading="lazy"
          onLoad={() => setImageLoaded(true)}
          onError={(e: any) => { e.currentTarget.src = `https://placehold.co/400x400/1e293b/60a5fa?text=${encodeURIComponent(product.name?.substring(0, 15) || 'Product')}`; setImageLoaded(true) }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-end justify-center p-3 gap-2">
          <motion.button
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium"
            onClick={(e) => { e.stopPropagation(); onView() }}
            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          >
            <Eye size={14} />View
          </motion.button>
          <motion.button
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium"
            onClick={(e) => { e.stopPropagation(); onAddCart() }}
            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          >
            <Plus size={14} />Cart
          </motion.button>
        </div>
      </div>

      {/* Info */}
      <div className="p-3">
        <p className="text-[10px] text-blue-400 font-medium mb-1 uppercase tracking-wider truncate">{product.category}</p>
        <h3 className="text-sm font-semibold text-white mb-1.5 line-clamp-2 leading-tight min-h-[2.5rem]">{product.name}</h3>
        {product.brand && <p className="text-[10px] text-slate-500 mb-1.5 truncate">by {product.brand}</p>}
        <div className="flex items-center gap-1 mb-2">
          <div className="flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-amber-500/10">
            <Star size={10} className="text-amber-400 fill-amber-400" />
            <span className="text-[10px] font-semibold text-amber-400">{product.rating?.toFixed(1) || '4.0'}</span>
          </div>
          <span className="text-[10px] text-slate-500">({product.review_count?.toLocaleString() || '0'})</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <div className="flex items-baseline gap-2">
              <span className="text-base font-bold text-white">₹{product.price?.toLocaleString('en-IN')}</span>
              {product.original_price && product.price < product.original_price && (
                <span className="text-[10px] line-through text-slate-600">₹{product.original_price?.toLocaleString('en-IN')}</span>
              )}
            </div>
          </div>
          <motion.button
            className="w-9 h-9 rounded-lg flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white transition-colors"
            onClick={(e) => { e.stopPropagation(); onAddCart() }}
            whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
          >
            <Plus size={18} />
          </motion.button>
        </div>
      </div>
    </motion.div>
  )
}

/* ── Products Page ────────────────────── */
function ProductsPage() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [toast, setToast] = useState<{ msg: string; type: string } | null>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const searchTimerRef = useState<any>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['products', category, search],
    queryFn: () => api.get('/products', { params: { category: category || undefined, search: search || undefined } }).then(r => r.data),
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get('/products/categories').then(r => r.data),
  })

  // Wishlist state from server
  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => api.get('/cart/wishlist').then(r => r.data),
  })
  const wishlistedIds = new Set((wishlistData?.items || []).map((i: any) => i.product_id))

  const handleSearch = useCallback((val: string) => {
    setSearch(val)
    // Track search after debounce
    if (val.length > 2) {
      if (searchTimerRef[0]) clearTimeout(searchTimerRef[0])
      searchTimerRef[0] = setTimeout(() => {
        api.post(`/products/search?query=${encodeURIComponent(val)}`).catch(() => {})
      }, 800)
    }
  }, [])

  const addToCart = async (product: any) => {
    try {
      await api.post('/cart/add', { product_id: product.product_id, quantity: 1 })
      setToast({ msg: `${product.name} added to cart`, type: 'success' })
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Failed to add', type: 'error' })
    }
  }

  const toggleWishlist = async (product: any) => {
    try {
      if (wishlistedIds.has(product.product_id)) {
        await api.delete(`/cart/wishlist/remove/${product.product_id}`)
        setToast({ msg: `Removed from wishlist`, type: 'success' })
      } else {
        await api.post('/cart/wishlist/add', { product_id: product.product_id })
        setToast({ msg: `${product.name} added to wishlist`, type: 'success' })
      }
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Failed', type: 'error' })
    }
  }

  return (
    <div>
      <AnimatePresence>{toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}</AnimatePresence>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-2xl">
          <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
          <input className="w-full h-12 pl-12 pr-4 rounded-xl border border-slate-800 bg-slate-900/50 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="Search for products, brands, categories..."
            value={search} onChange={e => handleSearch(e.target.value)}
          />
        </div>
      </div>

      {/* Categories */}
      <div className="mb-6 -mx-6 px-6">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          <motion.button
            className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${!category ? 'bg-blue-600 text-white' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 hover:text-white'}`}
            onClick={() => setCategory('')} whileTap={{ scale: 0.95 }}
          >All Products</motion.button>
          {(categories || []).map((c: string) => (
            <motion.button key={c}
              className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${category === c ? 'bg-blue-600 text-white' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800 hover:text-white'}`}
              onClick={() => setCategory(c)} whileTap={{ scale: 0.95 }}
            >{c}</motion.button>
          ))}
        </div>
      </div>

      <div className="mb-4"><p className="text-sm text-slate-400">{isLoading ? 'Loading...' : `${data?.products?.length || 0} products found`}</p></div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="rounded-xl border border-slate-800/50 bg-slate-900/30 overflow-hidden animate-pulse">
              <div className="aspect-square bg-slate-800/50" />
              <div className="p-3 space-y-2"><div className="h-3 bg-slate-800/50 rounded w-1/3" /><div className="h-4 bg-slate-800/50 rounded w-full" /><div className="h-6 bg-slate-800/50 rounded w-1/2" /></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {(data?.products || []).map((p: any) => (
            <ProductCard key={p.product_id} product={p}
              isWishlisted={wishlistedIds.has(p.product_id)}
              onView={() => navigate(`/shop/product/${p.product_id}`)}
              onAddCart={() => addToCart(p)}
              onToggleWishlist={() => toggleWishlist(p)}
            />
          ))}
        </div>
      )}

      {!isLoading && (!data?.products || data.products.length === 0) && (
        <div className="text-center py-16"><Package size={48} className="mx-auto mb-4 text-slate-600" /><p className="text-slate-400">No products found</p></div>
      )}
    </div>
  )
}

/* ── Product Detail Page ──────────────── */
function ProductDetailPage() {
  const { productId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [toast, setToast] = useState<{ msg: string; type: string } | null>(null)
  const [qty, setQty] = useState(1)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => api.get(`/products/${productId}`).then(r => r.data),
    enabled: !!productId,
  })

  const imageUrl = product?.image_url || getCategoryImage(product?.category || '', product?.product_id || '')
  const discount = product?.original_price && product?.price < product?.original_price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100) : 0

  const addToCart = async () => {
    try {
      await api.post('/cart/add', { product_id: productId, quantity: qty })
      setToast({ msg: `${product.name} added to cart!`, type: 'success' })
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Error', type: 'error' })
    }
  }

  const addToWishlist = async () => {
    try {
      await api.post('/cart/wishlist/add', { product_id: productId })
      setToast({ msg: 'Added to wishlist!', type: 'success' })
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Error', type: 'error' })
    }
  }

  if (isLoading) return <div className="flex items-center justify-center py-20"><div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>
  if (!product) return <div className="text-center py-20 text-slate-400">Product not found</div>

  return (
    <div>
      <AnimatePresence>{toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}</AnimatePresence>

      <button onClick={() => navigate('/shop')} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6 transition">
        <ArrowLeft size={16} />Back to Products
      </button>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Image */}
        <motion.div className="rounded-2xl overflow-hidden border border-slate-800/50 bg-slate-900/30 aspect-square"
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
          <img src={imageUrl} alt={product.name} className="w-full h-full object-cover"
            onError={(e: any) => { e.currentTarget.src = `https://placehold.co/600x600/1e293b/60a5fa?text=${encodeURIComponent(product.name?.substring(0, 20) || 'Product')}` }}
          />
        </motion.div>

        {/* Details */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
          <div>
            <p className="text-sm text-blue-400 font-medium uppercase tracking-wider mb-2">{product.category}</p>
            <h1 className="text-3xl font-bold text-white mb-2">{product.name}</h1>
            {product.brand && <p className="text-slate-400">by {product.brand}</p>}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-500/10">
              <Star size={16} className="text-amber-400 fill-amber-400" />
              <span className="text-sm font-semibold text-amber-400">{product.rating?.toFixed(1)}</span>
            </div>
            <span className="text-sm text-slate-500">({product.review_count?.toLocaleString()} reviews)</span>
          </div>

          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-bold text-white">₹{product.price?.toLocaleString('en-IN')}</span>
            {product.original_price && product.price < product.original_price && (
              <>
                <span className="text-xl line-through text-slate-600">₹{product.original_price?.toLocaleString('en-IN')}</span>
                <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-sm font-bold">{discount}% OFF</span>
              </>
            )}
          </div>

          {product.description && <p className="text-slate-400 text-sm leading-relaxed">{product.description}</p>}

          <div className="flex items-center gap-2 text-sm">
            <span className={`px-3 py-1 rounded-full ${product.stock > 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
              {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
            </span>
          </div>

          {/* Quantity */}
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400">Quantity:</span>
            <div className="flex items-center gap-2 bg-slate-800/50 rounded-lg p-1">
              <button onClick={() => setQty(Math.max(1, qty - 1))} className="w-8 h-8 rounded flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition"><Minus size={16} /></button>
              <span className="w-8 text-center text-white font-medium">{qty}</span>
              <button onClick={() => setQty(Math.min(product.stock || 10, qty + 1))} className="w-8 h-8 rounded flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition"><Plus size={16} /></button>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <motion.button onClick={addToCart}
              className="flex-1 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center justify-center gap-2 transition"
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} disabled={product.stock <= 0}
            >
              <ShoppingCart size={20} />Add to Cart
            </motion.button>
            <motion.button onClick={addToWishlist}
              className="px-5 py-3.5 rounded-xl border border-slate-700 hover:border-red-500/50 text-slate-400 hover:text-red-400 transition"
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            >
              <Heart size={20} />
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

/* ── Cart Page ────────────────────────── */
function CartPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [toast, setToast] = useState<{ msg: string; type: string } | null>(null)
  const [checkingOut, setCheckingOut] = useState(false)

  const { data: cartData, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => api.get('/cart').then(r => r.data),
  })

  const removeItem = async (cartItemId: string) => {
    try {
      await api.delete(`/cart/remove/${cartItemId}`)
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setToast({ msg: 'Item removed', type: 'success' })
    } catch { setToast({ msg: 'Failed to remove', type: 'error' }) }
  }

  const updateQty = async (cartItemId: string, quantity: number) => {
    try {
      await api.put('/cart/update', { cart_item_id: cartItemId, quantity })
      queryClient.invalidateQueries({ queryKey: ['cart'] })
    } catch {}
  }

  const checkout = async () => {
    setCheckingOut(true)
    try {
      const { data } = await api.post('/cart/checkout', { payment_method: 'card' })
      setToast({ msg: `Order placed! ₹${data.total_amount?.toLocaleString('en-IN')}`, type: 'success' })
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      setTimeout(() => navigate('/shop/orders'), 2000)
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Checkout failed', type: 'error' })
    } finally { setCheckingOut(false) }
  }

  const items = cartData?.items || []

  return (
    <div>
      <AnimatePresence>{toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}</AnimatePresence>
      <h2 className="text-2xl font-bold text-white mb-6">Shopping Cart</h2>

      {isLoading ? (
        <div className="flex justify-center py-16"><div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>
      ) : items.length === 0 ? (
        <div className="text-center py-16">
          <ShoppingCart size={48} className="mx-auto mb-4 text-slate-600" />
          <p className="text-slate-400 mb-4">Your cart is empty</p>
          <Link to="/shop" className="text-blue-400 hover:text-blue-300 text-sm">Continue Shopping →</Link>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            {items.map((item: any, i: number) => (
              <motion.div key={item.cart_item_id}
                className="flex items-center gap-4 p-4 rounded-xl border border-slate-800/50 bg-slate-900/30"
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
              >
                <img src={item.product_image || getCategoryImage(item.category || '', item.product_id)}
                  alt={item.product_name} className="w-20 h-20 rounded-lg object-cover bg-slate-800"
                  onError={(e: any) => { e.currentTarget.src = `https://placehold.co/100x100/1e293b/60a5fa?text=Item` }}
                />
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-white truncate">{item.product_name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">{item.category} • {item.brand}</p>
                  <p className="text-base font-bold text-white mt-1">₹{item.product_price?.toLocaleString('en-IN')}</p>
                </div>
                <div className="flex items-center gap-2 bg-slate-800/50 rounded-lg p-1">
                  <button onClick={() => updateQty(item.cart_item_id, Math.max(1, item.quantity - 1))} className="w-7 h-7 rounded flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700"><Minus size={14} /></button>
                  <span className="w-6 text-center text-white text-sm font-medium">{item.quantity}</span>
                  <button onClick={() => updateQty(item.cart_item_id, item.quantity + 1)} className="w-7 h-7 rounded flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700"><Plus size={14} /></button>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-white">₹{item.item_total?.toLocaleString('en-IN')}</p>
                  <button onClick={() => removeItem(item.cart_item_id)} className="text-red-400 hover:text-red-300 mt-1"><Trash2 size={14} /></button>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Order Summary */}
          <motion.div className="p-6 rounded-xl border border-slate-800/50 bg-slate-900/30 h-fit sticky top-24"
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
            <h3 className="text-lg font-bold text-white mb-4">Order Summary</h3>
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm"><span className="text-slate-400">Subtotal ({items.length} items)</span><span className="text-white">₹{cartData?.subtotal?.toLocaleString('en-IN')}</span></div>
              <div className="flex justify-between text-sm"><span className="text-slate-400">Shipping</span><span className="text-emerald-400">FREE</span></div>
              <div className="h-px bg-slate-800" />
              <div className="flex justify-between font-bold"><span className="text-white">Total</span><span className="text-xl text-blue-400">₹{cartData?.total?.toLocaleString('en-IN')}</span></div>
            </div>
            <motion.button onClick={checkout} disabled={checkingOut}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50"
              whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            >
              {checkingOut ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <><CreditCard size={18} />Place Order</>}
            </motion.button>
          </motion.div>
        </div>
      )}
    </div>
  )
}

/* ── Wishlist Page ────────────────────── */
function WishlistPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [toast, setToast] = useState<{ msg: string; type: string } | null>(null)

  const { data: wishlistData, isLoading } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => api.get('/cart/wishlist').then(r => r.data),
  })

  const removeFromWishlist = async (productId: string) => {
    try {
      await api.delete(`/cart/wishlist/remove/${productId}`)
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
      setToast({ msg: 'Removed from wishlist', type: 'success' })
    } catch { setToast({ msg: 'Error', type: 'error' }) }
  }

  const moveToCart = async (item: any) => {
    try {
      await api.post('/cart/add', { product_id: item.product_id, quantity: 1 })
      await api.delete(`/cart/wishlist/remove/${item.product_id}`)
      queryClient.invalidateQueries({ queryKey: ['wishlist'] })
      queryClient.invalidateQueries({ queryKey: ['cart'] })
      setToast({ msg: `${item.product_name} moved to cart`, type: 'success' })
    } catch { setToast({ msg: 'Error', type: 'error' }) }
  }

  const items = wishlistData?.items || []

  return (
    <div>
      <AnimatePresence>{toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}</AnimatePresence>
      <h2 className="text-2xl font-bold text-white mb-6">My Wishlist ({items.length})</h2>
      {isLoading ? (
        <div className="flex justify-center py-16"><div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>
      ) : items.length === 0 ? (
        <div className="text-center py-16"><Heart size={48} className="mx-auto mb-4 text-slate-600" /><p className="text-slate-400">Your wishlist is empty</p></div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {items.map((item: any) => (
            <motion.div key={item.wishlist_item_id} className="rounded-xl border border-slate-800/50 bg-slate-900/30 overflow-hidden"
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="aspect-square overflow-hidden bg-slate-800/50 cursor-pointer" onClick={() => navigate(`/shop/product/${item.product_id}`)}>
                <img src={item.product_image || getCategoryImage(item.category || '', item.product_id)} alt={item.product_name} className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  onError={(e: any) => { e.currentTarget.src = `https://placehold.co/400x400/1e293b/60a5fa?text=Product` }}
                />
              </div>
              <div className="p-3">
                <h3 className="text-sm font-semibold text-white truncate">{item.product_name}</h3>
                <p className="text-base font-bold text-white mt-1">₹{item.product_price?.toLocaleString('en-IN')}</p>
                <div className="flex gap-2 mt-3">
                  <button onClick={() => moveToCart(item)} className="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium flex items-center justify-center gap-1"><ShoppingCart size={12} />Move to Cart</button>
                  <button onClick={() => removeFromWishlist(item.product_id)} className="px-3 py-2 rounded-lg border border-slate-700 text-red-400 hover:bg-red-500/10"><Trash2 size={12} /></button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ── Orders Page ──────────────────────── */
function OrdersPage() {
  const [toast, setToast] = useState<{ msg: string; type: string } | null>(null)
  const queryClient = useQueryClient()

  const { data: ordersData } = useQuery({
    queryKey: ['orders'],
    queryFn: () => api.get('/cart/orders').then(r => r.data),
  })

  const orders = ordersData?.orders || []

  const requestRefund = async (orderId: string) => {
    try {
      await api.post('/cart/refund', { order_id: orderId, reason: 'Customer requested refund' })
      setToast({ msg: 'Refund requested', type: 'success' })
      queryClient.invalidateQueries({ queryKey: ['orders'] })
    } catch (err: any) {
      setToast({ msg: err.response?.data?.detail || 'Error', type: 'error' })
    }
  }

  return (
    <div>
      <AnimatePresence>{toast && <Toast message={toast.msg} type={toast.type} onClose={() => setToast(null)} />}</AnimatePresence>
      <h2 className="text-2xl font-bold text-white mb-6">My Orders</h2>
      <div className="space-y-4">
        {orders.map((o: any, i: number) => (
          <motion.div key={o.order_id} className="p-5 rounded-xl border border-slate-800/50 bg-slate-900/30"
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center"><Package size={20} className="text-blue-400" /></div>
                <div>
                  <p className="text-sm font-semibold text-white">Order #{o.order_id.slice(0, 12)}</p>
                  <p className="text-xs text-slate-500">{new Date(o.order_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-emerald-400">₹{o.total_amount?.toLocaleString('en-IN')}</p>
                <span className={`inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-medium ${
                  o.status === 'delivered' ? 'bg-emerald-500/10 text-emerald-400' :
                  o.status === 'cancelled' || o.status === 'refund_requested' ? 'bg-red-500/10 text-red-400' :
                  'bg-blue-500/10 text-blue-400'
                }`}>{o.status}</span>
              </div>
            </div>
            {o.items && o.items.length > 0 && (
              <div className="flex gap-2 mb-3 overflow-x-auto">
                {o.items.map((item: any) => (
                  <div key={item.product_id} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/30 flex-shrink-0">
                    <span className="text-xs text-slate-300">{item.product_name}</span>
                    <span className="text-[10px] text-slate-500">×{item.quantity}</span>
                  </div>
                ))}
              </div>
            )}
            {o.status === 'confirmed' && (
              <button onClick={() => requestRefund(o.order_id)} className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300">
                <RotateCcw size={12} />Request Refund
              </button>
            )}
          </motion.div>
        ))}
        {orders.length === 0 && (
          <div className="text-center py-16"><Package size={48} className="mx-auto mb-4 text-slate-600" /><p className="text-slate-400">No orders yet</p>
            <Link to="/shop" className="inline-block mt-4 text-blue-400 hover:text-blue-300 text-sm">Start shopping →</Link>
          </div>
        )}
      </div>
    </div>
  )
}

/* ── Support Page ─────────────────────── */
function SupportPage() {
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const submit = async () => {
    if (!message.trim()) return
    await api.post('/support', { subject: subject || 'Support Request', message })
    setMessage('')
    setSubject('')
    setSubmitted(true)
    setTimeout(() => setSubmitted(false), 3000)
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold text-white mb-6">Customer Support</h2>
      <div className="p-6 rounded-xl border border-slate-800/50 bg-slate-900/30">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">Subject</label>
          <input className="w-full px-4 py-3 rounded-lg border border-slate-800 bg-slate-900/50 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            placeholder="Brief description of your issue" value={subject} onChange={e => setSubject(e.target.value)} />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">How can we help?</label>
          <textarea className="w-full min-h-[150px] px-4 py-3 rounded-lg border border-slate-800 bg-slate-900/50 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 transition-colors resize-none"
            placeholder="Describe your issue or question..." value={message} onChange={e => setMessage(e.target.value)} />
        </div>
        <motion.button className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors disabled:opacity-50"
          onClick={submit} whileTap={{ scale: 0.98 }} disabled={!message.trim()}>
          <MessageSquare size={16} className="inline mr-2" />Submit Ticket
        </motion.button>
        <AnimatePresence>
          {submitted && (
            <motion.div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm"
              initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
              ✓ Your ticket has been submitted! We'll get back to you soon.
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

/* ── Customer Portal Layout ───────────── */
export default function CustomerPortal() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const { data: cartData } = useQuery({
    queryKey: ['cart'],
    queryFn: () => api.get('/cart').then(r => r.data),
    refetchInterval: 30000,
  })

  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: () => api.get('/cart/wishlist').then(r => r.data),
    refetchInterval: 30000,
  })

  const cartCount = cartData?.item_count || 0
  const wishlistCount = wishlistData?.count || 0

  const handleLogout = async () => {
    try { await api.post('/auth/logout') } catch {}
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-[#0B0F14]">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-800">
        <div className="max-w-[1920px] mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/shop" className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-600">
              <Zap size={18} color="white" />
            </div>
            <span className="text-white font-bold text-lg">OmniPulse Store</span>
          </Link>

          <div className="flex items-center gap-6">
            <Link to="/shop" className="text-sm font-medium text-slate-400 hover:text-white transition">Products</Link>
            <Link to="/shop/cart" className="relative text-sm font-medium text-slate-400 hover:text-white transition flex items-center gap-1">
              <ShoppingCart size={16} />Cart
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-3 w-5 h-5 rounded-full bg-blue-600 text-[10px] font-bold text-white flex items-center justify-center">{cartCount}</span>
              )}
            </Link>
            <Link to="/shop/wishlist" className="relative text-sm font-medium text-slate-400 hover:text-white transition flex items-center gap-1">
              <Heart size={16} />Wishlist
              {wishlistCount > 0 && (
                <span className="absolute -top-2 -right-3 w-5 h-5 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">{wishlistCount}</span>
              )}
            </Link>
            <Link to="/shop/orders" className="text-sm font-medium text-slate-400 hover:text-white transition">Orders</Link>
            <Link to="/shop/support" className="text-sm font-medium text-slate-400 hover:text-white transition">Support</Link>

            <div className="h-6 w-px bg-slate-700" />

            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-white">{user?.name}</span>
              <motion.button onClick={handleLogout} className="text-slate-400 hover:text-red-400 transition" whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
                <LogOut size={18} />
              </motion.button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-[1920px] mx-auto px-6 py-8">
        <Routes>
          <Route index element={<ProductsPage />} />
          <Route path="product/:productId" element={<ProductDetailPage />} />
          <Route path="cart" element={<CartPage />} />
          <Route path="wishlist" element={<WishlistPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="support" element={<SupportPage />} />
        </Routes>
      </main>
    </div>
  )
}
