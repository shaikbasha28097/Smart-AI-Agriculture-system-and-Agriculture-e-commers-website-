// Seller Agribusiness Main JavaScript Logic

document.addEventListener('DOMContentLoaded', () => {
    checkSellerAuth();
    loadSellerFarmerHarvests();
    loadSellerInventory();
    loadSellerOrders();
    initSellerCharts();
});

function openAuthModal(mode) {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.classList.remove('hidden');
        toggleAuthMode(mode);
    }
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) modal.classList.add('hidden');
}

function toggleAuthMode(mode) {
    const loginForm = document.getElementById('loginForm');
    const regForm = document.getElementById('registerForm');
    const title = document.getElementById('modalTitle');
    
    if (mode === 'register') {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        if (title) title.innerText = 'Register Agribusiness';
    } else {
        regForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
        if (title) title.innerText = 'Seller Login';
    }
}

async function handleAuthLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role: 'seller' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/seller/dashboard';
        } else {
            alert(data.message || 'Login failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Error connecting to server.');
    }
}

async function handleAuthRegister(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const city = document.getElementById('regCity').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, city, password, role: 'seller' })
        });
        const data = await res.json();
        if (data.success) {
            localStorage.setItem('user_id', data.user.id);
            localStorage.setItem('user_role', data.user.role);
            localStorage.setItem('user_name', data.user.name);
            window.location.href = '/seller/dashboard';
        } else {
            alert(data.message || 'Registration failed.');
        }
    } catch (err) {
        console.error(err);
        alert('Error creating account.');
    }
}

function quickDemoLogin() {
    localStorage.setItem('user_id', '2');
    localStorage.setItem('user_role', 'seller');
    localStorage.setItem('user_name', 'ABC Agro Traders (Seller)');
    window.location.href = '/seller/dashboard';
}

function handleLogout() {
    fetch('/api/auth/logout').finally(() => {
        localStorage.clear();
        window.location.href = '/seller';
    });
}

function checkSellerAuth() {
    const userName = localStorage.getItem('user_name') || 'ABC Agro Traders';
    const navName = document.getElementById('navSellerName');
    const dashName = document.getElementById('dashSellerName');
    if (navName) navName.innerText = userName;
    if (dashName) dashName.innerText = userName;
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    
    const activeBtn = document.getElementById(`tabBtn-${tabId}`);
    const activeContent = document.getElementById(`tab-${tabId}`);
    
    if (activeBtn) activeBtn.classList.add('active');
    if (activeContent) activeContent.classList.remove('hidden');
}


// ==============================================================================
// 1. AVAILABLE FARMER CROPS FEED (Farmer -> Seller Workflow)
// ==============================================================================
async function loadSellerFarmerHarvests() {
    const feed = document.getElementById('farmerHarvestsFeed');
    if (!feed) return;

    try {
        const res = await fetch('/api/seller/farmer-harvests');
        const json = await res.json();
        
        if (json.success) {
            feed.innerHTML = '';
            let availableCount = 0;

            json.harvests.forEach(h => {
                const isPurchased = (h.status === 'purchased_by_seller');
                if (!isPurchased) availableCount++;

                const card = document.createElement('div');
                card.className = `p-5 rounded-2xl border ${isPurchased ? 'bg-slate-900/60 border-slate-800' : 'bg-slate-900 border-slate-700 shadow-md'} flex flex-col justify-between`;
                card.innerHTML = `
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold ${isPurchased ? 'bg-slate-800 text-slate-400' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}">
                                ${isPurchased ? '✓ Acquired / In Inventory' : '⚡ Available for Sourcing'}
                            </span>
                            <span class="text-xs text-slate-400 font-semibold">${h.harvest_date}</span>
                        </div>

                        <h4 class="text-base font-bold text-white mb-1">${h.crop_name} (${h.variety || 'Standard'})</h4>
                        
                        <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-1.5 my-3 text-xs">
                            <div class="flex justify-between"><span class="text-slate-400">Grower / Farmer:</span> <strong class="text-white">${h.farmer_name}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Location:</span> <strong class="text-white">${h.location}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Total Lot Quantity:</span> <strong class="text-emerald-400">${h.quantity} ${h.unit}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Expected Farm-Gate:</span> <strong class="text-blue-300 font-bold">₹${h.expected_price_per_unit} / ${h.unit}</strong></div>
                            <div class="flex justify-between"><span class="text-slate-400">Quality Standard:</span> <strong class="text-amber-300">${h.quality}</strong></div>
                        </div>

                        <p class="text-xs text-slate-400 mb-4">${h.description || 'Farm-gate direct harvest.'}</p>
                    </div>

                    <div>
                        ${isPurchased ? `
                            <button disabled class="w-full py-2.5 rounded-xl bg-slate-800 text-slate-500 font-bold text-xs cursor-not-allowed">
                                Already Acquired
                            </button>
                        ` : `
                            <button onclick="acquireFarmerHarvest(${h.id}, '${h.crop_name}', ${h.quantity}, '${h.unit}')" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition flex items-center justify-center gap-2">
                                <i class="fa-solid fa-handshake"></i> 1-Click Purchase / Acquire Lot
                            </button>
                        `}
                    </div>
                `;
                feed.appendChild(card);
            });

            const statCrops = document.getElementById('statFarmerCrops');
            if (statCrops) statCrops.innerText = `${availableCount} Lots Available`;
        }
    } catch (err) {
        console.error(err);
    }
}

async function acquireFarmerHarvest(harvestId, cropName, quantity, unit) {
    if (!confirm(`Confirm acquisition of ${quantity} ${unit} ${cropName} from farmer?`)) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/buy-harvest/${harvestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seller_id: sellerId })
        });
        const json = await res.json();
        
        if (json.success) {
            alert('🎉 ' + json.message);
            loadSellerFarmerHarvests();
            loadSellerInventory();
        } else {
            alert(json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error acquiring crop.');
    }
}


// ==============================================================================
// 2. INVENTORY & PUBLISH TO BUYER E-MART
// ==============================================================================
function openPublishProductModal() {
    const modal = document.getElementById('publishProductModal');
    if (modal) modal.classList.remove('hidden');
}

function closePublishProductModal() {
    const modal = document.getElementById('publishProductModal');
    if (modal) modal.classList.add('hidden');
}

async function handlePublishProductSubmit(e) {
    e.preventDefault();
    const payload = {
        seller_id: localStorage.getItem('user_id') || 2,
        name: document.getElementById('prodName').value,
        category_id: document.getElementById('prodCategory').value,
        price: document.getElementById('prodPrice').value,
        stock_quantity: document.getElementById('prodStock').value,
        unit: document.getElementById('prodUnit').value,
        is_organic: document.getElementById('prodIsOrganic').checked ? 1 : 0,
        short_description: document.getElementById('prodDesc').value,
        description: document.getElementById('prodDesc').value
    };

    try {
        const res = await fetch('/api/seller/create-product', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
            alert('🎉 ' + json.message);
            closePublishProductModal();
            loadSellerInventory();
            switchTab('inventory');
        } else {
            alert(json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Error publishing product.');
    }
}

async function loadSellerInventory() {
    const grid = document.getElementById('inventoryGrid');
    if (!grid) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/inventory?seller_id=${sellerId}`);
        const json = await res.json();
        
        if (json.success) {
            grid.innerHTML = '';
            json.products.forEach(p => {
                const card = document.createElement('div');
                card.className = 'p-4 rounded-2xl bg-slate-900 border border-slate-700/80 shadow-sm flex flex-col justify-between';
                card.innerHTML = `
                    <div>
                        <img src="${p.image_url}" class="w-full h-32 object-cover rounded-xl mb-3 border border-slate-800" alt="${p.name}">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[10px] uppercase font-bold text-blue-400">Stock: ${p.stock_quantity} ${p.unit}</span>
                            ${p.is_organic ? '<span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-bold">Organic</span>' : ''}
                        </div>
                        <h5 class="text-sm font-bold text-white line-clamp-1">${p.name}</h5>
                        <div class="text-base font-extrabold text-emerald-400 mt-1">₹${p.price.toFixed(2)} <span class="text-xs text-slate-400">/${p.unit}</span></div>
                    </div>
                    <div class="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                        <a href="/buyer?product_id=${p.id}#product-${p.id}" target="_blank" class="text-amber-400 hover:underline">
                            View on E-Mart &rarr;
                        </a>
                    </div>
                `;
                grid.appendChild(card);
            });

            const statInv = document.getElementById('statInventoryCount');
            if (statInv) statInv.innerText = `${json.products.length} Products`;
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// 3. BUYER ORDERS & DELIVERY FULFILLMENT
// ==============================================================================
async function loadSellerOrders() {
    const tbody = document.getElementById('sellerOrdersTableBody');
    if (!tbody) return;

    try {
        const sellerId = localStorage.getItem('user_id') || 2;
        const res = await fetch(`/api/seller/orders?seller_id=${sellerId}`);
        const json = await res.json();
        
        if (json.success) {
            tbody.innerHTML = '';
            if (json.orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="p-6 text-center text-slate-500">No buyer orders received yet.</td></tr>';
                return;
            }

            json.orders.forEach(o => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition';
                tr.innerHTML = `
                    <td class="p-3.5 font-bold text-white">#${o.order_number}</td>
                    <td class="p-3.5">${o.buyer_name || 'Buyer Customer'}</td>
                    <td class="p-3.5 font-semibold text-white">${o.product_name} (${o.quantity} units)</td>
                    <td class="p-3.5 text-emerald-400 font-bold">₹${o.total_price.toFixed(2)}</td>
                    <td class="p-3.5">
                        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold ${
                            o.order_status === 'delivered' ? 'bg-emerald-500/20 text-emerald-400' :
                            o.order_status === 'shipped' ? 'bg-blue-500/20 text-blue-400' : 'bg-amber-500/20 text-amber-400'
                        }">
                            ${o.order_status.replace('_', ' ').toUpperCase()}
                        </span>
                    </td>
                    <td class="p-3.5">
                        <select onchange="updateOrderStatus(${o.id}, this.value)" class="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white">
                            <option value="placed" ${o.order_status === 'placed' ? 'selected' : ''}>Placed</option>
                            <option value="processing" ${o.order_status === 'processing' ? 'selected' : ''}>Processing</option>
                            <option value="shipped" ${o.order_status === 'shipped' ? 'selected' : ''}>Shipped</option>
                            <option value="out_for_delivery" ${o.order_status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
                            <option value="delivered" ${o.order_status === 'delivered' ? 'selected' : ''}>Delivered</option>
                        </select>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (err) {
        console.error(err);
    }
}

async function updateOrderStatus(orderId, status) {
    try {
        const res = await fetch(`/api/seller/orders/${orderId}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status })
        });
        const json = await res.json();
        if (json.success) {
            alert('Order fulfillment status updated!');
            loadSellerOrders();
        }
    } catch (err) {
        console.error(err);
    }
}


// ==============================================================================
// 4. ANALYTICS CHARTS (Chart.js)
// ==============================================================================
function initSellerCharts() {
    const sourcingCtx = document.getElementById('sourcingChart');
    if (sourcingCtx) {
        new Chart(sourcingCtx, {
            type: 'bar',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep (Current)'],
                datasets: [{
                    label: 'Sourced Harvest (Quintals)',
                    data: [120, 190, 240, 310, 480],
                    backgroundColor: '#3b82f6',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
                }
            }
        });
    }

    const catCtx = document.getElementById('categoryChart');
    if (catCtx) {
        new Chart(catCtx, {
            type: 'doughnut',
            data: {
                labels: ['Fresh Farm Produce', 'Organic Fertilizers', 'Chemical Fungicides', 'Hybrid Seeds'],
                datasets: [{
                    data: [82500, 31000, 24700, 16000],
                    backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: '#94a3b8' } } }
            }
        });
    }
}

