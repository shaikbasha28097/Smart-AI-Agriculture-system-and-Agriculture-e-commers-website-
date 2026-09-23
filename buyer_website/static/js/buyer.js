// Buyer E-Mart Main JavaScript Logic

let currentCategory = null;
let currentSearch = '';
let currentOnlyOrganic = false;
let productsCache = [];

document.addEventListener('DOMContentLoaded', () => {
    checkBuyerAuth();
    loadProducts();
    loadCart();
    checkUrlReferral();
});

function checkBuyerAuth() {
    const userName = localStorage.getItem('user_name') || 'Ramesh Kumar';
    const navName = document.getElementById('buyerNavName');
    const profName = document.getElementById('buyerProfileName');
    if (navName) navName.innerText = userName.split(' ')[0] || 'My Orders';
    if (profName) profName.innerText = userName;
}

function handleLogout() {
    fetch('/api/auth/logout').finally(() => {
        localStorage.clear();
        window.location.href = '/buyer';
    });
}

// Check if redirected from Farmer AI Disease Diagnostic
function checkUrlReferral() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product_id');
    const source = urlParams.get('source');

    if (productId) {
        const banner = document.getElementById('aiReferralBanner');
        if (banner) banner.classList.remove('hidden');

        // Automatically add to cart and open drawer for seamless 1-click purchase
        setTimeout(() => {
            addToCart(productId, 1, true);
        }, 600);
    }
}

// ==============================================================================
// 1. PRODUCTS CATALOG & FILTERING
// ==============================================================================
async function loadProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    let url = '/api/products?';
    if (currentCategory) url += `category_id=${currentCategory}&`;
    if (currentSearch) url += `search=${encodeURIComponent(currentSearch)}&`;
    if (currentOnlyOrganic) url += `is_organic=1&`;

    try {
        const res = await fetch(url);
        const json = await res.json();
        
        if (json.success) {
            productsCache = json.products;
            grid.innerHTML = '';

            if (json.products.length === 0) {
                grid.innerHTML = '<div class="col-span-4 text-center py-16 text-slate-400 text-sm">No products found matching the criteria.</div>';
                return;
            }

            json.products.forEach(p => {
                const card = document.createElement('div');
                card.id = `product-${p.id}`;
                card.className = 'bg-white rounded-3xl p-4 border border-slate-200 shadow-sm hover:shadow-lg hover:-translate-y-1 transition duration-300 flex flex-col justify-between';
                
                card.innerHTML = `
                    <div>
                        <div class="relative rounded-2xl overflow-hidden mb-3 aspect-square bg-slate-100">
                            <img src="${p.image_url}" class="w-full h-full object-cover" alt="${p.name}">
                            ${p.is_organic ? '<span class="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-full bg-emerald-600 text-white text-[10px] font-bold shadow"><i class="fa-solid fa-leaf mr-1"></i> Organic</span>' : ''}
                            ${p.remedy_for_disease ? `<span class="absolute bottom-2.5 left-2.5 right-2.5 px-2 py-1 rounded-lg bg-slate-900/80 backdrop-blur text-amber-300 text-[10px] font-semibold text-center truncate"><i class="fa-solid fa-wand-magic-sparkles mr-1"></i> AI Remedy: ${p.remedy_for_disease}</span>` : ''}
                        </div>

                        <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">${p.category_name || 'Agri Product'}</span>
                        <h4 class="text-sm font-bold text-slate-900 line-clamp-2 mt-0.5 mb-1">${p.name}</h4>
                        <p class="text-[11px] text-slate-500 line-clamp-2 mb-3">${p.short_description || p.description}</p>
                    </div>

                    <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
                        <div>
                            <span class="text-xs text-slate-400 font-semibold block">Price</span>
                            <div class="text-base font-black text-orange-600">₹${p.price.toFixed(2)} <span class="text-[11px] text-slate-500 font-normal">/${p.unit}</span></div>
                        </div>
                        <button onclick="addToCart(${p.id}, 1, true)" class="px-3.5 py-2 rounded-xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-xs shadow-md shadow-orange-600/20 transition flex items-center gap-1.5">
                            <i class="fa-solid fa-cart-plus"></i> <span>Add</span>
                        </button>
                    </div>
                `;
                grid.appendChild(card);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

function filterCategory(catId) {
    currentCategory = catId;
    document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    loadProducts();
}

function handleSearch(query) {
    currentSearch = query.trim();
    loadProducts();
}

function handleOrganicToggle(checked) {
    currentOnlyOrganic = checked;
    loadProducts();
}


// ==============================================================================
// 2. SHOPPING CART MANAGEMENT
// ==============================================================================
function toggleCartDrawer() {
    const drawer = document.getElementById('cartDrawer');
    if (drawer) drawer.classList.toggle('hidden');
}

async function addToCart(productId, quantity = 1, openDrawer = false) {
    try {
        const userId = localStorage.getItem('user_id') || 3;
        const res = await fetch('/api/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, product_id: productId, quantity: quantity })
        });
        const json = await res.json();
        
        if (json.success) {
            loadCart();
            if (openDrawer) {
                const drawer = document.getElementById('cartDrawer');
                if (drawer) drawer.classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error(err);
    }
}

async function removeCartItem(itemId) {
    try {
        const userId = localStorage.getItem('user_id') || 3;
        await fetch(`/api/cart?item_id=${itemId}&user_id=${userId}`, { method: 'DELETE' });
        loadCart();
    } catch (err) {
        console.error(err);
    }
}

async function loadCart() {
    try {
        const userId = localStorage.getItem('user_id') || 3;
        const res = await fetch(`/api/cart?user_id=${userId}`);
        const json = await res.json();
        
        if (json.success) {
            const list = document.getElementById('cartItemsList');
            const badge = document.getElementById('cartBadge');
            const subtotal = document.getElementById('cartSubtotal');
            const delivery = document.getElementById('cartDelivery');
            const total = document.getElementById('cartTotal');
            const chkAmt = document.getElementById('chkOrderAmount');
            
            if (badge) badge.innerText = json.summary.item_count;
            if (subtotal) subtotal.innerText = `₹${json.summary.subtotal.toFixed(2)}`;
            if (delivery) delivery.innerText = json.summary.delivery > 0 ? `₹${json.summary.delivery.toFixed(2)}` : 'FREE';
            if (total) total.innerText = `₹${json.summary.total.toFixed(2)}`;
            if (chkAmt) chkAmt.innerText = `₹${json.summary.total.toFixed(2)}`;

            if (list) {
                list.innerHTML = '';
                if (json.items.length === 0) {
                    list.innerHTML = '<div class="text-center py-12 text-slate-400 text-xs">Your cart is empty. Explore our catalog!</div>';
                    return;
                }

                json.items.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'flex items-center gap-3 p-3 bg-slate-50 rounded-2xl border border-slate-200';
                    itemDiv.innerHTML = `
                        <img src="${item.image_url}" class="w-14 h-14 rounded-xl object-cover border border-slate-200" alt="${item.name}">
                        <div class="flex-1 min-w-0">
                            <h5 class="text-xs font-bold text-slate-900 truncate">${item.name}</h5>
                            <div class="text-[11px] text-slate-500 font-semibold">Qty: ${item.quantity} ${item.unit}</div>
                            <div class="text-xs font-extrabold text-orange-600">₹${(item.price * item.quantity).toFixed(2)}</div>
                        </div>
                        <button onclick="removeCartItem(${item.cart_item_id})" class="text-slate-400 hover:text-rose-600 text-xs p-2">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    `;
                    list.appendChild(itemDiv);
                });
            }
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// 3. INSTANT CHECKOUT & ORDER PLACEMENT
// ==============================================================================
function openCheckoutModal() {
    toggleCartDrawer();
    const modal = document.getElementById('checkoutModal');
    if (modal) modal.classList.remove('hidden');
}

function closeCheckoutModal() {
    const modal = document.getElementById('checkoutModal');
    if (modal) modal.classList.add('hidden');
}

async function handleCheckoutSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btnPlaceOrder');
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Order...';
    btn.disabled = true;

    const payload = {
        user_id: localStorage.getItem('user_id') || 3,
        shipping_address: document.getElementById('chkAddress').value,
        phone: document.getElementById('chkPhone').value,
        payment_method: document.getElementById('chkPaymentMethod').value
    };

    try {
        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        
        if (json.success) {
            alert(`🎉 ${json.message}\nOrder Number: ${json.order_number}\nTracking ID: ${json.tracking_number}`);
            closeCheckoutModal();
            loadCart();
            window.location.href = '/buyer/dashboard';
        } else {
            alert(json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error placing order.');
    } finally {
        btn.innerHTML = 'Confirm & Place Order';
        btn.disabled = false;
    }
}


// ==============================================================================
// 4. BUYER ORDERS & TRACKING DASHBOARD
// ==============================================================================
async function loadBuyerOrders() {
    const list = document.getElementById('buyerOrdersList');
    if (!list) return;

    try {
        const userId = localStorage.getItem('user_id') || 3;
        const res = await fetch(`/api/orders?user_id=${userId}`);
        const json = await res.json();
        
        if (json.success) {
            list.innerHTML = '';
            if (json.orders.length === 0) {
                list.innerHTML = '<div class="text-center py-10 text-slate-400 text-sm">You haven\'t placed any orders yet. <a href="/buyer" class="text-orange-600 font-bold hover:underline">Start Shopping</a></div>';
                return;
            }

            json.orders.forEach(o => {
                const card = document.createElement('div');
                card.className = 'bg-slate-50 rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4';
                
                // Status stage calculation for timeline
                const statusMap = { 'placed': 1, 'processing': 2, 'shipped': 3, 'out_for_delivery': 4, 'delivered': 5 };
                const currentStep = statusMap[o.order_status] || 1;

                card.innerHTML = `
                    <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-200 text-xs">
                        <div>
                            <span class="text-slate-400 font-semibold">Order Number:</span>
                            <strong class="text-slate-900 ml-1">#${o.order_number}</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 font-semibold">Tracking ID:</span>
                            <strong class="text-emerald-700 ml-1">${o.tracking_number || 'TRK-AGRI-1002'}</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 font-semibold">Order Total:</span>
                            <strong class="text-orange-600 text-sm ml-1">₹${o.total_amount.toFixed(2)}</strong>
                        </div>
                    </div>

                    <!-- Live Delivery Tracking Timeline -->
                    <div class="py-2">
                        <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-3">Live Delivery Status</span>
                        <div class="grid grid-cols-5 gap-2 text-center text-[10px] font-bold">
                            <div class="${currentStep >= 1 ? 'text-emerald-700' : 'text-slate-400'}">
                                <div class="w-7 h-7 rounded-full ${currentStep >= 1 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'} flex items-center justify-center mx-auto mb-1">
                                    <i class="fa-solid fa-receipt"></i>
                                </div>
                                <span>Placed</span>
                            </div>
                            <div class="${currentStep >= 2 ? 'text-emerald-700' : 'text-slate-400'}">
                                <div class="w-7 h-7 rounded-full ${currentStep >= 2 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'} flex items-center justify-center mx-auto mb-1">
                                    <i class="fa-solid fa-box-open"></i>
                                </div>
                                <span>Processing</span>
                            </div>
                            <div class="${currentStep >= 3 ? 'text-emerald-700' : 'text-slate-400'}">
                                <div class="w-7 h-7 rounded-full ${currentStep >= 3 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'} flex items-center justify-center mx-auto mb-1">
                                    <i class="fa-solid fa-truck"></i>
                                </div>
                                <span>Shipped</span>
                            </div>
                            <div class="${currentStep >= 4 ? 'text-emerald-700' : 'text-slate-400'}">
                                <div class="w-7 h-7 rounded-full ${currentStep >= 4 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'} flex items-center justify-center mx-auto mb-1">
                                    <i class="fa-solid fa-person-biking"></i>
                                </div>
                                <span>Out for Delivery</span>
                            </div>
                            <div class="${currentStep >= 5 ? 'text-emerald-700' : 'text-slate-400'}">
                                <div class="w-7 h-7 rounded-full ${currentStep >= 5 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-500'} flex items-center justify-center mx-auto mb-1">
                                    <i class="fa-solid fa-circle-check"></i>
                                </div>
                                <span>Delivered</span>
                            </div>
                        </div>
                    </div>

                    <div class="pt-3 border-t border-slate-200 text-xs text-slate-500 flex items-center justify-between">
                        <span>Delivery Address: <strong class="text-slate-800">${o.shipping_address}</strong></span>
                        <span class="font-semibold text-emerald-700">Payment: ${o.payment_method.toUpperCase()} (${o.payment_status.toUpperCase()})</span>
                    </div>
                `;
                list.appendChild(card);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

