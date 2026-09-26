// Buyer E-Mart Main JavaScript Logic

let currentCategory = null;
let currentSearch = '';
let currentOnlyOrganic = false;
let productsCache = [];
let selectedFruitVegFile = null;
let mandiFiltersCache = null;

document.addEventListener('DOMContentLoaded', () => {
    checkBuyerAuth();
    loadProducts();
    loadCart();
    checkUrlReferral();
    loadMandiFilters();
    loadMandiPrices();
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

// Top Tab Switcher (Catalog vs Chemical Scanner vs Mandi Rates)
function switchBuyerTab(tabId) {
    document.querySelectorAll('.buyer-top-tab').forEach(btn => {
        btn.classList.remove('active', 'bg-white', 'text-orange-700', 'shadow-md');
        btn.classList.add('bg-white/20', 'text-white');
    });
    document.querySelectorAll('.buyer-tab-view').forEach(view => view.classList.add('hidden'));

    const activeBtn = document.getElementById(`topTab-${tabId}`);
    const activeView = document.getElementById(`buyer-tab-${tabId}`);

    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-white', 'text-orange-700', 'shadow-md');
        activeBtn.classList.remove('bg-white/20', 'text-white');
    }
    if (activeView) activeView.classList.remove('hidden');

    if (tabId === 'mandi') {
        loadMandiPrices();
    }
}

// Check if redirected from Farmer AI Disease Diagnostic or scan referrals
function checkUrlReferral() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('product_id');
    const source = urlParams.get('source');
    const tab = urlParams.get('tab');

    if (tab === 'scanner') {
        switchBuyerTab('scanner');
    } else if (tab === 'mandi') {
        switchBuyerTab('mandi');
    }

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
// 1. PRODUCTS CATALOG & FILTERING (8 Divided Services)
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
                card.className = 'bg-white rounded-3xl p-4 border border-slate-200 shadow-sm hover:shadow-lg hover:-translate-y-1 transition duration-300 flex flex-col justify-between relative';
                
                const isAgriProduce = [1, 2, 3, 4].includes(p.category_id);
                const isFarmingTool = (p.category_id == 8 || (p.category_name && p.category_name.toLowerCase().includes('tool')));
                const safeImg = p.image_url || 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500';

                // Only non-tool categories display unit of measure (e.g. /KG, /Litre, /Pack). Farming tools do NOT display unit of measure.
                const unitHtml = isFarmingTool ? '' : ` <span class="text-[11px] text-slate-500 font-normal">/${p.unit || 'KG'}</span>`;

                card.innerHTML = `
                    <div>
                        <div onclick="openProductDetail(${p.id})" class="relative rounded-2xl overflow-hidden mb-3 aspect-square bg-slate-100 cursor-pointer group">
                            <img src="${safeImg}" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500';" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" alt="${p.name}">
                            ${p.is_organic ? '<span class="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-full bg-emerald-600 text-white text-[10px] font-bold shadow"><i class="fa-solid fa-leaf mr-1"></i> 100% Organic</span>' : ''}
                            ${isAgriProduce ? '<span class="absolute top-2.5 right-2.5 px-2 py-0.5 rounded-full bg-slate-950/80 backdrop-blur text-emerald-300 text-[10px] font-bold border border-emerald-500/40 shadow"><i class="fa-solid fa-shield-halved mr-1 text-emerald-400"></i> AI Verified (&le; 30% Chem)</span>' : ''}
                            ${p.remedy_for_disease ? `<span class="absolute bottom-2.5 left-2.5 right-2.5 px-2 py-1 rounded-lg bg-slate-900/80 backdrop-blur text-amber-300 text-[10px] font-semibold text-center truncate"><i class="fa-solid fa-wand-magic-sparkles mr-1"></i> AI Remedy: ${p.remedy_for_disease}</span>` : ''}
                            <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs font-bold gap-1">
                                <i class="fa-solid fa-magnifying-glass-plus"></i> View Details
                            </div>
                        </div>

                        <div class="flex items-center justify-between gap-1 mb-0.5">
                            <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">${p.category_name || 'Agri Product'}</span>
                            <span class="text-[10px] font-semibold text-emerald-600"><i class="fa-solid fa-circle-check"></i> Quality Inspected</span>
                        </div>
                        <h4 onclick="openProductDetail(${p.id})" class="text-sm font-bold text-slate-900 line-clamp-2 mt-0.5 mb-1 cursor-pointer hover:text-orange-600 transition">${p.name}</h4>
                        <div class="text-[10px] text-slate-400 mb-1 flex items-center gap-1">
                            <i class="fa-solid fa-store text-blue-500"></i> ${p.seller_name || 'Agri Seller'}
                        </div>
                        <p class="text-[11px] text-slate-500 line-clamp-2 mb-3">${p.short_description || p.description}</p>
                    </div>

                    <div class="pt-3 border-t border-slate-100 flex flex-col gap-2.5">
                        <div class="flex items-center justify-between">
                            <span class="text-xs text-slate-400 font-semibold">Price</span>
                            <div class="text-base font-black text-orange-600">₹${(Number(p.price) || 0).toFixed(2)}${unitHtml}</div>
                        </div>
                        <div class="grid grid-cols-2 gap-2">
                            <button onclick="addToCart(${p.id}, 1, true)" class="w-full py-2 px-2 rounded-xl bg-orange-100 hover:bg-orange-200 text-orange-800 font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-sm">
                                <i class="fa-solid fa-cart-plus"></i> <span>Add to Cart</span>
                            </button>
                            <button onclick="buyNow(${p.id})" class="w-full py-2 px-2 rounded-xl bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white font-bold text-xs shadow-md shadow-orange-600/20 transition flex items-center justify-center gap-1.5">
                                <i class="fa-solid fa-bolt"></i> <span>Buy Now</span>
                            </button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });

            // Check if redirected from Seller with a specific product_id to highlight
            const urlParams = new URLSearchParams(window.location.search);
            const targetProdId = urlParams.get('product_id') || (window.location.hash.startsWith('#product-') ? window.location.hash.replace('#product-', '') : null);
            if (targetProdId) {
                setTimeout(() => {
                    const targetEl = document.getElementById(`product-${targetProdId}`);
                    if (targetEl) {
                        targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        targetEl.classList.add('ring-4', 'ring-emerald-500', 'ring-offset-4', 'shadow-2xl', 'scale-[1.03]');
                        
                        // Show banner toast
                        showHighlightBanner(targetProdId);
                    }
                }, 400);
            }
        }
    } catch (err) {
        console.error(err);
    }
}

function showHighlightBanner(prodId) {
    const existing = document.getElementById('newProductHighlightBanner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'newProductHighlightBanner';
    banner.className = 'fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-slate-900 text-white px-6 py-3.5 rounded-2xl shadow-2xl border-2 border-emerald-500 flex items-center gap-3 animate-bounce';
    banner.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-lg">
            <i class="fa-solid fa-circle-check"></i>
        </div>
        <div>
            <h5 class="text-xs font-black text-emerald-400 uppercase tracking-wider">AI Quality Approved Product Listed!</h5>
            <p class="text-xs text-slate-300">Product passed AI Whole-Lot Inspection (&le; 30% Chemical) and is live on E-Mart.</p>
        </div>
        <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white text-sm ml-2">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
    document.body.appendChild(banner);
    setTimeout(() => { if (banner) banner.remove(); }, 6000);
}


function filterCategory(catId) {
    currentCategory = catId;
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active', 'bg-orange-600', 'text-white', 'shadow-sm');
        btn.classList.add('bg-slate-100', 'text-slate-700');
    });
    const targetId = catId ? `catBtn-${catId}` : 'catBtn-all';
    const activeBtn = document.getElementById(targetId);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-orange-600', 'text-white', 'shadow-sm');
        activeBtn.classList.remove('bg-slate-100', 'text-slate-700');
    }
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
// 2. AI FRUIT & VEGETABLE CHEMICAL, PESTICIDE & TDS QUALITY SCANNER
// ==============================================================================
function previewFruitVegImage(input) {
    if (input.files && input.files[0]) {
        selectedFruitVegFile = input.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('scanDropzoneContent').classList.add('hidden');
            const container = document.getElementById('scanImagePreviewContainer');
            container.classList.remove('hidden');
            document.getElementById('scanPreviewImg').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function loadSampleScan(commodity, sampleType) {
    const select = document.getElementById('scanCommoditySelect');
    const container = document.getElementById('scanImagePreviewContainer');
    const dropzoneContent = document.getElementById('scanDropzoneContent');
    const previewImg = document.getElementById('scanPreviewImg');

    dropzoneContent.classList.add('hidden');
    container.classList.remove('hidden');

    const sampleImages = {
        'tomato_organic': { val: 'Tomato', img: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500' },
        'apple_chemical': { val: 'Apple', img: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500' },
        'mango_chemical': { val: 'Mango', img: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=500' },
        'banana_organic': { val: 'Banana', img: 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=500' }
    };

    const key = `${commodity}_${sampleType}`;
    const preset = sampleImages[key] || sampleImages['tomato_organic'];

    if (select) select.value = preset.val;
    if (previewImg) previewImg.src = preset.img;
    selectedFruitVegFile = null;

    // Trigger instant diagnosis
    runScanWithParams(preset.val, sampleType);
}

async function handleFruitVegScanSubmit(e) {
    e.preventDefault();
    const commodity = document.getElementById('scanCommoditySelect').value;
    runScanWithParams(commodity, 'organic');
}

async function runScanWithParams(commodity, sampleType) {
    const btn = document.getElementById('btnRunChemicalScan');
    const origText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Chemical Residue & TDS...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('commodity', commodity);
    formData.append('sample_type', sampleType);
    if (selectedFruitVegFile) {
        formData.append('image', selectedFruitVegFile);
    }

    try {
        const res = await fetch('/api/ai/scan-fruit-veg', {
            method: 'POST',
            body: formData
        });
        const json = await res.json();
        if (json.success) {
            renderFruitVegScanResult(json.data);
        } else {
            alert('Error scanning item: ' + json.message);
        }
    } catch (err) {
        console.error(err);
        alert('Food safety scanner server error.');
    } finally {
        btn.innerHTML = origText;
        btn.disabled = false;
    }
}

function renderFruitVegScanResult(data) {
    document.getElementById('scanPlaceholder').classList.add('hidden');
    document.getElementById('scanActiveResult').classList.remove('hidden');

    document.getElementById('scanCommodityBadge').innerText = `COMMODITY: ${data.commodity.toUpperCase()}`;
    document.getElementById('scanPurityTitle').innerText = data.status;
    document.getElementById('scanConfidence').innerText = `${data.confidence}%`;

    document.getElementById('scanChemicalPpm').innerText = data.chemical_level;
    document.getElementById('scanChemicalSub').innerText = data.chemical_status;
    document.getElementById('scanChemicalSub').className = data.is_organic ? 'text-[10px] font-bold text-emerald-600' : 'text-[10px] font-bold text-rose-600';

    document.getElementById('scanTdsScore').innerText = `${data.tds_score} mg/L`;
    document.getElementById('scanRipeningMode').innerText = data.ripening_mode;
    document.getElementById('scanFreshnessPct').innerText = `${data.freshness_pct}%`;
    document.getElementById('scanShelfLife').innerText = `${data.shelf_life_days} Shelf`;

    document.getElementById('scanPesticideDesc').innerText = data.pesticide_detected;
    document.getElementById('scanWaxDesc').innerText = data.wax_coating;
    document.getElementById('scanDetoxGuide').innerText = data.detox_protocol;

    if (data.recommended_organic_product) {
        document.getElementById('scanOrganicProdName').innerText = data.recommended_organic_product.name;
        const buyBtn = document.getElementById('btnBuyOrganicProduce');
        buyBtn.href = data.recommended_organic_product.buy_url;
    }
}


// ==============================================================================
// 3. LIVE APMC MANDI MARKET PRICES (Official Agmarknet / e-NAM Gov Feed)
// ==============================================================================
async function loadMandiFilters() {
    try {
        const res = await fetch('/api/market-prices/filters');
        const json = await res.json();
        if (json.success) {
            mandiFiltersCache = json.filters;
        }
    } catch (e) {
        console.error(e);
    }
}

function handleMandiStateChange(state) {
    const distSelect = document.getElementById('mandiDistrictFilter');
    if (!distSelect) return;

    distSelect.innerHTML = '<option value="all">All Districts</option>';

    const stateDistMap = {
        'Telangana': ['Hyderabad', 'Warangal', 'Rangareddy', 'Nizamabad'],
        'Andhra Pradesh': ['Guntur', 'Vijayawada', 'Kurnool', 'Chittoor'],
        'Maharashtra': ['Nashik', 'Pune', 'Nagpur', 'Mumbai'],
        'Karnataka': ['Bengaluru', 'Kolar', 'Mysuru'],
        'Tamil Nadu': ['Chennai', 'Coimbatore'],
        'Gujarat': ['Ahmedabad', 'Rajkot'],
        'Uttar Pradesh': ['Agra', 'Varanasi'],
        'Punjab': ['Ludhiana']
    };

    const districts = stateDistMap[state] || [];
    districts.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.innerText = d;
        distSelect.appendChild(opt);
    });

    loadMandiPrices();
}

async function loadMandiPrices() {
    const tableBody = document.getElementById('mandiPricesTableBody');
    const countBadge = document.getElementById('mandiTotalCount');
    if (!tableBody) return;

    const state = document.getElementById('mandiStateFilter')?.value || 'all';
    const district = document.getElementById('mandiDistrictFilter')?.value || 'all';
    const commodity = document.getElementById('mandiCommodityFilter')?.value || 'all';
    const search = document.getElementById('mandiSearchInput')?.value || '';

    let url = `/api/market-prices?state=${state}&district=${district}&commodity=${commodity}&search=${encodeURIComponent(search)}`;

    try {
        const res = await fetch(url);
        const json = await res.json();
        
        if (json.success) {
            if (countBadge) countBadge.innerText = `Showing ${json.total} Market Yards (Live 2026)`;
            tableBody.innerHTML = '';

            if (json.prices.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" class="text-center py-10 text-slate-400">No APMC Mandi price records found matching your filters.</td></tr>';
                return;
            }

            json.prices.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';

                let trendBadge = `<span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-bold">Stable</span>`;
                if (row.trend === 'up') {
                    trendBadge = `<span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold"><i class="fa-solid fa-arrow-trend-up mr-1"></i> ${row.trend_pct}</span>`;
                } else if (row.trend === 'down') {
                    trendBadge = `<span class="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-bold"><i class="fa-solid fa-arrow-trend-down mr-1"></i> ${row.trend_pct}</span>`;
                }

                tr.innerHTML = `
                    <td class="py-3.5 px-4">
                        <strong class="text-slate-900 block font-bold">${row.commodity}</strong>
                        <span class="text-[10px] text-slate-500">${row.variety}</span>
                    </td>
                    <td class="py-3.5 px-4 font-semibold text-slate-700">
                        ${row.state}
                        <span class="block text-[10px] text-slate-400">${row.district}</span>
                    </td>
                    <td class="py-3.5 px-4 text-slate-600 font-medium">
                        ${row.market_yard}
                    </td>
                    <td class="py-3.5 px-4 text-right font-bold text-slate-700">
                        ₹${row.min_price}
                    </td>
                    <td class="py-3.5 px-4 text-right font-bold text-slate-700">
                        ₹${row.max_price}
                    </td>
                    <td class="py-3.5 px-4 text-right">
                        <strong class="text-orange-600 text-sm font-black">₹${row.price_per_kg.toFixed(2)}</strong>
                        <span class="block text-[10px] text-slate-400">₹${row.modal_price} / Q</span>
                    </td>
                    <td class="py-3.5 px-4 text-center">
                        ${trendBadge}
                    </td>
                    <td class="py-3.5 px-4 text-[10px] font-semibold text-emerald-700">
                        <i class="fa-solid fa-circle-check mr-1"></i> ${row.source}
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error(e);
    }
}


// ==============================================================================
// 4. SHOPPING CART MANAGEMENT
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
                    const isTool = (item.category_id == 8 || (item.category_name && item.category_name.toLowerCase().includes('tool')) || item.unit === 'Piece' || item.unit === 'Unit' || !item.unit);
                    const qtyDisplay = isTool ? `Qty: ${item.quantity}` : `Qty: ${item.quantity} ${item.unit}`;

                    itemDiv.innerHTML = `
                        <img src="${item.image_url}" class="w-14 h-14 rounded-xl object-cover border border-slate-200" alt="${item.name}">
                        <div class="flex-1 min-w-0">
                            <h5 class="text-xs font-bold text-slate-900 truncate">${item.name}</h5>
                            <div class="text-[11px] text-slate-500 font-semibold">${qtyDisplay}</div>
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
// 5. INSTANT CHECKOUT & BUY NOW
// ==============================================================================
async function buyNow(productId) {
    try {
        await addToCart(productId, 1, false);
        openCheckoutModal();
    } catch (e) {
        console.error('Error during Buy Now action:', e);
    }
}

function openCheckoutModal() {
    const drawer = document.getElementById('cartDrawer');
    if (drawer) drawer.classList.add('hidden');
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
// 6. BUYER ORDERS & TRACKING DASHBOARD
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

// ==============================================================================
// 7. PRODUCT DETAIL QUICK-VIEW MODAL
// ==============================================================================
function openProductDetail(productId) {
    const p = productsCache.find(item => item.id == productId);
    if (!p) return;

    const modal = document.getElementById('productDetailModal');
    if (!modal) return;

    const img = document.getElementById('modalDetailImage');
    const title = document.getElementById('modalDetailTitle');
    const cat = document.getElementById('modalDetailCategory');
    const stock = document.getElementById('modalDetailStock');
    const seller = document.getElementById('modalDetailSeller');
    const price = document.getElementById('modalDetailPrice');
    const unit = document.getElementById('modalDetailUnit');
    const desc = document.getElementById('modalDetailDesc');
    const badges = document.getElementById('modalDetailBadges');
    const addBtn = document.getElementById('modalDetailAddToCartBtn');
    const buyBtn = document.getElementById('modalDetailBuyNowBtn');

    const safeImg = p.image_url || 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500';
    const isFarmingTool = (p.category_id == 8 || (p.category_name && p.category_name.toLowerCase().includes('tool')));

    if (img) {
        img.src = safeImg;
        img.onerror = function() { this.src = 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500'; };
    }
    if (title) title.innerText = p.name;
    if (cat) cat.innerText = p.category_name || 'Agri Product';
    if (stock) stock.innerText = isFarmingTool ? `${p.stock_quantity || 100} Available` : `${p.stock_quantity || 100} ${p.unit || 'KG'} Available`;
    if (seller) seller.innerText = p.seller_name || 'Verified Agribusiness Seller';
    if (price) price.innerText = `₹${(Number(p.price) || 0).toFixed(2)}`;
    if (unit) unit.innerText = isFarmingTool ? '' : `/${p.unit || 'KG'}`;
    if (desc) desc.innerText = p.description || p.short_description || 'Naturally grown, certified safe agricultural product.';

    if (badges) {
        badges.innerHTML = '';
        if (p.is_organic) {
            badges.innerHTML += '<span class="px-2.5 py-1 rounded-full bg-emerald-600 text-white text-[10px] font-bold shadow"><i class="fa-solid fa-leaf mr-1"></i> 100% Organic</span>';
        }
        if ([1, 2, 3, 4].includes(p.category_id)) {
            badges.innerHTML += '<span class="px-2.5 py-1 rounded-full bg-slate-900/90 text-emerald-400 text-[10px] font-bold border border-emerald-500/40 shadow"><i class="fa-solid fa-shield-halved mr-1"></i> AI Verified Quality (≤ 30% Chem)</span>';
        }
    }

    if (addBtn) {
        addBtn.onclick = () => {
            addToCart(p.id, 1, true);
            closeProductDetailModal();
        };
    }
    if (buyBtn) {
        buyBtn.onclick = () => {
            closeProductDetailModal();
            buyNow(p.id);
        };
    }

    modal.classList.remove('hidden');
}

function closeProductDetailModal() {
    const modal = document.getElementById('productDetailModal');
    if (modal) modal.classList.add('hidden');
}
